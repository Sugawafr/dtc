from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from io import BytesIO
import cgi, hashlib, json, os, re, secrets, sqlite3, time, uuid

ROOT = Path(__file__).resolve().parent
DB = ROOT / "dtc.db"
UPLOADS = ROOT / "uploads"
PORT = int(os.environ.get("DTC_PORT", "4180"))

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def password_hash(value, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", value.encode(), salt, 310000)
    return f"{salt.hex()}:{digest.hex()}"

def password_ok(value, stored):
    salt, digest = stored.split(":", 1)
    return secrets.compare_digest(password_hash(value, bytes.fromhex(salt)).split(":", 1)[1], digest)

def setup():
    UPLOADS.mkdir(exist_ok=True)
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, is_admin INTEGER NOT NULL DEFAULT 0, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, type TEXT NOT NULL CHECK(type IN ('dtc','incident')), code TEXT NOT NULL, description TEXT NOT NULL, model TEXT NOT NULL DEFAULT '', vehicle_year TEXT NOT NULL DEFAULT '', system TEXT NOT NULL DEFAULT '', solution TEXT NOT NULL, checklist TEXT NOT NULL DEFAULT '', created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL, UNIQUE(type, code));
        CREATE TABLE IF NOT EXISTS favorites (user_id INTEGER NOT NULL, record_id INTEGER NOT NULL, PRIMARY KEY(user_id,record_id));
        CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, record_id INTEGER NOT NULL, user_id INTEGER, action TEXT NOT NULL, details TEXT NOT NULL DEFAULT '', created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS attachments (id INTEGER PRIMARY KEY, record_id INTEGER NOT NULL, path TEXT NOT NULL, filename TEXT NOT NULL, created_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS vag_updates (id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, module TEXT NOT NULL, vehicle TEXT NOT NULL, reference TEXT NOT NULL DEFAULT '', created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS vag_attachments (id INTEGER PRIMARY KEY, vag_update_id INTEGER NOT NULL, path TEXT NOT NULL, filename TEXT NOT NULL, created_at INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_records_type_system ON records(type, system);
        CREATE INDEX IF NOT EXISTS idx_history_record_time ON history(record_id, created_at DESC);
        """)
        if not c.execute("SELECT 1 FROM vag_updates LIMIT 1").fetchone():
            now=int(time.time())
            c.executemany("INSERT INTO vag_updates(code,module,vehicle,reference,created_at,updated_at) VALUES(?,?,?,?,?,?)", [("1F69CE","SOBDM","Explorer","",now,now),("37D6","PCM","Connect","26-2076",now,now),("2K4R","GWM","Connect","26-2336",now,now)])

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, data, status=200, cookie=None):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if cookie: self.send_header("Set-Cookie", cookie)
        self.end_headers(); self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length or 0))

    def user(self):
        cookie = self.headers.get("Cookie", "")
        token = next((part.split("=", 1)[1] for part in cookie.split("; ") if part.startswith("dtc_session=")), None)
        if not token: return None
        with db() as c:
            return c.execute("SELECT users.id,users.email,users.is_admin FROM sessions JOIN users ON users.id=sessions.user_id WHERE token=? AND expires_at>?", (token, int(time.time()))).fetchone()

    def require_user(self):
        user = self.user()
        if not user: self.send_json({"error":"Connexion requise."}, 401)
        return user

    def require_admin(self):
        user = self.require_user()
        if user and not user["is_admin"]:
            self.send_json({"error":"Accès administrateur requis."}, 403); return None
        return user

    def add_history(self, record_id, user_id, action, details=""):
        with db() as c: c.execute("INSERT INTO history(record_id,user_id,action,details,created_at) VALUES(?,?,?,?,?)", (record_id, user_id, action, details, int(time.time())))

    def record_payload(self, row, user_id=None):
        item = dict(row)
        item["checklist"] = [line for line in item["checklist"].split("\n") if line.strip()]
        with db() as c:
            item["attachments"] = [dict(x) for x in c.execute("SELECT id,path,filename FROM attachments WHERE record_id=? ORDER BY id DESC", (item["id"],))]
            item["favorite"] = bool(user_id and c.execute("SELECT 1 FROM favorites WHERE user_id=? AND record_id=?", (user_id, item["id"])).fetchone())
        return item

    def get_records(self):
        user = self.user(); uid = user["id"] if user else None
        with db() as c: rows = c.execute("SELECT * FROM records ORDER BY type,code COLLATE NOCASE").fetchall()
        self.send_json({"records":[self.record_payload(row, uid) for row in rows], "user": dict(user) if user else None})

    def vag_payload(self, row):
        item = dict(row)
        with db() as c:
            item["attachments"] = [dict(x) for x in c.execute("SELECT id,path,filename FROM vag_attachments WHERE vag_update_id=? ORDER BY id DESC", (item["id"],))]
        return item

    def get_vag_updates(self):
        with db() as c: rows = c.execute("SELECT * FROM vag_updates ORDER BY code COLLATE NOCASE").fetchall()
        self.send_json({"updates":[self.vag_payload(row) for row in rows], "user":dict(self.user()) if self.user() else None})

    def save_vag_update(self, data, update_id=None):
        code = str(data.get("code", "")).strip().upper(); module = str(data.get("module", "")).strip(); vehicle = str(data.get("vehicle", "")).strip(); reference = str(data.get("reference", "")).strip()
        if not code or not module or not vehicle: raise ValueError("Code, module et véhicule sont obligatoires.")
        now = int(time.time())
        with db() as c:
            if update_id:
                c.execute("UPDATE vag_updates SET code=?,module=?,vehicle=?,reference=?,updated_at=? WHERE id=?", (code,module,vehicle,reference,now,update_id))
                if not c.total_changes: raise ValueError("Code VAG introuvable.")
            else:
                cur=c.execute("INSERT INTO vag_updates(code,module,vehicle,reference,created_at,updated_at) VALUES(?,?,?,?,?,?)", (code,module,vehicle,reference,now,now)); update_id=cur.lastrowid
            return self.vag_payload(c.execute("SELECT * FROM vag_updates WHERE id=?", (update_id,)).fetchone())

    def save_record(self, data, user_id, record_id=None):
        kind = data.get("type", "dtc")
        if kind not in ("dtc", "incident"): raise ValueError("Type de référence invalide.")
        code = str(data.get("code", "")).strip()
        if kind == "dtc": code = code.upper()
        description = str(data.get("description", "")).strip()
        solution = str(data.get("solution", "")).strip()
        if not code or not description or not solution: raise ValueError("Code, description et solution sont obligatoires.")
        values = (kind, code, description, str(data.get("model", "")).strip(), str(data.get("vehicle_year", "")).strip(), str(data.get("system", "")).strip(), solution, "\n".join(x.strip() for x in data.get("checklist", []) if x.strip()))
        now = int(time.time())
        with db() as c:
            if record_id:
                c.execute("UPDATE records SET type=?,code=?,description=?,model=?,vehicle_year=?,system=?,solution=?,checklist=?,updated_at=? WHERE id=?", (*values, now, record_id))
                if not c.total_changes: raise ValueError("Référence introuvable.")
                action = "Modification"
            else:
                cur = c.execute("INSERT INTO records(type,code,description,model,vehicle_year,system,solution,checklist,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (*values, now, now))
                record_id = cur.lastrowid; action = "Création"
        self.add_history(record_id, user_id, action, solution)
        with db() as c: return self.record_payload(c.execute("SELECT * FROM records WHERE id=?", (record_id,)).fetchone(), user_id)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/records": self.get_records()
        elif path == "/api/vag-updates": self.get_vag_updates()
        elif path == "/api/me":
            user = self.user(); self.send_json(dict(user) if user else None)
        elif path == "/api/stats":
            with db() as c:
                systems = [dict(r) for r in c.execute("SELECT COALESCE(NULLIF(system,''),'Non classé') label,COUNT(*) total FROM records GROUP BY label ORDER BY total DESC")]
                models = [dict(r) for r in c.execute("SELECT model label,COUNT(*) total FROM records WHERE model<>'' GROUP BY model ORDER BY total DESC LIMIT 8")]
            self.send_json({"systems":systems,"models":models})
        elif (match := re.fullmatch(r"/api/records/(\d+)/history", path)):
            user = self.require_user()
            if user:
                with db() as c: rows = c.execute("SELECT history.action,history.details,history.created_at,COALESCE(users.email,'Système') email FROM history LEFT JOIN users ON users.id=history.user_id WHERE record_id=? ORDER BY history.created_at DESC", (match[1],)).fetchall()
                self.send_json([dict(r) for r in rows])
        elif path == "/api/admin/backup":
            if self.require_admin():
                self.send_response(200); self.send_header("Content-Type", "application/octet-stream"); self.send_header("Content-Disposition", "attachment; filename=dtc-backup.db"); self.end_headers(); self.wfile.write(DB.read_bytes())
        else: super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path in ("/api/register", "/api/login"):
                data = self.read_json(); email = data.get("email", "").strip().lower(); password = data.get("password", "")
                if "@" not in email or len(password) < 8: raise ValueError("Utilisez un e-mail valide et un mot de passe d’au moins 8 caractères.")
                with db() as c:
                    if path.endswith("register"):
                        admin = 0 if c.execute("SELECT 1 FROM users LIMIT 1").fetchone() else 1
                        cur = c.execute("INSERT INTO users(email,password,is_admin,created_at) VALUES(?,?,?,?)", (email,password_hash(password),admin,int(time.time())))
                        uid, is_admin = cur.lastrowid, bool(admin)
                    else:
                        found = c.execute("SELECT id,password,is_admin FROM users WHERE email=?", (email,)).fetchone()
                        if not found or not password_ok(password, found["password"]): raise ValueError("E-mail ou mot de passe incorrect.")
                        uid, is_admin = found["id"], bool(found["is_admin"])
                    token = secrets.token_urlsafe(32); c.execute("INSERT INTO sessions(token,user_id,expires_at) VALUES(?,?,?)", (token,uid,int(time.time())+2592000))
                self.send_json({"id":uid,"email":email,"is_admin":is_admin}, cookie=f"dtc_session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000")
            elif path == "/api/logout": self.send_json({"ok":True}, cookie="dtc_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0")
            elif path == "/api/seed":
                data = self.read_json().get("records", [])
                with db() as c: empty = not c.execute("SELECT 1 FROM records LIMIT 1").fetchone()
                if empty:
                    for item in data[:100]:
                        try: self.save_record(item, None)
                        except (ValueError, sqlite3.IntegrityError): pass
                self.get_records()
            elif path == "/api/records":
                self.send_json(self.save_record(self.read_json(), None), 201)
            elif path == "/api/vag-updates":
                if self.require_admin(): self.send_json(self.save_vag_update(self.read_json()), 201)
            elif (match := re.fullmatch(r"/api/records/(\d+)/favorite", path)):
                user = self.require_user()
                if user:
                    with db() as c:
                        exists = c.execute("SELECT 1 FROM favorites WHERE user_id=? AND record_id=?", (user["id"],match[1])).fetchone()
                        if exists: c.execute("DELETE FROM favorites WHERE user_id=? AND record_id=?", (user["id"],match[1])); favorite=False
                        else: c.execute("INSERT INTO favorites(user_id,record_id) VALUES(?,?)", (user["id"],match[1])); favorite=True
                    self.send_json({"favorite":favorite})
            elif (match := re.fullmatch(r"/api/records/(\d+)/attachment", path)):
                user = self.require_admin()
                if user:
                    form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD":"POST","CONTENT_TYPE":self.headers.get("Content-Type","")})
                    item=form["file"]; content=item.file.read(8*1024*1024+1)
                    if len(content)>8*1024*1024: raise ValueError("Fichier limité à 8 Mo.")
                    name=Path(item.filename or "document").name; stored=f"{uuid.uuid4().hex}_{name}"; (UPLOADS/stored).write_bytes(content)
                    with db() as c: c.execute("INSERT INTO attachments(record_id,path,filename,created_at) VALUES(?,?,?,?)", (match[1],f"/uploads/{stored}",name,int(time.time())))
                    self.add_history(match[1],user["id"],"Pièce jointe",name); self.send_json({"ok":True})
            elif (match := re.fullmatch(r"/api/vag-updates/(\d+)/attachment", path)):
                user = self.require_admin()
                if user:
                    form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={"REQUEST_METHOD":"POST","CONTENT_TYPE":self.headers.get("Content-Type","")})
                    item=form["file"]; content=item.file.read(8*1024*1024+1)
                    if len(content)>8*1024*1024: raise ValueError("Fichier limité à 8 Mo.")
                    name=Path(item.filename or "document").name; stored=f"vag_{uuid.uuid4().hex}_{name}"; (UPLOADS/stored).write_bytes(content)
                    with db() as c: c.execute("INSERT INTO vag_attachments(vag_update_id,path,filename,created_at) VALUES(?,?,?,?)", (match[1],f"/uploads/{stored}",name,int(time.time())))
                    self.send_json({"ok":True})
            else: self.send_error(404)
        except sqlite3.IntegrityError: self.send_json({"error":"Cette référence existe déjà."},400)
        except Exception as error: self.send_json({"error":str(error)},400)

    def do_PUT(self):
        path=urlparse(self.path).path; match = re.fullmatch(r"/api/records/(\d+)", path); vag_match = re.fullmatch(r"/api/vag-updates/(\d+)", path); user=self.require_admin()
        if user and match:
            try: self.send_json(self.save_record(self.read_json(),user["id"],int(match[1])))
            except Exception as error: self.send_json({"error":str(error)},400)
        elif user and vag_match:
            try: self.send_json(self.save_vag_update(self.read_json(),int(vag_match[1])))
            except Exception as error: self.send_json({"error":str(error)},400)

    def do_DELETE(self):
        path=urlparse(self.path).path; match = re.fullmatch(r"/api/records/(\d+)", path); vag_match = re.fullmatch(r"/api/vag-updates/(\d+)", path); user=self.require_admin()
        if user and match:
            with db() as c: c.execute("DELETE FROM records WHERE id=?",(match[1],)); c.execute("DELETE FROM favorites WHERE record_id=?",(match[1],)); c.execute("DELETE FROM attachments WHERE record_id=?",(match[1],)); c.execute("DELETE FROM history WHERE record_id=?",(match[1],))
            self.send_json({"ok":True})
        elif user and vag_match:
            with db() as c: c.execute("DELETE FROM vag_attachments WHERE vag_update_id=?",(vag_match[1],)); c.execute("DELETE FROM vag_updates WHERE id=?",(vag_match[1],))
            self.send_json({"ok":True})

if __name__ == "__main__":
    os.chdir(ROOT); setup(); print(f"Site disponible sur http://0.0.0.0:{PORT}"); ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
