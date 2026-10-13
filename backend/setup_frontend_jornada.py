"""Adiciona aba Jornada ao frontend (CRUD de trilhas)."""
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
  /* ============ JORNADA ============ */
  .trilha-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 24px;
    transition: all 0.2s; cursor: pointer;
  }
  .trilha-card:hover { background: var(--bg-card-hover); border-color: var(--accent); transform: translateY(-2px); }
  .trilha-card.inativa { opacity: 0.6; }
  .trilha-titulo { font-size: 18px; font-weight: 700; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .trilha-meta { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
  .trilha-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; }
  .trilha-badge {
    font-size: 11px; font-weight: 600; padding: 3px 8px;
    border-radius: 6px; letter-spacing: 0.3px;
  }
  .trilha-badge.batismo     { background: rgba(99,102,241,0.15); color: #818cf8; }
  .trilha-badge.discipulado { background: rgba(16,185,129,0.15); color: #34d399; }
  .trilha-badge.lideranca   { background: rgba(139,92,246,0.15); color: #a78bfa; }
  .trilha-badge.outro       { background: rgba(139,149,168,0.15); color: var(--text-muted); }

  .etapa-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 8px;
  }
  .etapa-ordem {
    width: 32px; height: 32px;
    background: rgba(99,102,241,0.15); color: var(--accent);
    border-radius: 50%; display: grid; place-items: center;
    font-size: 13px; font-weight: 700; flex-shrink: 0;
  }
  .etapa-corpo { flex: 1; min-width: 0; }
  .etapa-nome { font-size: 14px; font-weight: 600; }
  .etapa-desc { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
  .etapa-tag {
    font-size: 10px; font-weight: 600; padding: 2px 6px;
    border-radius: 5px; letter-spacing: 0.3px;
  }
  .etapa-tag.obrigatoria { background: rgba(239,68,68,0.15); color: var(--danger); }
  .etapa-tag.opcional    { background: rgba(139,149,168,0.15); color: var(--text-muted); }

  .etapa-builder {
    display: flex; gap: 8px; align-items: center;
    padding: 10px; background: var(--bg);
    border: 1px solid var(--border); border-radius: 10px;
    margin-bottom: 8px;
  }
  .etapa-builder input[type="text"] {
    flex: 1; padding: 8px 12px;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text);
    font-size: 13px; font-family: inherit;
  }
  .etapa-builder input[type="text"]:focus { outline: none; border-color: var(--accent); }
  .etapa-builder input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--accent); }
  .etapa-builder .btn-remove {
    background: transparent; border: none; color: var(--danger);
    font-size: 18px; cursor: pointer; padding: 4px 8px;
  }
'''

if ".trilha-card" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Adicionar aba no nav (depois de Eventos)
# ============================================================
aba_nav = '<button class="tab" data-tab="jornada" onclick="trocarAba(\'jornada\')">🎯 Jornada</button>'
marcador_nav = '<button class="tab" data-tab="usuarios" onclick="trocarAba(\'usuarios\')" id="tab-usuarios" style="display:none;">👤 Usuários</button>'

if 'data-tab="jornada"' not in conteudo and marcador_nav in conteudo:
    conteudo = conteudo.replace(marcador_nav, aba_nav + "\n    " + marcador_nav, 1)

# ============================================================
# 3. HTML da aba
# ============================================================
html_aba = '''
    <!-- ABA JORNADA -->
    <div id="conteudo-jornada" style="display: none;">
      <h1 class="page-title">🎯 Jornada</h1>
      <p class="page-subtitle">Trilhas de discipulado e crescimento espiritual</p>

      <div id="jornada-alertas" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px;"></div>

      <div class="toolbar">
        <input type="text" class="toolbar-search" id="busca-trilha" placeholder="🔎 Buscar por nome..." oninput="renderizarTrilhas()">
        <select class="toolbar-select" id="filtro-tipo-trilha" onchange="carregarTrilhas()">
          <option value="">Todos os tipos</option>
          <option value="batismo">Batismo</option>
          <option value="discipulado">Discipulado</option>
          <option value="lideranca">Liderança</option>
          <option value="outro">Outro</option>
        </select>
        <label class="toolbar-check">
          <input type="checkbox" id="mostrar-inativas-trilha" onchange="carregarTrilhas()">
          Mostrar inativas
        </label>
        <div class="toolbar-count" id="contador-trilhas"></div>
      </div>
      <div id="container-trilhas" class="grid"></div>
    </div>
'''

if 'id="conteudo-jornada"' not in conteudo:
    marcador = "  </main>"
    conteudo = conteudo.replace(marcador, html_aba + marcador, 1)

# ============================================================
# 4. Modais
# ============================================================
modais = '''
<!-- Trilha: form -->
<div class="modal-backdrop" id="modal-form-trilha">
  <div class="modal" style="max-width: 640px;">
    <div class="modal-header">
      <h2 class="modal-title" id="form-trilha-titulo">Nova Trilha</h2>
      <button class="modal-close" onclick="fecharFormTrilha()">×</button>
    </div>
    <form id="form-trilha" onsubmit="salvarTrilha(event)">
      <input type="hidden" id="form-trilha-id">
      <div class="form-group">
        <label class="form-label">Nome *</label>
        <input class="form-input" name="nome" required minlength="2" placeholder="Trilha de Batismo">
      </div>
      <div class="form-group">
        <label class="form-label">Descrição</label>
        <textarea class="form-input" name="descricao" rows="2" style="font-family: inherit; resize: vertical;"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Tipo *</label>
        <select class="form-select" name="tipo" required>
          <option value="batismo">Batismo</option>
          <option value="discipulado" selected>Discipulado</option>
          <option value="lideranca">Liderança</option>
          <option value="outro">Outro</option>
        </select>
      </div>

      <div id="campo-etapas" style="margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <label class="form-label" style="margin: 0;">Etapas</label>
          <button type="button" class="btn btn-ghost" style="padding: 6px 12px; font-size: 12px;" onclick="adicionarEtapa()">+ Adicionar etapa</button>
        </div>
        <div id="etapas-builder"></div>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormTrilha()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-trilha">Criar Trilha</button>
      </div>
    </form>
  </div>
</div>

<!-- Trilha: detalhes -->
<div class="modal-backdrop" id="modal-detalhes-trilha">
  <div class="modal" style="max-width: 640px;">
    <div class="modal-header">
      <h2 class="modal-title" id="detalhe-trilha-titulo">Trilha</h2>
      <button class="modal-close" onclick="fecharDetalhesTrilha()">×</button>
    </div>
    <div id="detalhe-trilha-corpo"></div>

    <div style="font-size:14px; font-weight:700; margin: 20px 0 12px;">Etapas</div>
    <div id="detalhe-trilha-etapas"></div>

    <div class="modal-actions modal-actions-3" style="margin-top: 20px;">
      <button class="btn btn-ghost" onclick="fecharDetalhesTrilha()">Fechar</button>
      <button class="btn btn-primary" onclick="editarTrilhaDoDetalhe()">Editar</button>
      <button class="btn btn-danger" onclick="confirmarDeletarTrilha()">Deletar</button>
    </div>
    <div class="modal-actions" style="margin-top: 8px;">
      <button class="btn btn-warning" id="btn-toggle-trilha" onclick="toggleAtivaTrilha()">Desativar</button>
    </div>
  </div>
</div>
'''

if 'id="modal-form-trilha"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)

# ============================================================
# 5. JS
# ============================================================
js = '''
// ============ JORNADA ============
let trilhasCache = [];
let trilhaAtual = null;

const TIPO_TRILHA_LABEL = {
  batismo: "💧 Batismo",
  discipulado: "📖 Discipulado",
  lideranca: "👑 Liderança",
  outro: "📌 Outro",
};

async function carregarTrilhas() {
  const container = document.getElementById("container-trilhas");
  if (!container) return;
  container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⏳</div><div class="state-text">Carregando...</div></div>`;

  const tipo = document.getElementById("filtro-tipo-trilha").value;
  const mostrarInativas = document.getElementById("mostrar-inativas-trilha").checked;

  const params = new URLSearchParams();
  if (tipo) params.append("tipo", tipo);
  if (!mostrarInativas) params.append("apenas_ativas", "true");

  try {
    const r = await apiFetch(`${API}/jornada/trilhas/?${params}`);
    trilhasCache = await r.json();
    renderizarTrilhas();
    carregarAlertasJornada();
  } catch (e) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⚠️</div><div class="state-text">${e.message}</div></div>`;
  }
}

