"""Adiciona aba Eventos ao frontend."""
import shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
FRONTEND_WEB = PROJETO / "frontend" / "web"
INDEX = FRONTEND_WEB / "index.html"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

print(f"Frontend: {FRONTEND_WEB}")

for b in FRONTEND_WEB.glob("index.html.bak.*"):
    b.unlink()
    print(f"  [DEL] {b.name}")

if INDEX.exists():
    backup = INDEX.with_suffix(f".html.bak.{STAMP}")
    shutil.copy2(INDEX, backup)
    print(f"[BACKUP] {backup.name}")

conteudo = INDEX.read_text(encoding="utf-8")

# ============================================================
# 1. CSS
# ============================================================
css = '''
  /* ============ EVENTOS ============ */
  .evento-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 24px;
    transition: all 0.2s; cursor: pointer;
    display: flex; gap: 20px; align-items: flex-start;
  }
  .evento-card:hover { background: var(--bg-card-hover); border-color: var(--accent); transform: translateY(-2px); }
  .evento-card.inativa { opacity: 0.6; }
  .evento-data-bloco {
    width: 70px; flex-shrink: 0;
    display: flex; flex-direction: column; align-items: center;
    padding: 10px 8px;
    background: linear-gradient(135deg, #1e293b, #4f46e5);
    border-radius: 14px;
    color: white;
  }
  .evento-data-mes { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85; }
  .evento-data-dia { font-size: 32px; font-weight: 800; line-height: 1; margin: 4px 0; }
  .evento-data-hora { font-size: 11px; font-weight: 600; opacity: 0.9; }

  .evento-corpo { flex: 1; min-width: 0; }
  .evento-titulo { font-size: 18px; font-weight: 700; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .evento-meta { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
  .evento-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }
  .evento-badge {
    font-size: 11px; font-weight: 600; padding: 3px 8px;
    border-radius: 6px; letter-spacing: 0.3px;
  }
  .evento-badge.culto      { background: rgba(99,102,241,0.15); color: #818cf8; }
  .evento-badge.reuniao    { background: rgba(16,185,129,0.15); color: #34d399; }
  .evento-badge.conferencia{ background: rgba(139,92,246,0.15); color: #a78bfa; }
  .evento-badge.retiro     { background: rgba(245,158,11,0.15); color: #fbbf24; }
  .evento-badge.especial   { background: rgba(236,72,153,0.15); color: #f472b6; }
  .evento-badge.outro      { background: rgba(139,149,168,0.15); color: var(--text-muted); }
  .evento-badge.vagas      { background: rgba(16,185,129,0.15); color: var(--success); }
  .evento-badge.lotado     { background: rgba(239,68,68,0.15); color: var(--danger); }

  /* Inscricao item */
  .inscrito-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 8px;
  }
  .inscrito-avatar {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    border-radius: 10px; display: grid; place-items: center;
    font-size: 14px; font-weight: 700; color: white; flex-shrink: 0;
  }
  .inscrito-corpo { flex: 1; min-width: 0; }
  .inscrito-nome { font-size: 14px; font-weight: 600; }
  .inscrito-meta { font-size: 12px; color: var(--text-muted); }

  .inscrito-acoes { display: flex; gap: 6px; }

  .status-badge {
    font-size: 11px; font-weight: 600; padding: 3px 8px;
    border-radius: 6px;
  }
  .status-badge.inscrito { background: rgba(99,102,241,0.15); color: var(--accent); }
  .status-badge.presente { background: rgba(16,185,129,0.15); color: var(--success); }
  .status-badge.ausente  { background: rgba(245,158,11,0.15); color: var(--warning); }
  .status-badge.cancelado{ background: rgba(239,68,68,0.15); color: var(--danger); }

  .eventos-lista { display: flex; flex-direction: column; gap: 12px; }
'''

if ".evento-card" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Adicionar aba no nav (depois de Oração)
# ============================================================
aba_nav = '<button class="tab" data-tab="eventos" onclick="trocarAba(\'eventos\')">📅 Eventos</button>'
marcador_nav = '<button class="tab" data-tab="usuarios" onclick="trocarAba(\'usuarios\')" id="tab-usuarios" style="display:none;">👤 Usuários</button>'

