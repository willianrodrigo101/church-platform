"""Frontend do modulo Estudo — Bloco 1: Trilhas, Cursos, Modulos e Conteudos."""
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
  /* ============ ESTUDO ============ */
  .estudo-trilha-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 24px;
    transition: all 0.2s; cursor: pointer;
    position: relative; overflow: hidden;
  }
  .estudo-trilha-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .estudo-trilha-card.inativa { opacity: 0.6; }
  .estudo-trilha-icon {
    width: 56px; height: 56px;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    border-radius: 16px;
    display: grid; place-items: center;
    font-size: 26px; margin-bottom: 14px;
  }
  .estudo-trilha-titulo { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
  .estudo-trilha-meta { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }
  .estudo-badge {
    font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 999px;
    letter-spacing: 0.3px;
    display: inline-block;
  }
  .estudo-badge.iniciante     { background: rgba(16,185,129,0.15); color: #34d399; }
  .estudo-badge.basico        { background: rgba(99,102,241,0.15); color: #818cf8; }
  .estudo-badge.intermediario { background: rgba(245,158,11,0.15); color: #fbbf24; }
  .estudo-badge.avancado      { background: rgba(236,72,153,0.15); color: #f472b6; }
  .estudo-badge.bacharelado   { background: rgba(139,92,246,0.15); color: #a78bfa; }
  .estudo-badge.tipo          { background: rgba(139,149,168,0.15); color: var(--text-muted); }

  .estudo-curso-card {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px;
    transition: all 0.15s; cursor: pointer;
    display: flex; gap: 14px; align-items: flex-start;
  }
  .estudo-curso-card:hover { border-color: var(--accent); background: var(--bg-card-hover); }
  .estudo-curso-card.inativo { opacity: 0.6; }
  .estudo-curso-icon {
    width: 44px; height: 44px;
    background: rgba(99,102,241,0.15);
    border-radius: 12px;
    display: grid; place-items: center;
    font-size: 20px; flex-shrink: 0;
  }
  .estudo-curso-corpo { flex: 1; min-width: 0; }
  .estudo-curso-titulo { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
  .estudo-curso-meta { font-size: 12px; color: var(--text-muted); }
  .estudo-curso-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }

  /* Modulos e conteudos */
  .modulo-item {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px 16px;
    margin-bottom: 10px;
  }
  .modulo-header {
    display: flex; justify-content: space-between; align-items: center; gap: 12px;
  }
  .modulo-ordem {
    width: 30px; height: 30px;
    background: rgba(99,102,241,0.15); color: var(--accent);
    border-radius: 50%; display: grid; place-items: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0;
  }
  .modulo-titulo { font-size: 14px; font-weight: 600; }
  .modulo-meta { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
  .conteudo-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; margin-top: 6px; margin-left: 42px;
    background: var(--bg-card);
    border-radius: 8px; font-size: 13px;
  }
  .conteudo-tipo-icon {
    width: 24px; height: 24px;
    display: grid; place-items: center;
    font-size: 14px; flex-shrink: 0;
  }

  /* Builder de modulos/conteudos */
  .modulo-builder {
    background: var(--bg);
    border: 1px dashed var(--border);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 12px;
  }
  .modulo-builder-header {
    display: flex; gap: 8px; align-items: center; margin-bottom: 10px;
  }
  .modulo-builder input[type="text"],
  .modulo-builder input[type="number"],
  .modulo-builder textarea,
  .modulo-builder select {
    width: 100%; padding: 8px 12px;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 8px; color: var(--text);
    font-size: 13px; font-family: inherit;
  }
  .modulo-builder input:focus, .modulo-builder textarea:focus { outline: none; border-color: var(--accent); }
  .conteudo-builder {
    display: flex; gap: 6px; align-items: center;
    padding: 8px; margin-bottom: 6px;
    background: var(--bg-card); border-radius: 8px;
  }
  .conteudo-builder input, .conteudo-builder select {
    padding: 6px 10px; font-size: 12px;
  }
  .btn-icon {
    background: transparent; border: none; cursor: pointer;
    padding: 4px 8px; border-radius: 6px; color: var(--text-muted);
    font-size: 14px;
  }
  .btn-icon:hover { background: var(--border); color: var(--text); }
  .btn-icon.danger:hover { color: var(--danger); }
'''

if ".estudo-trilha-card" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Aba no nav (depois de Jornada)
# ============================================================
aba_nav = '<button class="tab" data-tab="estudo" onclick="trocarAba(\'estudo\')">📚 Estudo</button>'
marcador_nav = '<button class="tab" data-tab="usuarios" onclick="trocarAba(\'usuarios\')" id="tab-usuarios" style="display:none;">👤 Usuários</button>'

if 'data-tab="estudo"' not in conteudo and marcador_nav in conteudo:
    conteudo = conteudo.replace(marcador_nav, aba_nav + "\n    " + marcador_nav, 1)

# ============================================================
# 3. HTML da aba
# ============================================================
html_aba = '''
    <!-- ABA ESTUDO -->
    <div id="conteudo-estudo" style="display: none;">
      <h1 class="page-title">📚 Estudo</h1>
      <p class="page-subtitle">Trilhas de formação teológica do iniciante ao bacharelado</p>

      <div id="estudo-alertas" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px;"></div>

      <div class="toolbar" style="margin-bottom: 24px;">
        <input type="text" class="toolbar-search" id="busca-trilha-estudo" placeholder="🔎 Buscar trilha..." oninput="renderizarTrilhasEstudo()">
        <select class="toolbar-select" id="filtro-nivel-estudo" onchange="carregarTrilhasEstudo()">
          <option value="">Todos os níveis</option>
          <option value="iniciante">Iniciante</option>
          <option value="basico">Básico</option>
          <option value="intermediario">Intermediário</option>
          <option value="avancado">Avançado</option>
          <option value="bacharelado">Bacharelado</option>
        </select>
        <button class="btn btn-primary" onclick="abrirFormTrilhaEstudo()">+ Nova Trilha</button>
        <button class="btn btn-primary" onclick="abrirFormCursoEstudo()">+ Novo Curso</button>
        <div class="toolbar-count" id="contador-trilhas-estudo"></div>
      </div>

      <div id="container-trilhas-estudo" class="grid"></div>
    </div>
'''

if 'id="conteudo-estudo"' not in conteudo:
    marcador = "  </main>"
    conteudo = conteudo.replace(marcador, html_aba + marcador, 1)

# ============================================================
# 4. Modais
# ============================================================
modais = '''
<!-- Trilha Estudo: form -->
<div class="modal-backdrop" id="modal-form-trilha-estudo">
  <div class="modal">
    <div class="modal-header">
      <h2 class="modal-title" id="form-trilha-estudo-titulo">Nova Trilha</h2>
      <button class="modal-close" onclick="fecharFormTrilhaEstudo()">×</button>
    </div>
    <form id="form-trilha-estudo" onsubmit="salvarTrilhaEstudo(event)">
      <input type="hidden" id="form-trilha-estudo-id">
      <div class="form-group">
        <label class="form-label">Nome *</label>
        <input class="form-input" name="nome" required minlength="2" placeholder="Formação Ministerial">
      </div>
      <div class="form-group">
        <label class="form-label">Descrição</label>
        <textarea class="form-input" name="descricao" rows="2" style="font-family: inherit; resize: vertical;"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Nível *</label>
          <select class="form-select" name="nivel" required>
            <option value="iniciante">Iniciante</option>
            <option value="basico">Básico</option>
            <option value="intermediario">Intermediário</option>
            <option value="avancado">Avançado</option>
            <option value="bacharelado">Bacharelado</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Ícone (emoji)</label>
          <input class="form-input" name="icone" maxlength="4" placeholder="📖">
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormTrilhaEstudo()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-trilha-estudo">Criar Trilha</button>
      </div>
    </form>
  </div>
</div>

<!-- Trilha Estudo: detalhes -->
<div class="modal-backdrop" id="modal-detalhes-trilha-estudo">
  <div class="modal" style="max-width: 720px;">
    <div class="modal-header">
      <h2 class="modal-title" id="detalhe-trilha-estudo-titulo">Trilha</h2>
      <button class="modal-close" onclick="fecharDetalhesTrilhaEstudo()">×</button>
    </div>
    <div id="detalhe-trilha-estudo-corpo"></div>
    <div style="font-size:14px; font-weight:700; margin:20px 0 12px;">Cursos nesta trilha</div>
    <div id="detalhe-trilha-estudo-cursos"></div>
    <div class="modal-actions modal-actions-3" style="margin-top: 20px;">
      <button class="btn btn-ghost" onclick="fecharDetalhesTrilhaEstudo()">Fechar</button>
      <button class="btn btn-primary" onclick="editarTrilhaEstudoDoDetalhe()">Editar</button>
      <button class="btn btn-danger" onclick="confirmarDeletarTrilhaEstudo()">Deletar</button>
    </div>
    <div class="modal-actions" style="margin-top: 8px;">
      <button class="btn btn-warning" id="btn-toggle-trilha-estudo" onclick="toggleAtivaTrilhaEstudo()">Desativar</button>
    </div>
  </div>
</div>

<!-- Curso Estudo: form -->
<div class="modal-backdrop" id="modal-form-curso-estudo">
  <div class="modal" style="max-width: 800px;">
    <div class="modal-header">
      <h2 class="modal-title" id="form-curso-estudo-titulo">Novo Curso</h2>
      <button class="modal-close" onclick="fecharFormCursoEstudo()">×</button>
    </div>
    <form id="form-curso-estudo" onsubmit="salvarCursoEstudo(event)">
      <input type="hidden" id="form-curso-estudo-id">
      <div class="form-group">
        <label class="form-label">Nome *</label>
        <input class="form-input" name="nome" required minlength="2" placeholder="Teologia Sistemática I">
      </div>
      <div class="form-group">
        <label class="form-label">Descrição</label>
        <textarea class="form-input" name="descricao" rows="2" style="font-family: inherit; resize: vertical;"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Tipo *</label>
          <select class="form-select" name="tipo" required>
            <option value="teologia">Teologia</option>
            <option value="biblico">Bíblico</option>
            <option value="sistematico">Sistemático</option>
            <option value="historico">Histórico</option>
            <option value="pratico">Prático</option>
            <option value="linguas">Línguas (Grego/Hebraico)</option>
            <option value="artes">Artes (Canto, Dança, Oratória)</option>
            <option value="ministerial">Ministerial</option>
            <option value="outro">Outro</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Nível *</label>
          <select class="form-select" name="nivel" required>
            <option value="iniciante">Iniciante</option>
            <option value="basico">Básico</option>
            <option value="intermediario">Intermediário</option>
            <option value="avancado">Avançado</option>
            <option value="bacharelado">Bacharelado</option>
          </select>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Trilha</label>
          <select class="form-select" name="trilha_id" id="select-trilha-curso">
            <option value="">Sem trilha</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Carga horária (h)</label>
          <input class="form-input" type="number" name="carga_horaria" min="0" placeholder="60">
        </div>
      </div>

      <div style="margin: 20px 0 12px; display:flex; justify-content:space-between; align-items:center;">
        <label class="form-label" style="margin:0;">Módulos</label>
        <button type="button" class="btn btn-ghost" style="padding:6px 12px; font-size:12px;" onclick="adicionarModuloEstudo()">+ Adicionar módulo</button>
      </div>
      <div id="modulos-builder"></div>

      <div class="modal-actions" style="margin-top: 20px;">
        <button type="button" class="btn btn-ghost" onclick="fecharFormCursoEstudo()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-curso-estudo">Criar Curso</button>
      </div>
    </form>
  </div>
</div>
'''

if 'id="modal-form-trilha-estudo"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)

# ============================================================
# 5. JS
# ============================================================
js = '''
// ============ ESTUDO ============
let trilhasEstudoCache = [];
let cursosEstudoCache = [];
let trilhaEstudoAtual = null;

const NIVEL_LABEL = {
  iniciante: "Iniciante",
  basico: "Básico",
  intermediario: "Intermediário",
  avancado: "Avançado",
  bacharelado: "Bacharelado",
};

const TIPO_CURSO_LABEL = {
  teologia: "📖 Teologia",
  biblico: "📜 Bíblico",
  sistematico: "🧠 Sistemático",
  historico: "🏛️ Histórico",
  pratico: "⚙️ Prático",
  linguas: "🔤 Línguas",
  artes: "🎨 Artes",
  ministerial: "⛪ Ministerial",
  outro: "📌 Outro",
};

const TIPO_CONTEUDO_ICON = {
  video: "🎬",
  pdf: "📄",
  audio: "🎧",
  texto: "📝",
  link: "🔗",
  imagem: "🖼️",
  slides: "📊",
};

async function carregarTrilhasEstudo() {
  const container = document.getElementById("container-trilhas-estudo");
  if (!container) return;
  container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⏳</div><div class="state-text">Carregando trilhas...</div></div>`;

  const nivel = document.getElementById("filtro-nivel-estudo").value;
  const params = new URLSearchParams();
  if (nivel) params.append("nivel", nivel);

  try {
    const [r1, r2] = await Promise.all([
      apiFetch(`${API}/estudo/trilhas/?${params}`),
      apiFetch(`${API}/estudo/cursos/`),
    ]);
    trilhasEstudoCache = await r1.json();
    cursosEstudoCache = await r2.json();
    renderizarTrilhasEstudo();
    carregarAlertasEstudo();
  } catch (e) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⚠️</div><div class="state-text">${e.message}</div></div>`;
  }
}

async function carregarAlertasEstudo() {
  const div = document.getElementById("estudo-alertas");
  if (!div) return;
  try {
    const r = await apiFetch(`${API}/estudo/dashboard`);
    const d = await r.json();
    const cards = [
      { label: "Trilhas", valor: d.total_trilhas, cor: "var(--accent)", icon: "📚" },
      { label: "Cursos", valor: d.total_cursos, cor: "var(--accent)", icon: "📖" },
      { label: "Módulos", valor: d.total_modulos, cor: "var(--warning)", icon: "📋" },
      { label: "Conteúdos", valor: d.total_conteudos || 0, cor: "var(--success)", icon: "🎬" },
    ];
    div.innerHTML = cards.map(c => `
      <div class="card" style="cursor: default;">
        <div style="font-size: 22px; margin-bottom: 6px;">${c.icon}</div>
        <div style="font-size: 26px; font-weight: 700; color: ${c.cor};">${c.valor}</div>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">${c.label}</div>
      </div>
    `).join("");
  } catch (e) { /* silencioso */ }
}

function renderizarTrilhasEstudo() {
  const container = document.getElementById("container-trilhas-estudo");
  const contador = document.getElementById("contador-trilhas-estudo");
  const busca = document.getElementById("busca-trilha-estudo").value.toLowerCase().trim();

  const filtradas = trilhasEstudoCache.filter(t => {
    if (!busca) return true;
    return (t.nome || "").toLowerCase().includes(busca);
  });

  const total = trilhasEstudoCache.length;
  contador.textContent = `${total} trilha${total !== 1 ? "s" : ""}`;

  if (trilhasEstudoCache.length === 0) {
    container.innerHTML = `
      <div class="state" style="grid-column: 1/-1;"><div class="state-icon">📚</div><div class="state-text">Nenhuma trilha criada ainda.<br>Comece criando uma trilha ou um curso.</div></div>`;
    return;
  }

  let html = "";
  for (const t of filtradas) {
    const cls = t.ativa ? "" : "inativa";
    const cursos = cursosEstudoCache.filter(c => c.trilha_id === t.id);
    const icone = t.icone || "📖";
    html += `
      <div class="estudo-trilha-card ${cls}" onclick="abrirDetalhesTrilhaEstudo('${t.id}')">
        <div class="estudo-trilha-icon">${icone}</div>
        <div class="estudo-trilha-titulo">${t.nome}</div>
        ${t.descricao ? `<div class="estudo-trilha-meta">${t.descricao}</div>` : ""}
        <div style="display:flex; gap:6px; flex-wrap:wrap;">
          <span class="estudo-badge ${t.nivel}">${NIVEL_LABEL[t.nivel] || t.nivel}</span>
          <span class="estudo-badge tipo">${cursos.length} curso${cursos.length !== 1 ? "s" : ""}</span>
          ${!t.ativa ? '<span class="estudo-badge tipo" style="background:rgba(245,158,11,0.15);color:var(--warning);">INATIVA</span>' : ""}
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
}

// ============ TRILHA — CRUD ============

function abrirFormTrilhaEstudo(trilha = null) {
  document.getElementById("form-trilha-estudo").reset();
  const t = document.getElementById("form-trilha-estudo-titulo");
  const b = document.getElementById("btn-salvar-trilha-estudo");

  if (trilha) {
    t.textContent = "Editar Trilha"; b.textContent = "Salvar Alterações";
    document.getElementById("form-trilha-estudo-id").value = trilha.id;
    document.querySelector('#form-trilha-estudo [name="nome"]').value = trilha.nome || "";
    document.querySelector('#form-trilha-estudo [name="descricao"]').value = trilha.descricao || "";
    document.querySelector('#form-trilha-estudo [name="nivel"]').value = trilha.nivel || "iniciante";
    document.querySelector('#form-trilha-estudo [name="icone"]').value = trilha.icone || "";
  } else {
    t.textContent = "Nova Trilha"; b.textContent = "Criar Trilha";
    document.getElementById("form-trilha-estudo-id").value = "";
  }

  document.getElementById("modal-form-trilha-estudo").classList.add("active");
  document.querySelector('#form-trilha-estudo [name="nome"]').focus();
}

function fecharFormTrilhaEstudo() {
  document.getElementById("modal-form-trilha-estudo").classList.remove("active");
}

async function salvarTrilhaEstudo(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-trilha-estudo");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";
  const dados = {};
  for (const [k, v] of new FormData(e.target).entries()) {
    if (k === "id") continue;
    if (typeof v === "string" && v.trim()) dados[k] = v.trim();
  }
  const id = document.getElementById("form-trilha-estudo-id").value;
  const url = id ? `${API}/estudo/trilhas/${id}` : `${API}/estudo/trilhas/`;
  const metodo = id ? "PUT" : "POST";
  try {
    const r = await apiFetch(url, { method: metodo, headers: {"Content-Type":"application/json"}, body: JSON.stringify(dados) });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormTrilhaEstudo();
    mostrarToast(id ? "✅ Trilha atualizada!" : "✅ Trilha criada!", "success");
    carregarTrilhasEstudo();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

function abrirDetalhesTrilhaEstudo(id) {
  const t = trilhasEstudoCache.find(x => x.id === id); if (!t) return;
  trilhaEstudoAtual = t;
  document.getElementById("detalhe-trilha-estudo-titulo").textContent = t.nome;

  const linhas = [
    ["Descrição", t.descricao],
    ["Nível", NIVEL_LABEL[t.nivel] || t.nivel],
    ["Situação", t.ativa ? "Ativa" : "Inativa"],
    ["Criada em", new Date(t.created_at).toLocaleString("pt-BR")],
  ].filter(([,v]) => v);

  document.getElementById("detalhe-trilha-estudo-corpo").innerHTML = linhas.map(([k,v])=>`<div class="detail-row"><div class="detail-label">${k}</div><div class="detail-value">${v}</div></div>`).join("");

  const cursos = cursosEstudoCache.filter(c => c.trilha_id === t.id);
  const divCursos = document.getElementById("detalhe-trilha-estudo-cursos");
  if (cursos.length === 0) {
    divCursos.innerHTML = `<div class="state" style="padding:20px;"><div class="state-text">Nenhum curso vinculado.</div></div>`;
  } else {
    divCursos.innerHTML = cursos.map(c => `
      <div class="estudo-curso-card" style="margin-bottom:8px;" onclick="event.stopPropagation(); abrirFormCursoEstudo(${JSON.stringify(c).replace(/"/g, '&quot;')})">
        <div class="estudo-curso-icon">${TIPO_CONTEUDO_ICON.video}</div>
        <div class="estudo-curso-corpo">
          <div class="estudo-curso-titulo">${c.nome}</div>
          <div class="estudo-curso-meta">${c.carga_horaria ? c.carga_horaria + "h · " : ""}${(c.modulos || []).length} módulo(s)</div>
        </div>
      </div>
    `).join("");
  }

  const b = document.getElementById("btn-toggle-trilha-estudo");
  if (t.ativa) { b.textContent = "Desativar"; b.className = "btn btn-warning"; }
  else { b.textContent = "Reativar"; b.className = "btn btn-success"; }

  document.getElementById("modal-detalhes-trilha-estudo").classList.add("active");
}

function fecharDetalhesTrilhaEstudo() {
  document.getElementById("modal-detalhes-trilha-estudo").classList.remove("active");
  trilhaEstudoAtual = null;
}

function editarTrilhaEstudoDoDetalhe() {
  if (!trilhaEstudoAtual) return;
  const t = trilhaEstudoAtual;
  fecharDetalhesTrilhaEstudo();
  abrirFormTrilhaEstudo(t);
}

function confirmarDeletarTrilhaEstudo() {
  if (!trilhaEstudoAtual) return;
  const t = trilhaEstudoAtual;
  abrirConfirmar("Excluir trilha?", `Tem certeza que deseja EXCLUIR "${t.nome}"? Se houver cursos vinculados, a exclusão será bloqueada.`, async () => {
    try {
      const r = await apiFetch(`${API}/estudo/trilhas/${t.id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      fecharDetalhesTrilhaEstudo(); mostrarToast("✅ Trilha excluída.", "success"); carregarTrilhasEstudo();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

function toggleAtivaTrilhaEstudo() {
  if (!trilhaEstudoAtual) return;
  const t = trilhaEstudoAtual; const acao = t.ativa ? "desativar" : "reativar";
  abrirConfirmar(t.ativa ? "Desativar trilha?" : "Reativar trilha?", t.ativa ? `"${t.nome}" ficará inativa.` : `"${t.nome}" voltará a ficar ativa.`, async () => {
    try {
      const r = await apiFetch(`${API}/estudo/trilhas/${t.id}/${acao}`, { method: "PATCH" });
      if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      fecharDetalhesTrilhaEstudo(); mostrarToast(t.ativa ? "✅ Trilha desativada." : "✅ Trilha reativada.", "success"); carregarTrilhasEstudo();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

// ============ CURSO — CRUD ============

async function carregarSelectTrilhas() {
  try {
    const sel = document.getElementById("select-trilha-curso");
    sel.innerHTML = '<option value="">Sem trilha</option>' +
      trilhasEstudoCache.map(t => `<option value="${t.id}">${t.icone || "📖"} ${t.nome}</option>`).join("");
  } catch (e) { /* silencioso */ }
}

function abrirFormCursoEstudo(curso = null) {
  document.getElementById("form-curso-estudo").reset();
  document.getElementById("modulos-builder").innerHTML = "";
  const t = document.getElementById("form-curso-estudo-titulo");
  const b = document.getElementById("btn-salvar-curso-estudo");

  carregarSelectTrilhas();

  if (curso) {
    t.textContent = "Editar Curso"; b.textContent = "Salvar Alterações";
    document.getElementById("form-curso-estudo-id").value = curso.id;
    document.querySelector('#form-curso-estudo [name="nome"]').value = curso.nome || "";
    document.querySelector('#form-curso-estudo [name="descricao"]').value = curso.descricao || "";
    document.querySelector('#form-curso-estudo [name="tipo"]').value = curso.tipo || "teologia";
    document.querySelector('#form-curso-estudo [name="nivel"]').value = curso.nivel || "iniciante";
    document.querySelector('#form-curso-estudo [name="carga_horaria"]').value = curso.carga_horaria || "";
    setTimeout(() => {
      document.getElementById("select-trilha-curso").value = curso.trilha_id || "";
    }, 100);
    // Carrega módulos
    (curso.modulos || []).forEach(m => adicionarModuloEstudo(m));
  } else {
    t.textContent = "Novo Curso"; b.textContent = "Criar Curso";
    document.getElementById("form-curso-estudo-id").value = "";
    adicionarModuloEstudo(); // módulo em branco
  }

  document.getElementById("modal-form-curso-estudo").classList.add("active");
  document.querySelector('#form-curso-estudo [name="nome"]').focus();
}

function fecharFormCursoEstudo() {
  document.getElementById("modal-form-curso-estudo").classList.remove("active");
}

function adicionarModuloEstudo(modulo = null) {
  const builder = document.getElementById("modulos-builder");
  const div = document.createElement("div");
  div.className = "modulo-builder";
  div.innerHTML = `
    <div class="modulo-builder-header">
      <input type="text" placeholder="Título do módulo" value="${modulo?.titulo || ''}" data-field="titulo" required>
      <button type="button" class="btn-icon danger" onclick="this.closest('.modulo-builder').remove()">✕</button>
    </div>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-bottom:10px;">
      <input type="number" placeholder="Duração (min)" value="${modulo?.duracao_minutos || ''}" data-field="duracao_minutos" min="0">
      <select data-field="obrigatorio">
        <option value="true" ${modulo?.obrigatorio !== false ? "selected" : ""}>Obrigatório</option>
        <option value="false" ${modulo?.obrigatorio === false ? "selected" : ""}>Opcional</option>
      </select>
    </div>
    <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px; display:flex; justify-content:space-between;">
      <span>Conteúdos</span>
      <button type="button" class="btn-icon" onclick="adicionarConteudo(this)" style="font-size:11px;">+ adicionar</button>
    </div>
    <div class="conteudos-builder"></div>
  `;
  builder.appendChild(div);

  // Se veio com conteudos, adiciona
  if (modulo?.conteudos) {
    const contBuilder = div.querySelector(".conteudos-builder");
    modulo.conteudos.forEach(c => adicionarConteudo(div.querySelector('.modulo-builder-header button[type="button"] + *'), c));
  }
}

function adicionarConteudo(btnElement, conteudo = null) {
  // Encontra o builder pai
  let parent = btnElement.parentElement;
  while (parent && !parent.classList.contains("modulo-builder")) {
    parent = parent.parentElement;
  }
  if (!parent) return;
  const contBuilder = parent.querySelector(".conteudos-builder");
  const div = document.createElement("div");
  div.className = "conteudo-builder";
  div.innerHTML = `
    <select data-field="tipo" style="width:110px;">
      <option value="texto" ${conteudo?.tipo === "texto" ? "selected" : ""}>📝 Texto</option>
      <option value="video" ${conteudo?.tipo === "video" ? "selected" : ""}>🎬 Vídeo</option>
      <option value="pdf" ${conteudo?.tipo === "pdf" ? "selected" : ""}>📄 PDF</option>
      <option value="audio" ${conteudo?.tipo === "audio" ? "selected" : ""}>🎧 Áudio</option>
      <option value="link" ${conteudo?.tipo === "link" ? "selected" : ""}>🔗 Link</option>
      <option value="imagem" ${conteudo?.tipo === "imagem" ? "selected" : ""}>🖼️ Imagem</option>
      <option value="slides" ${conteudo?.tipo === "slides" ? "selected" : ""}>📊 Slides</option>
    </select>
    <input type="text" placeholder="Título" value="${conteudo?.titulo || ''}" data-field="titulo" style="flex:1;">
    <input type="text" placeholder="URL ou conteúdo" value="${conteudo?.url || conteudo?.texto || ''}" data-field="url" style="flex:2;">
    <button type="button" class="btn-icon danger" onclick="this.parentElement.remove()">✕</button>
  `;
  contBuilder.appendChild(div);
}

function coletarModulosEstudo() {
  const builders = document.querySelectorAll("#modulos-builder .modulo-builder");
  const modulos = [];
  builders.forEach((b, i) => {
    const titulo = b.querySelector('[data-field="titulo"]').value.trim();
    if (!titulo) return;
    const duracao = b.querySelector('[data-field="duracao_minutos"]').value;
    const obrig = b.querySelector('[data-field="obrigatorio"]').value === "true";

    const conteudos = [];
    b.querySelectorAll(".conteudo-builder").forEach((c, j) => {
      const tipo = c.querySelector('[data-field="tipo"]').value;
      const ctitulo = c.querySelector('[data-field="titulo"]').value.trim();
      const url = c.querySelector('[data-field="url"]').value.trim();
      if (!ctitulo) return;
      const item = { ordem: j+1, tipo, titulo: ctitulo };
      if (tipo === "texto") item.texto = url;
      else item.url = url;
      conteudos.push(item);
    });

    modulos.push({
      ordem: i + 1,
      titulo,
      duracao_minutos: duracao ? parseInt(duracao) : null,
      obrigatorio: obrig,
      conteudos,
    });
  });
  return modulos;
}

async function salvarCursoEstudo(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-curso-estudo");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";

  const id = document.getElementById("form-curso-estudo-id").value;
  const dados = {
    nome: document.querySelector('#form-curso-estudo [name="nome"]').value.trim(),
    descricao: document.querySelector('#form-curso-estudo [name="descricao"]').value.trim() || null,
    tipo: document.querySelector('#form-curso-estudo [name="tipo"]').value,
    nivel: document.querySelector('#form-curso-estudo [name="nivel"]').value,
    carga_horaria: parseInt(document.querySelector('#form-curso-estudo [name="carga_horaria"]').value) || null,
    trilha_id: document.getElementById("select-trilha-curso").value || null,
  };

  if (!id) {
    dados.modulos = coletarModulosEstudo();
  }

  const url = id ? `${API}/estudo/cursos/${id}` : `${API}/estudo/cursos/`;
  const metodo = id ? "PUT" : "POST";

  try {
    const r = await apiFetch(url, { method: metodo, headers: {"Content-Type":"application/json"}, body: JSON.stringify(dados) });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormCursoEstudo();
    mostrarToast(id ? "✅ Curso atualizado!" : "✅ Curso criado!", "success");
    carregarTrilhasEstudo();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}
'''

if "// ============ ESTUDO ============" not in conteudo:
    marcador = "// ============ NOTIFICACOES ============"
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
  const contEstudo = document.getElementById("conteudo-estudo");
  if (contEstudo) contEstudo.style.display = nome === "estudo" ? "block" : "none";
  document.getElementById("conteudo-usuarios").style.display = nome === "usuarios" ? "block" : "none";
  if (nome === "inicio") { carregarDashboard(); }
  else if (nome === "pessoas") { carregarSelectIgrejas(); carregarPessoas(); }
  else if (nome === "cuidado") { carregarAcompanhamentos(); }
  else if (nome === "oracao") { carregarOracoes(); }
  else if (nome === "eventos") { carregarEventos(); }
  else if (nome === "jornada") { carregarTrilhas(); }
  else if (nome === "estudo") { carregarTrilhasEstudo(); }
  else if (nome === "usuarios") { carregarIgrejasParaUsuario(); carregarUsuarios(); }
  else { carregarIgrejas(); }
}'''
conteudo = re.sub(r'function trocarAba\(nome\) \{.*?\n\}', novo_trocar, conteudo, count=1, flags=re.DOTALL)

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("Vá para a aba Estudo e crie uma trilha + curso.")
print("=" * 60)