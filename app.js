let records = [
  ["dtc","P040D","Capteur A température gaz échappement, circuit haut","Remplacer réf. 2457155 (Ranger)"],
  ["dtc","P20BA","Performance commande additif A (P20BA–P204F)","Remplacer réf. 2345643 (résistance réservoir ADB)"],
  ["dtc","P0171","Mélange trop pauvre, rangée 1","Vérifier carburant (éthanol), contrôle PCM"],
  ["dtc","P0420","Catalyseur inefficace","Remplacer catalyseur"],
  ["dtc","P0092","Régulateur pression carburant cassé (rampe)","Remplacer réf. 2345718 (Transit 2.0 EcoBlue)"],
  ["dtc","P0087","Pression carburant basse (Transit Custom 2020)","Contrôler pompe immergée, réf. 2511769"],
  ["dtc","P0299","Sous-pression turbo","Contrôler admission, MAP, fuite, filtre à air, turbo"],
  ["dtc","P2000","Efficacité NOx rangée 1","Remplacer FAP ou réf. 2452571"],
  ["dtc","P244C","Température catalyseur trop basse pendant régénération","Contrôler injecteur FAP"],
  ["dtc","P2598","Turbo compresseur A défaut","Remplacement turbo (Ranger)"],
  ["dtc","P0402","Débit EGR excessif","Remplacement du capteur EGR seul — DTC P0402, finis 2782797"],
  ["dtc","P041D","Tension élevée sonde température EGR B","Remplacer réf. 1862037"],
  ["dtc","P2002","Efficacité FAP","DPF à remplacer + contrôler l’injecteur AdBlue (Ranger)"],
  ["dtc","P20EE","Ensemble SCR inefficace","Sonde NOx + contrôler l’injecteur AdBlue (Ranger)"],
  ["dtc","P049B","Focus 1.5 Diesel, MIL + joint EGR bloqué","Remplacer joint réf. HG9Q-9V473-AB (finis 2532932)"],
  ["dtc","P061B","Performance calcul couple (PCM)","Mise à jour étalonnage PCM (KX7A-14C204-APJ ou +)"],
  ["dtc","P00BD","Débitmètre / EGR / filtre à air défectueux","Contrôler filtre, MAF, conduits EGR"],
  ["dtc","P0141","Chauffage sonde O2 B1S2 défaillant","Remplacer sonde réf. 2540139"],
  ["dtc","P1102 / P006A","Moteur 1.5 EcoBlue","Contrôler calage distribution + chaîne arbre à cames, guide plastique cassé"],
  ["dtc","P2096","Convertisseur catalytique inefficace","Remplacer réf. 2382295 + sonde réf. 2492696"],
  ["dtc","P0A05 / P0A78 / P0A90","Défaut moteur électrique","Remplacer réf. 2454272"],
  ["dtc","P20E8","Débit SCR trop lent","Remplacer pompe SCR"],
  ["dtc","P228C542E","Coupure moteur en roulant 2.0 TDCi","Remplacer pompe HP"],
  ["dtc","C0051","Capteur angle volant (ESP/ABS)","Remplacer réf. 2369132"],
  ["dtc","U0428","Données non valides capteur angle braquage","Vérifier module HCM"],
  ["dtc","B1041528A / B10416408","Défaut HCM (IPMA)","Ré-étalonnage dynamique module IPMA"],
  ["dtc","C1001 / B115E","Caméra visibilité (APIM / BCM)","Remplacer caméra réf. 2212988"],
  ["dtc","P02CA","Anomalie transmission","Pompe à huile remplacée, réf. 2665127"],
  ["dtc","B1578:78:2F:IPMA","Caméra 360 ne fonctionne pas après remplacement d’un rétro","Contrôler que la caméra du rétro a la bonne référence"],
  ["dtc","P2D00:00 BECM","Blocage pompe LR A, moteur électrique sous le phare AVD","PID datalogger COOL_B_CMD(%) ; remplacer pompe réf. 2593011"],
  ["dtc","U3513–U3517","Tension faible du circuit B-C","Déposer batterie HT, remplacer fusible réf. 2411031"],
  ["incident","Pompe lave-glace","Kuga 2020","Vérifier fusibles F39 et F69 (alimentés via moteur essuie-glace)"],
  ["incident","Démarrage impossible","Transit Panther 2.0L","Vérifier fusible 20A F13, réf. 5559031"],
  ["incident","Ratés cylindre 2 et 3","Ford KA","Faire adaptation cible (accélération ×3 jusqu’à 6000 tr/min)"],
  ["incident","P0172 · Mélange trop riche","Kuga Flexifuel E85","Vérifier carburant (plein de SP95), apprentissage KAM, BT 25-2424"],
  ["incident","P0171 · Mélange trop pauvre","Kuga Flexifuel E85","Vérifier carburant (plein éthanol), reprogrammer PCM, apprentissage KAM, BT 25-2424"],
  ["incident","Démarrage difficile","EcoBoost","Ne pas oublier gobelet de pompe HP"],
  ["incident","Fuite huile boîte 6 vitesses","Focus / Puma / Fiesta","Vérifier reniflard, déposer boîtier filtre à air, remplacer reniflard (défaut assemblage)"],
  ["incident","ESP/ABS voyant allumé","Focus / Puma / Fiesta","Remplacer réf. 2369132"],
  ["incident","Problème Sync","Mach-E","Remise à zéro via volant côté droit + flèche bas"],
  ["incident","Joint EGR bloqué","Focus 1.5 Diesel","Remplacer joint HG9Q-9V473-AB"],
  ["incident","Pompe SCR","Puma · bulletin 21-7036","Remplacer pompe SCR"],
  ["incident","Module cc/cc","Puma 1.0 EcoBoost hybride","Remplacer module cc/cc"],
  ["incident","Non démarrage (P0087–P008A–P0627)","Puma Flexifuel","Remplacer pompe immergée réf. 2513934"],
  ["incident","Vitre qui ne remonte plus","Transit Custom 2024–","Mise à jour DDM ou PDM"],
  ["incident","DTC U0401 PAM","Kuga","Voir sonde de température extérieure débranchée"]
].map(([type, code, description, solution], id) => ({ type, code, description, solution, model: '', id }));
const savedEdits = JSON.parse(localStorage.getItem('ford-dtc-solution-edits') || '{}');
records = records.map(record => savedEdits[record.code] ? { ...record, solution: savedEdits[record.code] } : record);
records = [...records, ...JSON.parse(localStorage.getItem('ford-dtc-added-records') || '[]')];