if 'data-tab="eventos"' not in conteudo and marcador_nav in conteudo:
    conteudo = conteudo.replace(marcador_nav, aba_nav + "\n    " + marcador_nav, 1)

# ============================================================
# 3. HTML da aba
# ============================================================
html_aba = '''
    <!-- ABA EVENTOS -->
    <div id="conteudo-eventos" style="display: none;">
      <h1 class="page-title">📅 Eventos</h1>
      <p class="page-subtitle">Agenda de cultos, reuniões e conferências</p>

      <div id="eventos-alertas" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 16px; margin-bottom: 32px;"></div>

      <div class="toolbar">
        <input type="text" class="toolbar-search" id="busca-evento" placeholder="🔎 Buscar por título ou local..." oninput="renderizarEventos()">
        <select class="toolbar-select" id="filtro-tipo-evento" onchange="carregarEventos()">
          <option value="">Todos os tipos</option>
          <option value="culto">Culto</option>
          <option value="reuniao">Reunião</option>
          <option value="conferencia">Conferência</option>
          <option value="retiro">Retiro</option>
          <option value="especial">Especial</option>
          <option value="outro">Outro</option>
        </select>
        <label class="toolbar-check">
          <input type="checkbox" id="mostrar-inativos-evento" onchange="carregarEventos()">
          Mostrar inativos
        </label>
        <div class="toolbar-count" id="contador-eventos"></div>
      </div>
      <div id="container-eventos" class="eventos-lista"></div>
    </div>
'''

if 'id="conteudo-eventos"' not in conteudo:
    marcador = "  </main>"
    conteudo = conteudo.replace(marcador, html_aba + marcador, 1)

# ============================================================
# 4. Modais
# ============================================================
modais = '''
<!-- Evento: form -->
<div class="modal-backdrop" id="modal-form-evento">
  <div class="modal">
    <div class="modal-header">
      <h2 class="modal-title" id="form-evento-titulo">Novo Evento</h2>
      <button class="modal-close" onclick="fecharFormEvento()">×</button>
    </div>
    <form id="form-evento" onsubmit="salvarEvento(event)">
      <input type="hidden" id="form-evento-id">
      <div class="form-group">
        <label class="form-label">Título *</label>
        <input class="form-input" name="titulo" required minlength="2" placeholder="Culto de Domingo">
      </div>
      <div class="form-group">
        <label class="form-label">Descrição</label>
        <textarea class="form-input" name="descricao" rows="2" style="font-family: inherit; resize: vertical;"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Tipo *</label>
          <select class="form-select" name="tipo" required>
            <option value="culto">Culto</option>
            <option value="reuniao">Reunião</option>
            <option value="conferencia">Conferência</option>
            <option value="retiro">Retiro</option>
            <option value="especial">Especial</option>
            <option value="outro">Outro</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Vagas</label>
          <input class="form-input" type="number" name="vagas" min="0" placeholder="Sem limite">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Início *</label>
          <input class="form-input" type="datetime-local" name="data_inicio" required id="input-inicio-evento">
        </div>
        <div class="form-group">
          <label class="form-label">Fim</label>
          <input class="form-input" type="datetime-local" name="data_fim">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Local</label>
        <input class="form-input" name="local" placeholder="Templo Principal">
      </div>
      <div class="form-group">
        <label class="form-label">Endereço</label>
        <input class="form-input" name="endereco" placeholder="Rua Exemplo, 123">
      </div>
      <div class="form-row">
        <label class="form-check"><input type="checkbox" name="publico" checked> Público</label>
        <label class="form-check"><input type="checkbox" name="requer_inscricao"> Requer inscrição</label>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormEvento()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-evento">Criar Evento</button>
      </div>
    </form>
  </div>
</div>

<!-- Evento: detalhes -->
<div class="modal-backdrop" id="modal-detalhes-evento">
  <div class="modal" style="max-width: 640px;">
    <div class="modal-header">
      <h2 class="modal-title" id="detalhe-evento-titulo">Evento</h2>
      <button class="modal-close" onclick="fecharDetalhesEvento()">×</button>
    </div>
    <div id="detalhe-evento-corpo"></div>

    <div style="display:flex; justify-content:space-between; align-items:center; margin: 20px 0 12px;">
      <div style="font-size:14px; font-weight:700;">Inscritos</div>
      <button class="btn btn-primary" style="padding:8px 14px; font-size:13px;" onclick="abrirFormInscricao()">+ Inscrever pessoa</button>
    </div>
    <div id="detalhe-evento-inscritos"></div>

    <div class="modal-actions modal-actions-3" style="margin-top: 20px;">
      <button class="btn btn-ghost" onclick="fecharDetalhesEvento()">Fechar</button>
      <button class="btn btn-primary" onclick="editarEventoDoDetalhe()">Editar</button>
      <button class="btn btn-danger" onclick="confirmarDeletarEvento()">Deletar</button>
    </div>
    <div class="modal-actions" style="margin-top: 8px;">
      <button class="btn btn-warning" id="btn-toggle-evento" onclick="toggleAtivoEvento()">Desativar</button>
    </div>
  </div>
</div>

<!-- Inscricao: form -->
<div class="modal-backdrop" id="modal-form-inscricao">
  <div class="modal" style="max-width: 460px;">
    <div class="modal-header">
      <h2 class="modal-title">Inscrever pessoa</h2>
      <button class="modal-close" onclick="fecharFormInscricao()">×</button>
    </div>
    <form id="form-inscricao" onsubmit="salvarInscricao(event)">
      <div class="form-group">
        <label class="form-label">Pessoa *</label>
        <select class="form-select" id="select-pessoa-inscricao" required></select>
      </div>
      <div class="form-group">
        <label class="form-label">Observação</label>
        <input class="form-input" id="input-obs-inscricao" placeholder="Opcional">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormInscricao()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-inscricao">Inscrever</button>
      </div>
    </form>
  </div>
</div>
'''