async function carregarAlertasJornada() {
  const div = document.getElementById("jornada-alertas");
  if (!div) return;
  try {
    const r = await apiFetch(`${API}/jornada/dashboard`);
    const d = await r.json();
    const cards = [
      { label: "Trilhas ativas", valor: d.total_trilhas_ativas, cor: "var(--accent)", icon: "🎯" },
      { label: "Em andamento", valor: d.total_em_andamento, cor: "var(--warning)", icon: "🏃" },
      { label: "Concluídas", valor: d.total_concluidas, cor: "var(--success)", icon: "✅" },
      { label: "Concluídas (30d)", valor: d.concluidas_ultimos_30_dias, cor: "var(--success)", icon: "📈" },
    ];
    div.innerHTML = cards.map(c => `
      <div class="card" style="cursor: default;">
        <div style="font-size: 24px; margin-bottom: 8px;">${c.icon}</div>
        <div style="font-size: 28px; font-weight: 700; color: ${c.cor};">${c.valor}</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">${c.label}</div>
      </div>
    `).join("");
  } catch (e) { /* silencioso */ }
}

function renderizarTrilhas() {
  const container = document.getElementById("container-trilhas");
  const contador = document.getElementById("contador-trilhas");
  const busca = document.getElementById("busca-trilha").value.toLowerCase().trim();
  const filtradas = trilhasCache.filter(t => {
    if (!busca) return true;
    return (t.nome || "").toLowerCase().includes(busca);
  });

  const total = trilhasCache.length;
  const ativas = trilhasCache.filter(t => t.ativa).length;
  contador.textContent = `${total} trilha${total !== 1 ? "s" : ""} (${ativas} ativa${ativas !== 1 ? "s" : ""})`;

  if (filtradas.length === 0 && busca) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">🔎</div><div class="state-text">Nenhum resultado.</div></div>`;
    return;
  }
  if (trilhasCache.length === 0) {
    container.innerHTML = `
      <div class="state" style="grid-column: 1/-1;"><div class="state-icon">🎯</div><div class="state-text">Nenhuma trilha cadastrada ainda.</div></div>
      <div class="card card-new" onclick="abrirFormTrilha()"><div class="card-new-inner"><div class="card-new-plus">+</div><div class="card-new-label">Nova Trilha</div></div></div>`;
    return;
  }

  let html = "";
  for (const t of filtradas) {
    const cls = t.ativa ? "" : "inativa";
    const tipoClass = t.tipo || "outro";
    const totalEtapas = t.etapas ? t.etapas.length : 0;
    html += `
      <div class="trilha-card ${cls}" onclick="abrirDetalhesTrilha('${t.id}')">
        <div class="trilha-titulo">
          ${t.nome}
          ${!t.ativa ? '<span class="card-tag" style="background:rgba(245,158,11,0.15);color:var(--warning);">INATIVA</span>' : ""}
        </div>
        ${t.descricao ? `<div class="trilha-meta">${t.descricao}</div>` : ""}
        <div class="trilha-badges">
          <span class="trilha-badge ${tipoClass}">${TIPO_TRILHA_LABEL[t.tipo] || t.tipo}</span>
          <span class="trilha-badge outro">${totalEtapas} etapa${totalEtapas !== 1 ? "s" : ""}</span>
          <span class="trilha-badge outro">${t.total_progressos || 0} pessoa${(t.total_progressos || 0) !== 1 ? "s" : ""}</span>
          ${t.total_concluidos > 0 ? `<span class="trilha-badge discipulado">${t.total_concluidos} concluída${t.total_concluidos !== 1 ? "s" : ""}</span>` : ""}
        </div>
      </div>
    `;
  }
  html += `<div class="card card-new" onclick="abrirFormTrilha()"><div class="card-new-inner"><div class="card-new-plus">+</div><div class="card-new-label">Nova Trilha</div></div></div>`;
  container.innerHTML = html;
}

