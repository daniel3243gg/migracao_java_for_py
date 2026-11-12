function esc(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}


let _toastTimer = null;

function showToast(msg, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast ' + type;
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { el.className = 'toast hidden'; }, 3500);
}


function openModal(title, bodyHtml) {
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-body').innerHTML = bodyHtml;
  document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.add('hidden');
  document.getElementById('modal-body').innerHTML = '';
}

function closeModalOverlay(event) {
  if (event.target === document.getElementById('modal-overlay')) closeModal();
}


const sectionLoaders = {
  dashboard:      loadDashboard,
  clientes:       () => Clientes.carregar(),
  veiculos:       () => Veiculos.carregar(),
  vagas:          () => Vagas.carregar(),
  estacionamento: loadEstacionamento,
  historico:      () => Permanencias.carregarHistorico(),
};

function navigateTo(sectionId) {
  document.querySelectorAll('.nav-link').forEach(el => {
    el.classList.toggle('active', el.dataset.section === sectionId);
  });

  document.querySelectorAll('.section').forEach(el => {
    el.classList.toggle('active', el.id === sectionId);
  });

  const loader = sectionLoaders[sectionId];
  if (loader) loader();
}

async function loadDashboard() {
  try {
    const data = await API.get('/api/dashboard');
    document.getElementById('stat-total').textContent       = data.totalVagas           ?? 0;
    document.getElementById('stat-livres').textContent      = data.vagasLivres          ?? 0;
    document.getElementById('stat-ocupadas').textContent    = data.vagasOcupadas        ?? 0;
    document.getElementById('stat-estacionados').textContent= data.veiculosEstacionados ?? 0;
  } catch (e) {
    showToast('Erro ao carregar dashboard: ' + e.message, 'error');
  }
}

async function loadEstacionamento() {
  await Promise.all([
    Clientes.carregar(),
    Permanencias.popularSelectsEntrada(),
    Permanencias.carregarEstacionados(),
  ]);
}


document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      navigateTo(link.dataset.section);
    });
  });

  navigateTo('dashboard');
});