if 'id="modal-form-evento"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)

# ============================================================
# 5. JS
# ============================================================
js = '''
// ============ EVENTOS ============
let eventosCache = [];
let eventoAtual = null;
let inscricoesEventoAtual = [];
let pessoasParaInscricao = [];

const TIPO_LABEL = {
  culto: "🎤 Culto",
  reuniao: "👥 Reunião",
  conferencia: "🎙️ Conferência",
  retiro: "🏕️ Retiro",
  especial: "⭐ Especial",
  outro: "📌 Outro",
};

const MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"];

function formatarDataEvento(iso) {
  const d = new Date(iso);
  const dia = String(d.getDate()).padStart(2, "0");
  const mes = MESES[d.getMonth()];
  const hora = String(d.getHours()).padStart(2, "0") + "h" + String(d.getMinutes()).padStart(2, "0");
  return { dia, mes, hora, dataCompleta: d.toLocaleString("pt-BR") };
}

async function carregarEventos() {
  const container = document.getElementById("container-eventos");
  if (!container) return;
  container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⏳</div><div class="state-text">Carregando...</div></div>`;

  const tipo = document.getElementById("filtro-tipo-evento").value;
  const mostrarInativos = document.getElementById("mostrar-inativos-evento").checked;

  const params = new URLSearchParams();
  if (tipo) params.append("tipo", tipo);
  if (!mostrarInativos) params.append("apenas_ativos", "true");

  try {
    const r = await apiFetch(`${API}/eventos/?${params}`);
    eventosCache = await r.json();
    renderizarEventos();
    carregarAlertasEventos();
  } catch (e) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⚠️</div><div class="state-text">${e.message}</div></div>`;
  }
}

async function carregarAlertasEventos() {
  const div = document.getElementById("eventos-alertas");
  if (!div) return;
  try {
    const r = await apiFetch(`${API}/eventos/dashboard/proximos`);
    const d = await r.json();
    const cards = [
      { label: "Próximos 7 dias", valor: d.total_proximos_7d, cor: "var(--accent)", icon: "📅" },
      { label: "Próximos 30 dias", valor: d.total_proximos_30d, cor: "var(--accent)", icon: "🗓️" },
    ];
    div.innerHTML = cards.map(c => `
      <div class="card" style="cursor: default;">
        <div style="font-size: 28px; margin-bottom: 8px;">${c.icon}</div>
        <div style="font-size: 32px; font-weight: 700; color: ${c.cor};">${c.valor}</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">${c.label}</div>
      </div>
    `).join("");
  } catch (e) { /* silencioso */ }
}

function renderizarEventos() {
  const container = document.getElementById("container-eventos");
  const contador = document.getElementById("contador-eventos");
  const busca = document.getElementById("busca-evento").value.toLowerCase().trim();
  const filtrados = eventosCache.filter(e => {
    if (!busca) return true;
    return [e.titulo, e.local].filter(Boolean).join(" ").toLowerCase().includes(busca);
  });

  const total = eventosCache.length;
  const ativos = eventosCache.filter(e => e.ativo).length;
  contador.textContent = `${total} evento${total !== 1 ? "s" : ""} (${ativos} ativo${ativos !== 1 ? "s" : ""})`;

  if (filtrados.length === 0 && busca) {
    container.innerHTML = `<div class="state"><div class="state-icon">🔎</div><div class="state-text">Nenhum resultado.</div></div>`;
    return;
  }
  if (eventosCache.length === 0) {
    container.innerHTML = `
      <div class="state"><div class="state-icon">📅</div><div class="state-text">Nenhum evento cadastrado ainda.</div></div>
      <div class="card card-new" onclick="abrirFormEvento()"><div class="card-new-inner"><div class="card-new-plus">+</div><div class="card-new-label">Novo Evento</div></div></div>`;
    return;
  }

  let html = "";
  for (const e of filtrados) {
    const f = formatarDataEvento(e.data_inicio);
    const cls = e.ativo ? "" : "inativa";
    const tipoClass = e.tipo || "outro";
    const temVagas = e.vagas !== null && e.vagas !== undefined;
    const totalInscritos = e.total_inscritos || 0;
    const lotado = temVagas && totalInscritos >= e.vagas;

    let vagasBadge = "";
    if (temVagas) {
      vagasBadge = lotado
        ? `<span class="evento-badge lotado">LOTADO</span>`
        : `<span class="evento-badge vagas">${totalInscritos}/${e.vagas} vagas</span>`;
    } else if (totalInscritos > 0) {
      vagasBadge = `<span class="evento-badge vagas">${totalInscritos} inscrito${totalInscritos !== 1 ? "s" : ""}</span>`;
    }

    html += `
      <div class="evento-card ${cls}" onclick="abrirDetalhesEvento('${e.id}')">
        <div class="evento-data-bloco">
          <div class="evento-data-mes">${f.mes}</div>
          <div class="evento-data-dia">${f.dia}</div>
          <div class="evento-data-hora">${f.hora}</div>
        </div>
        <div class="evento-corpo">
          <div class="evento-titulo">
            ${e.titulo}
            ${!e.ativo ? '<span class="card-tag" style="background:rgba(245,158,11,0.15);color:var(--warning);">INATIVO</span>' : ""}
          </div>
          ${e.local ? `<div class="evento-meta">📍 ${e.local}</div>` : ""}
          ${e.descricao ? `<div class="evento-meta">${e.descricao}</div>` : ""}
          <div class="evento-badges">
            <span class="evento-badge ${tipoClass}">${TIPO_LABEL[e.tipo] || e.tipo}</span>
            ${vagasBadge}
            ${e.publico ? "" : '<span class="evento-badge outro">🔒 Restrito</span>'}
          </div>
        </div>
      </div>
    `;
  }
  html += `<div class="card card-new" onclick="abrirFormEvento()"><div class="card-new-inner"><div class="card-new-plus">+</div><div class="card-new-label">Novo Evento</div></div></div>`;
  container.innerHTML = html;
}

function abrirFormEvento(evento = null) {
  document.getElementById("form-evento").reset();
  const t = document.getElementById("form-evento-titulo");
  const b = document.getElementById("btn-salvar-evento");

  if (evento) {
    t.textContent = "Editar Evento"; b.textContent = "Salvar Alterações";
    document.getElementById("form-evento-id").value = evento.id;
    ["titulo","descricao","tipo","local","endereco"].forEach(k => {
      const el = document.querySelector(`#form-evento [name="${k}"]`);
      if (el) el.value = evento[k] || "";
    });
    if (evento.vagas !== null && evento.vagas !== undefined) {
      document.querySelector('#form-evento [name="vagas"]').value = evento.vagas;
    }
    document.querySelector('#form-evento [name="data_inicio"]').value = evento.data_inicio.slice(0, 16);
    if (evento.data_fim) {
      document.querySelector('#form-evento [name="data_fim"]').value = evento.data_fim.slice(0, 16);
    }
    document.querySelector('#form-evento [name="publico"]').checked = !!evento.publico;
    document.querySelector('#form-evento [name="requer_inscricao"]').checked = !!evento.requer_inscricao;
  } else {
    t.textContent = "Novo Evento"; b.textContent = "Criar Evento";
    document.getElementById("form-evento-id").value = "";
    // Sugere data de hoje às 19h
    const agora = new Date();
    agora.setHours(19, 0, 0, 0);
    const iso = agora.toISOString().slice(0, 16);
    document.getElementById("input-inicio-evento").value = iso;
  }
  document.getElementById("modal-form-evento").classList.add("active");
  document.querySelector('#form-evento [name="titulo"]').focus();
}

function fecharFormEvento() { document.getElementById("modal-form-evento").classList.remove("active"); }

async function salvarEvento(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-evento");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";
  const form = new FormData(e.target);
  const dados = {};
  for (const [k, v] of form.entries()) {
    if (k === "id") continue;
    if (k === "publico" || k === "requer_inscricao") { dados[k] = form.get(k) === "on"; continue; }
    if (k === "vagas") { if (v.trim()) dados[k] = parseInt(v); continue; }
    if (typeof v === "string" && v.trim()) dados[k] = v.trim();
  }
  // Converte datas para ISO completo
  if (dados.data_inicio) dados.data_inicio = new Date(dados.data_inicio).toISOString();
  if (dados.data_fim) dados.data_fim = new Date(dados.data_fim).toISOString();

  const id = document.getElementById("form-evento-id").value;
  const url = id ? `${API}/eventos/${id}` : `${API}/eventos/`;
  const metodo = id ? "PUT" : "POST";
  try {
    const r = await apiFetch(url, { method: metodo, headers: {"Content-Type":"application/json"}, body: JSON.stringify(dados) });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormEvento();
    mostrarToast(id ? "✅ Evento atualizado!" : "✅ Evento criado!", "success");
    carregarEventos();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

async function abrirDetalhesEvento(id) {
  const e = eventosCache.find(x => x.id === id); if (!e) return;
  eventoAtual = e;
  const f = formatarDataEvento(e.data_inicio);
  document.getElementById("detalhe-evento-titulo").textContent = e.titulo;

  const linhas = [
    ["Tipo", TIPO_LABEL[e.tipo] || e.tipo],
    ["Início", f.dataCompleta],
    ["Fim", e.data_fim ? new Date(e.data_fim).toLocaleString("pt-BR") : null],
    ["Local", e.local],
    ["Endereço", e.endereco],
    ["Vagas", e.vagas !== null ? String(e.vagas) : "Sem limite"],
    ["Público", e.publico ? "Sim" : "Restrito"],
    ["Requer inscrição", e.requer_inscricao ? "Sim" : "Não"],
    ["Descrição", e.descricao],
    ["Responsável", e.responsavel?.nome],
    ["Situação", e.ativo ? "Ativo" : "Inativo"],
  ].filter(([,v]) => v);

  document.getElementById("detalhe-evento-corpo").innerHTML = linhas.map(([k,v])=>`<div class="detail-row"><div class="detail-label">${k}</div><div class="detail-value">${v}</div></div>`).join("");

  // Botão toggle
  const b = document.getElementById("btn-toggle-evento");
  if (e.ativo) { b.textContent = "Desativar"; b.className = "btn btn-warning"; }
  else { b.textContent = "Reativar"; b.className = "btn btn-success"; }

  document.getElementById("modal-detalhes-evento").classList.add("active");

  // Carrega inscritos
  await carregarInscritos(id);
}

async function carregarInscritos(eventoId) {
  const div = document.getElementById("detalhe-evento-inscritos");
  div.innerHTML = `<div class="state" style="padding:20px;"><div class="state-icon">⏳</div><div class="state-text">Carregando inscritos...</div></div>`;
  try {
    const r = await apiFetch(`${API}/eventos/${eventoId}/inscricoes`);
    inscricoesEventoAtual = await r.json();
    renderizarInscritos();
  } catch (e) {
    div.innerHTML = `<div class="state" style="padding:20px;"><div class="state-text">${e.message}</div></div>`;
  }
}

function renderizarInscritos() {
  const div = document.getElementById("detalhe-evento-inscritos");
  if (inscricoesEventoAtual.length === 0) {
    div.innerHTML = `<div class="state" style="padding:20px;"><div class="state-icon">👥</div><div class="state-text">Nenhum inscrito ainda.</div></div>`;
    return;
  }

  div.innerHTML = inscricoesEventoAtual.map(i => {
    const iniciais = (i.pessoa?.nome || "?").split(" ").slice(0, 2).map(s => s[0]).join("").toUpperCase();
    const statusLabel = { inscrito: "Inscrito", presente: "Presente", ausente: "Ausente", cancelado: "Cancelado" };
    return `
      <div class="inscrito-item">
        <div class="inscrito-avatar">${iniciais}</div>
        <div class="inscrito-corpo">
          <div class="inscrito-nome">${i.pessoa?.nome || "?"}</div>
          <div class="inscrito-meta">
            <span class="status-badge ${i.status}">${statusLabel[i.status] || i.status}</span>
            ${i.observacao ? ` · ${i.observacao}` : ""}
          </div>
        </div>
        <div class="inscrito-acoes">
          ${i.status !== "presente" ? `<button class="btn btn-success" style="padding:6px 10px; font-size:12px;" onclick="checkinInscricao('${i.id}', 'presente')" title="Marcar como presente">✓</button>` : ""}
          <button class="btn btn-danger" style="padding:6px 10px; font-size:12px;" onclick="deletarInscricao('${i.id}')" title="Remover inscrição">✕</button>
        </div>
      </div>`;
  }).join("");
}

async function checkinInscricao(id, status) {
  try {
    const r = await apiFetch(`${API}/eventos/inscricoes/${id}/checkin`, {
      method: "PATCH",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ status }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    mostrarToast("✅ Check-in realizado!", "success");
    await carregarInscritos(eventoAtual.id);
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
}

async function deletarInscricao(id) {
  abrirConfirmar("Remover inscrição?", "Tem certeza que deseja remover esta inscrição?", async () => {
    try {
      const r = await apiFetch(`${API}/eventos/inscricoes/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Inscrição removida.", "success");
      await carregarInscritos(eventoAtual.id);
      carregarEventos();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

function fecharDetalhesEvento() {
  document.getElementById("modal-detalhes-evento").classList.remove("active");
  eventoAtual = null;
  inscricoesEventoAtual = [];
}

function editarEventoDoDetalhe() { if (!eventoAtual) return; const e = eventoAtual; fecharDetalhesEvento(); abrirFormEvento(e); }

function confirmarDeletarEvento() {
  if (!eventoAtual) return;
  const e = eventoAtual;
  abrirConfirmar("Excluir evento?", `Tem certeza que deseja EXCLUIR "${e.titulo}"? Se houver inscrições, a exclusão será bloqueada.`, async () => {
    try {
      const r = await apiFetch(`${API}/eventos/${e.id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      fecharDetalhesEvento(); mostrarToast("✅ Evento excluído.", "success"); carregarEventos();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

function toggleAtivoEvento() {
  if (!eventoAtual) return;
  const e = eventoAtual; const acao = e.ativo ? "desativar" : "reativar";
  abrirConfirmar(e.ativo ? "Desativar evento?" : "Reativar evento?", e.ativo ? `"${e.titulo}" ficará inativo.` : `"${e.titulo}" voltará a ficar ativo.`, async () => {
    try {
      const r = await apiFetch(`${API}/eventos/${e.id}/${acao}`, { method: "PATCH" });
      if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      fecharDetalhesEvento(); mostrarToast(e.ativo ? "✅ Evento desativado." : "✅ Evento reativado.", "success"); carregarEventos();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

async function carregarPessoasParaInscricao() {
  try {
    const r = await apiFetch(`${API}/pessoas/?apenas_ativos=true&limit=1000`);
    pessoasParaInscricao = await r.json();
    const sel = document.getElementById("select-pessoa-inscricao");
    sel.innerHTML = '<option value="">Selecione a pessoa...</option>' +
      pessoasParaInscricao.map(p => `<option value="${p.id}">${p.nome}</option>`).join("");
  } catch (e) { /* silencioso */ }
}

function abrirFormInscricao() {
  if (!eventoAtual) return;
  document.getElementById("form-inscricao").reset();
  carregarPessoasParaInscricao();
  document.getElementById("modal-form-inscricao").classList.add("active");
}

function fecharFormInscricao() { document.getElementById("modal-form-inscricao").classList.remove("active"); }

async function salvarInscricao(e) {
  e.preventDefault();
  if (!eventoAtual) return;
  const btn = document.getElementById("btn-salvar-inscricao");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Inscrevendo...";
  const pessoaId = document.getElementById("select-pessoa-inscricao").value;
  const obs = document.getElementById("input-obs-inscricao").value.trim();
  if (!pessoaId) { mostrarToast("❌ Selecione uma pessoa", "error"); btn.disabled = false; btn.textContent = txt; return; }

  try {
    const r = await apiFetch(`${API}/eventos/${eventoAtual.id}/inscricoes`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ pessoa_id: pessoaId, observacao: obs || null }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormInscricao();
    mostrarToast("✅ Pessoa inscrita!", "success");
    await carregarInscritos(eventoAtual.id);
    carregarEventos();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}
'''