// ============ BUILDER DE ETAPAS ============

function adicionarEtapa(nome = "", obrigatoria = true) {
  const builder = document.getElementById("etapas-builder");
  const div = document.createElement("div");
  div.className = "etapa-builder";
  div.innerHTML = `
    <input type="text" placeholder="Nome da etapa" value="${nome}" data-field="nome" required>
    <label style="display:flex; align-items:center; gap:6px; font-size:12px; color:var(--text-muted); white-space:nowrap;">
      <input type="checkbox" data-field="obrigatoria" ${obrigatoria ? "checked" : ""}>
      Obrigatória
    </label>
    <button type="button" class="btn-remove" onclick="this.parentElement.remove(); reordenarEtapas();">✕</button>
  `;
  builder.appendChild(div);
  reordenarEtapas();
}

function reordenarEtapas() {
  const builders = document.querySelectorAll("#etapas-builder .etapa-builder");
  builders.forEach((b, i) => {
    // Atualiza a ordem visualmente (opcional — não precisa setar dado)
  });
}

function coletarEtapas() {
  const builders = document.querySelectorAll("#etapas-builder .etapa-builder");
  const etapas = [];
  builders.forEach((b, i) => {
    const nome = b.querySelector('[data-field="nome"]').value.trim();
    const obrigatoria = b.querySelector('[data-field="obrigatoria"]').checked;
    if (nome) {
      etapas.push({
        ordem: i + 1,
        nome,
        obrigatoria,
      });
    }
  });
  return etapas;
}