const search = document.querySelector('#search');
const results = document.querySelector('#results');
const detail = document.querySelector('#detail');
const empty = document.querySelector('#empty');
const count = document.querySelector('#result-count');
let currentType = 'all';
let selectedId = null;

const normalise = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const escapeHtml = value => value.replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);

function filteredRecords() {
  const term = normalise(search.value.trim());
  return records.filter(record => (currentType === 'all' || record.type === currentType) && (!term || normalise(`${record.code} ${record.description} ${record.model || ''} ${record.solution}`).includes(term)));
}

function renderDetail(record) {
  selectedId = record.id;
  detail.innerHTML = `<div class="detail-top"><span class="type-pill ${record.type}">${record.type === 'dtc' ? 'Code DTC' : 'Incident spécifique'}</span><div class="detail-actions"><button class="copy-button" type="button" data-copy="${record.id}">Copier</button><button class="edit-button" type="button" data-edit-solution="${record.id}">Modifier</button></div></div><p class="detail-code">${escapeHtml(record.code)}</p><h2>${escapeHtml(record.description)}</h2>${record.model ? `<p class="vehicle-model">Modèle concerné · <strong>${escapeHtml(record.model)}</strong></p>` : ''}<div class="solution"><span>Solution recommandée</span><p>${escapeHtml(record.solution)}</p></div><p class="detail-tip">Pensez à effectuer les contrôles indiqués avant tout remplacement de pièce.</p>`;
}

function render() {
  const visible = filteredRecords();
  document.querySelector('#total-records').textContent = records.length;
  document.querySelector('.tab[data-type="all"] span').textContent = records.length;
  document.querySelector('.tab[data-type="dtc"] span').textContent = records.filter(record => record.type === 'dtc').length;
  document.querySelector('.tab[data-type="incident"] span').textContent = records.filter(record => record.type === 'incident').length;
  count.textContent = `${visible.length} résultat${visible.length > 1 ? 's' : ''}`;
  results.innerHTML = visible.map(record => `<button class="result-card ${selectedId === record.id ? 'selected' : ''}" type="button" data-id="${record.id}"><span class="type-pill ${record.type}">${record.type === 'dtc' ? 'DTC' : 'Incident'}</span><strong>${escapeHtml(record.code)}</strong><span class="result-description">${escapeHtml(record.description)}</span><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M9 18l6-6-6-6" /></svg></button>`).join('');
  empty.hidden = visible.length !== 0;
  results.hidden = visible.length === 0;
  document.querySelector('#clear-search').hidden = !search.value;
}

document.querySelector('.tabs').addEventListener('click', event => {
  const button = event.target.closest('.tab');
  if (!button) return;
  currentType = button.dataset.type;
  document.querySelectorAll('.tab').forEach(tab => { tab.classList.toggle('active', tab === button); tab.setAttribute('aria-selected', tab === button); });
  selectedId = null;
  detail.innerHTML = `<div class="detail-placeholder"><span class="detail-icon">⌁</span><h2>Sélectionnez une référence</h2><p>La description et la solution apparaîtront ici.</p></div>`;
  render();
});