if "// ============ EVENTOS ============" not in conteudo:
    marcador = "// ============ CONFIRMAR ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)

# ============================================================
# 6. Atualizar trocarAba
# ============================================================
import re
novo_trocar = '''function trocarAba(nome) {
  document.querySelectorAll(".tab").forEach(t => t.classList.toggle("ativa", t.dataset.tab === nome));
  const inicio = document.getElementById("conteudo-inicio");
  if (inicio) inicio.style.display = nome === "inicio" ? "block" : "none";
  document.getElementById("conteudo-igrejas").style.display = nome === "igrejas" ? "block" : "none";
  document.getElementById("conteudo-pessoas").style.display = nome === "pessoas" ? "block" : "none";
  document.getElementById("conteudo-cuidado").style.display = nome === "cuidado" ? "block" : "none";
  document.getElementById("conteudo-oracao").style.display = nome === "oracao" ? "block" : "none";
  const contEventos = document.getElementById("conteudo-eventos");
  if (contEventos) contEventos.style.display = nome === "eventos" ? "block" : "none";
  document.getElementById("conteudo-usuarios").style.display = nome === "usuarios" ? "block" : "none";
  if (nome === "inicio") { carregarDashboard(); }
  else if (nome === "pessoas") { carregarSelectIgrejas(); carregarPessoas(); }
  else if (nome === "cuidado") { carregarAcompanhamentos(); }
  else if (nome === "oracao") { carregarOracoes(); }
  else if (nome === "eventos") { carregarEventos(); }
  else if (nome === "usuarios") { carregarIgrejasParaUsuario(); carregarUsuarios(); }
  else { carregarIgrejas(); }
}'''
conteudo = re.sub(r'function trocarAba\(nome\) \{.*?\n\}', novo_trocar, conteudo, count=1, flags=re.DOTALL)

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("=" * 60)