function limparEtapas() {
  document.getElementById("etapas-builder").innerHTML = "";
}

// ============ CRUD TRILHA ============

function abrirFormTrilha(trilha = null) {
  document.getElementById("form-trilha").reset();
  limparEtapas();
  const t = document.getElementById("form-trilha-titulo");
  const b = document.getElementById("btn-salvar-trilha");

  if (trilha) {
    t.textContent = "Editar Trilha"; b.textContent = "Salvar Alterações";
    document.getElementById("form-trilha-id").value = trilha.id;
    document.querySelector('#form-trilha [name="nome"]').value = trilha.nome || "";
    document.querySelector('#form-trilha [name="descricao"]').value = trilha.descricao || "";
    document.querySelector('#form-trilha [name="tipo"]').value = trilha.tipo || "discipulado";
    // Preenche etapas
    if (trilha.etapas && trilha.etapas.length > 0) {
      trilha.etapas.forEach(e => adicionarEtapa(e.nome, e.obrigatoria));
    } else {
      adicionarEtapa();
    }
  } else {
    t.textContent = "Nova Trilha"; b.textContent = "Criar Trilha";
    document.getElementById("form-trilha-id").value = "";
    // Adiciona uma etapa em branco para começar
    adicionarEtapa();
  }

  document.getElementById("modal-form-trilha").classList.add("active");
  document.querySelector('#form-trilha [name="nome"]').focus();
}

function fecharFormTrilha() { document.getElementById("modal-form-trilha").classList.remove("active"); }