search.addEventListener('input', render);
document.querySelector('#clear-search').addEventListener('click', () => { search.value = ''; search.focus(); render(); });
results.addEventListener('click', event => { const card = event.target.closest('[data-id]'); if (card) { renderDetail(records.find(record => record.id === Number(card.dataset.id))); render(); } });
detail.addEventListener('click', async event => {
  const button = event.target.closest('[data-copy]');
  if (!button) return;
  const solution = records.find(record => record.id === Number(button.dataset.copy)).solution;
  await navigator.clipboard.writeText(solution);
  button.textContent = 'Solution copiée ✓';
  setTimeout(() => { button.textContent = 'Copier la solution'; }, 1800);
});
const editDialog = document.querySelector('#edit-dialog');
const editForm = document.querySelector('#edit-form');
let editingId = null;
function closeEditDialog() { editDialog.close(); editingId = null; }
detail.addEventListener('click', event => {
  const button = event.target.closest('[data-edit-solution]');
  if (!button) return;
  const record = records.find(item => item.id === Number(button.dataset.editSolution));
  editingId = record.id;
  document.querySelector('#edit-code').textContent = record.code;
  document.querySelector('#edit-solution').value = record.solution;
  editDialog.showModal();
  document.querySelector('#edit-solution').focus();
});
document.querySelector('#close-edit-dialog').addEventListener('click', closeEditDialog);
document.querySelector('#cancel-edit').addEventListener('click', closeEditDialog);
editForm.addEventListener('submit', event => {
  event.preventDefault();
  const record = records.find(item => item.id === editingId);
  const solution = document.querySelector('#edit-solution').value.trim();
  record.solution = solution;
  if (record.id > 1000) localStorage.setItem('ford-dtc-added-records', JSON.stringify(records.filter(item => item.id > 1000)));
  else { savedEdits[record.code] = solution; localStorage.setItem('ford-dtc-solution-edits', JSON.stringify(savedEdits)); }
  renderDetail(record); render(); closeEditDialog();
});
document.addEventListener('keydown', event => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); search.focus(); } });
const addDialog = document.querySelector('#add-dialog');
const addForm = document.querySelector('#add-form');
const formError = document.querySelector('#form-error');
let addingType = 'dtc';
function closeAddDialog() { addDialog.close(); addForm.reset(); formError.textContent = ''; }
function openAddDialog(type) {
  addingType = type; addForm.reset(); formError.textContent = '';
  const incident = type === 'incident';
  document.querySelector('#add-dialog-title').textContent = incident ? 'Ajouter un incident' : 'Ajouter un DTC';
  document.querySelector('#new-code-label').textContent = incident ? 'Problème / symptôme' : 'Code DTC';
  document.querySelector('#new-code').placeholder = incident ? 'Ex. Démarrage difficile' : 'Ex. P0300';
  document.querySelector('#description-field').hidden = incident;
  document.querySelector('#new-description').required = !incident;
  document.querySelector('#new-model').placeholder = incident ? 'Ex. Transit Custom 2024' : 'Ex. Ranger 2.0 EcoBlue';
  document.querySelector('.submit-button').textContent = incident ? 'Ajouter l’incident' : 'Ajouter le DTC';
  addDialog.showModal(); document.querySelector('#new-code').focus();
}
document.querySelector('#open-add-dialog').addEventListener('click', () => openAddDialog('dtc'));
document.querySelector('#open-incident-dialog').addEventListener('click', () => openAddDialog('incident'));
document.querySelector('#close-add-dialog').addEventListener('click', closeAddDialog);
document.querySelector('#cancel-add').addEventListener('click', closeAddDialog);
addForm.addEventListener('submit', event => {
  event.preventDefault();
  const enteredCode = document.querySelector('#new-code').value.trim();
  const code = addingType === 'dtc' ? enteredCode.toUpperCase() : enteredCode;
  const description = document.querySelector('#new-description').value.trim();
  const model = document.querySelector('#new-model').value.trim();
  const solution = document.querySelector('#new-solution').value.trim();
  if (records.some(record => record.type === addingType && normalise(record.code) === normalise(code))) { formError.textContent = 'Cette référence existe déjà dans la base.'; return; }
  const record = { type: addingType, code, description: addingType === 'incident' ? model : description, model, solution, id: Date.now() };
  records.push(record);
  localStorage.setItem('ford-dtc-added-records', JSON.stringify(records.filter(item => item.id > 1000)));
  currentType = 'all';
  document.querySelectorAll('.tab').forEach(tab => { const active = tab.dataset.type === 'all'; tab.classList.toggle('active', active); tab.setAttribute('aria-selected', active); });
  search.value = code; renderDetail(record); render(); closeAddDialog();
});
render();