async function salvarTrilha(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-trilha");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";
  const form = new FormData(e.target);
  const dados = {
    nome: document.querySelector('#form-trilha [name="nome"]').value.trim(),
    descricao: document.querySelector('#form-trilha [name="descricao"]').value.trim() || null,
    tipo: document.querySelector('#form-trilha [name="tipo"]').value,
  };
  const etapas = coletarEtapas();
  const id = document.getElementById("form-trilha-id").value;

  if (!id && etapas.length === 0) {
    mostrarToast("❌ Adicione pelo menos 1 etapa", "error");
    btn.disabled = false; btn.textContent = txt;
    return;
  }

  if (!id) dados.etapas = etapas;

  const url = id ? `${API}/jornada/trilhas/${id}` : `${API}/jornada/trilhas/`;
  const metodo = id ? "PUT" : "POST";
  try {
    const r = await apiFetch(url, { method: metodo, headers: {"Content-Type":"application/json"}, body: JSON.stringify(dados) });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormTrilha();
    mostrarToast(id ? "✅ Trilha atualizada!" : "✅ Trilha criada!", "success");
    carregarTrilhas();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

function abrirDetalhesTrilha(id) {
  const t = trilhasCache.find(x => x.id === id); if (!t) return;
  trilhaAtual = t;
  document.getElementById("detalhe-trilha-titulo").textContent = t.nome;

  const linhas = [
    ["Tipo", TIPO_TRILHA_LABEL[t.tipo] || t.tipo],
    ["Descrição", t.descricao],
    ["Pessoas fazendo", String(t.total_progressos || 0)],
    ["Concluídas", String(t.total_concluidos || 0)],
    ["Situação", t.ativa ? "Ativa" : "Inativa"],
    ["Criada em", new Date(t.created_at).toLocaleString("pt-BR")],
  ].filter(([,v]) => v);

  document.getElementById("detalhe-trilha-corpo").innerHTML = linhas.map(([k,v])=>`<div class="detail-row"><div class="detail-label">${k}</div><div class="detail-value">${v}</div></div>`).join("");

  // Etapas
  const divEtapas = document.getElementById("detalhe-trilha-etapas");
  if (!t.etapas || t.etapas.length === 0) {
    divEtapas.innerHTML = `<div class="state" style="padding:20px;"><div class="state-text">Nenhuma etapa.</div></div>`;
  } else {
    divEtapas.innerHTML = t.etapas.map(e => `
      <div class="etapa-item">
        <div class="etapa-ordem">${e.ordem}</div>
        <div class="etapa-corpo">
          <div class="etapa-nome">${e.nome}</div>
          ${e.descricao ? `<div class="etapa-desc">${e.descricao}</div>` : ""}
        </div>
        <span class="etapa-tag ${e.obrigatoria ? 'obrigatoria' : 'opcional'}">${e.obrigatoria ? 'OBRIGATÓRIA' : 'OPCIONAL'}</span>
      </div>
    `).join("");
  }

  const b = document.getElementById("btn-toggle-trilha");
  if (t.ativa) { b.textContent = "Desativar"; b.className = "btn btn-warning"; }
  else { b.textContent = "Reativar"; b.className = "btn btn-success"; }

  document.getElementById("modal-detalhes-trilha").classList.add("active");
}

function fecharDetalhesTrilha() { document.getElementById("modal-detalhes-trilha").classList.remove("active"); trilhaAtual = null; }
function editarTrilhaDoDetalhe() { if (!trilhaAtual) return; const t = trilhaAtual; fecharDetalhesTrilha(); abrirFormTrilha(t); }

function confirmarDeletarTrilha() {
  if (!trilhaAtual) return;
  const t = trilhaAtual;
  abrirConfirmar("Excluir trilha?", `Tem certeza que deseja EXCLUIR "${t.nome}"? Se houver pessoas fazendo, a exclusão será bloqueada.`, async () => {
    try {
      const r = await apiFetch(`${API}/jornada/trilhas/${t.id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      fecharDetalhesTrilha(); mostrarToast("✅ Trilha excluída.", "success"); carregarTrilhas();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

function toggleAtivaTrilha() {
  if (!trilhaAtual) return;
  const t = trilhaAtual; const acao = t.ativa ? "desativar" : "reativar";
  abrirConfirmar(t.ativa ? "Desativar trilha?" : "Reativar trilha?", t.ativa ? `"${t.nome}" ficará inativa.` : `"${t.nome}" voltará a ficar ativa.`, async () => {
    try {
      const r = await apiFetch(`${API}/jornada/trilhas/${t.id}/${acao}`, { method: "PATCH" });
      if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      fecharDetalhesTrilha(); mostrarToast(t.ativa ? "✅ Trilha desativada." : "✅ Trilha reativada.", "success"); carregarTrilhas();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}
'''

if "// ============ JORNADA ============" not in conteudo:
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
  const contJornada = document.getElementById("conteudo-jornada");
  if (contJornada) contJornada.style.display = nome === "jornada" ? "block" : "none";
  document.getElementById("conteudo-usuarios").style.display = nome === "usuarios" ? "block" : "none";
  if (nome === "inicio") { carregarDashboard(); }
  else if (nome === "pessoas") { carregarSelectIgrejas(); carregarPessoas(); }
  else if (nome === "cuidado") { carregarAcompanhamentos(); }
  else if (nome === "oracao") { carregarOracoes(); }
  else if (nome === "eventos") { carregarEventos(); }
  else if (nome === "jornada") { carregarTrilhas(); }
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