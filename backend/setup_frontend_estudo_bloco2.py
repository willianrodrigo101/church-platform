"""Frontend do modulo Estudo — Bloco 2: Turmas, Matriculas, Presencas."""
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
  /* ============ TURMAS ============ */
  .turma-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 22px;
    transition: all 0.2s; cursor: pointer;
  }
  .turma-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .turma-card.inativa { opacity: 0.6; }
  .turma-titulo { font-size: 17px; font-weight: 700; margin-bottom: 4px; }
  .turma-meta { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
  .turma-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 12px; }
  .turma-badge {
    font-size: 11px; font-weight: 600;
    padding: 3px 10px; border-radius: 999px;
  }
  .turma-badge.planejada      { background: rgba(99,102,241,0.15); color: #818cf8; }
  .turma-badge.em_andamento   { background: rgba(16,185,129,0.15); color: #34d399; }
  .turma-badge.concluida      { background: rgba(139,149,168,0.15); color: var(--text-muted); }
  .turma-badge.cancelada      { background: rgba(239,68,68,0.15); color: var(--danger); }
  .turma-badge.presencial     { background: rgba(139,92,246,0.15); color: #a78bfa; }
  .turma-badge.online         { background: rgba(59,130,246,0.15); color: #60a5fa; }
  .turma-badge.hibrido        { background: rgba(236,72,153,0.15); color: #f472b6; }

  /* Alunos matriculados */
  .aluno-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 14px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; margin-bottom: 8px;
  }
  .aluno-avatar {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    border-radius: 10px; display: grid; place-items: center;
    font-size: 14px; font-weight: 700; color: white; flex-shrink: 0;
  }
  .aluno-corpo { flex: 1; min-width: 0; }
  .aluno-nome { font-size: 14px; font-weight: 600; }
  .aluno-meta { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
  .aluno-acoes { display: flex; gap: 6px; }

  .progresso-mini {
    width: 100%; height: 6px;
    background: var(--bg-card); border-radius: 999px;
    overflow: hidden; margin-top: 6px;
  }
  .progresso-mini-fill {
    height: 100%; background: linear-gradient(90deg, var(--accent), #8b5cf6);
    transition: width 0.3s ease;
  }

  /* Chamada */
  .chamada-lista {
    max-height: 400px; overflow-y: auto;
    border: 1px solid var(--border); border-radius: 10px; padding: 10px;
  }
  .chamada-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px;
    background: var(--bg); border-radius: 8px;
    margin-bottom: 6px;
  }
  .chamada-item input[type="checkbox"] {
    width: 20px; height: 20px; accent-color: var(--success);
    cursor: pointer;
  }
  .chamada-nome { font-size: 14px; font-weight: 600; }

  /* Abas internas */
  .estudo-sub-abas {
    display: flex; gap: 4px; margin-bottom: 24px;
    border-bottom: 1px solid var(--border);
  }
  .estudo-sub-aba {
    padding: 12px 20px; background: transparent; color: var(--text-muted);
    border: none; border-bottom: 2px solid transparent;
    font-size: 14px; font-weight: 600; font-family: inherit; cursor: pointer;
  }
  .estudo-sub-aba:hover { color: var(--text); }
  .estudo-sub-aba.ativa { color: var(--accent); border-bottom-color: var(--accent); }
'''

if ".turma-card" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Substituir o conteúdo da aba Estudo para incluir sub-abas
# ============================================================
old_estudo = '''    <!-- ABA ESTUDO -->
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
    </div>'''

new_estudo = '''    <!-- ABA ESTUDO -->
    <div id="conteudo-estudo" style="display: none;">
      <h1 class="page-title">📚 Estudo</h1>
      <p class="page-subtitle">Trilhas, cursos, turmas e formação teológica</p>

      <div id="estudo-alertas" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px;"></div>

      <div class="estudo-sub-abas">
        <button class="estudo-sub-aba ativa" data-subtab="catalogo" onclick="trocarSubAbaEstudo('catalogo')">📖 Catálogo</button>
        <button class="estudo-sub-aba" data-subtab="turmas" onclick="trocarSubAbaEstudo('turmas')">🎓 Turmas</button>
      </div>

      <!-- SUB-ABA: CATALOGO -->
      <div id="estudo-sub-catalogo">
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

      <!-- SUB-ABA: TURMAS -->
      <div id="estudo-sub-turmas" style="display: none;">
        <div class="toolbar" style="margin-bottom: 24px;">
          <input type="text" class="toolbar-search" id="busca-turma-estudo" placeholder="🔎 Buscar turma..." oninput="renderizarTurmas()">
          <select class="toolbar-select" id="filtro-status-turma" onchange="carregarTurmas()">
            <option value="">Todos os status</option>
            <option value="planejada">Planejadas</option>
            <option value="em_andamento">Em andamento</option>
            <option value="concluida">Concluídas</option>
            <option value="cancelada">Canceladas</option>
          </select>
          <button class="btn btn-primary" onclick="abrirFormTurma()">+ Nova Turma</button>
          <div class="toolbar-count" id="contador-turmas"></div>
        </div>
        <div id="container-turmas" class="grid"></div>
      </div>
    </div>'''

if old_estudo in conteudo:
    conteudo = conteudo.replace(old_estudo, new_estudo, 1)
    print("  [OK] Aba Estudo atualizada com sub-abas")

# ============================================================
# 3. Modais — Turma + Matrícula + Chamada
# ============================================================
modais = '''
<!-- Turma: form -->
<div class="modal-backdrop" id="modal-form-turma">
  <div class="modal" style="max-width: 620px;">
    <div class="modal-header">
      <h2 class="modal-title" id="form-turma-titulo">Nova Turma</h2>
      <button class="modal-close" onclick="fecharFormTurma()">×</button>
    </div>
    <form id="form-turma" onsubmit="salvarTurma(event)">
      <input type="hidden" id="form-turma-id">
      <div class="form-group">
        <label class="form-label">Nome *</label>
        <input class="form-input" name="nome" required minlength="2" placeholder="Turma Outubro/2026">
      </div>
      <div class="form-group">
        <label class="form-label">Curso *</label>
        <select class="form-select" name="curso_id" id="select-curso-turma" required></select>
      </div>
      <div class="form-group">
        <label class="form-label">Professor</label>
        <select class="form-select" name="professor_id" id="select-professor-turma">
          <option value="">Sem professor definido</option>
        </select>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Data de início</label>
          <input class="form-input" type="date" name="data_inicio">
        </div>
        <div class="form-group">
          <label class="form-label">Data de fim</label>
          <input class="form-input" type="date" name="data_fim">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Horário</label>
          <input class="form-input" name="horario" placeholder="Quinta 20h">
        </div>
        <div class="form-group">
          <label class="form-label">Local</label>
          <input class="form-input" name="local" placeholder="Sala 1">
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Vagas</label>
          <input class="form-input" type="number" name="vagas" min="0" placeholder="Sem limite">
        </div>
        <div class="form-group">
          <label class="form-label">Modalidade *</label>
          <select class="form-select" name="modalidade" required>
            <option value="presencial">Presencial</option>
            <option value="online">Online</option>
            <option value="hibrido">Híbrido</option>
          </select>
        </div>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormTurma()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-turma">Criar Turma</button>
      </div>
    </form>
  </div>
</div>

<!-- Turma: detalhes -->
<div class="modal-backdrop" id="modal-detalhes-turma">
  <div class="modal" style="max-width: 700px;">
    <div class="modal-header">
      <h2 class="modal-title" id="detalhe-turma-titulo">Turma</h2>
      <button class="modal-close" onclick="fecharDetalhesTurma()">×</button>
    </div>
    <div id="detalhe-turma-corpo"></div>

    <div style="display:flex; justify-content:space-between; align-items:center; margin:20px 0 12px;">
      <div style="font-size:14px; font-weight:700;">Alunos matriculados</div>
      <button class="btn btn-primary" style="padding:8px 14px; font-size:13px;" onclick="abrirFormMatricula()">+ Matricular aluno</button>
    </div>
    <div id="detalhe-turma-alunos"></div>

    <div style="display:flex; gap:8px; margin-top:20px; flex-wrap:wrap;">
      <button class="btn btn-ghost" onclick="fecharDetalhesTurma()">Fechar</button>
      <button class="btn btn-primary" onclick="editarTurmaDoDetalhe()">Editar</button>
      <button class="btn btn-success" onclick="abrirFormChamada()">📋 Fazer chamada</button>
      <button class="btn btn-danger" onclick="confirmarDeletarTurma()">Deletar</button>
    </div>
    <div class="modal-actions" style="margin-top: 8px;">
      <button class="btn btn-warning" id="btn-status-turma" onclick="alterarStatusTurma()">Iniciar turma</button>
    </div>
  </div>
</div>

<!-- Matricula: form -->
<div class="modal-backdrop" id="modal-form-matricula">
  <div class="modal" style="max-width: 480px;">
    <div class="modal-header">
      <h2 class="modal-title">Matricular aluno</h2>
      <button class="modal-close" onclick="fecharFormMatricula()">×</button>
    </div>
    <form id="form-matricula" onsubmit="salvarMatricula(event)">
      <div class="form-group">
        <label class="form-label">Pessoa *</label>
        <select class="form-select" id="select-pessoa-matricula" required></select>
      </div>
      <div class="form-group">
        <label class="form-label">Observações</label>
        <textarea class="form-input" id="input-obs-matricula" rows="2" style="font-family:inherit; resize:vertical;"></textarea>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormMatricula()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-matricula">Matricular</button>
      </div>
    </form>
  </div>
</div>

<!-- Chamada -->
<div class="modal-backdrop" id="modal-chamada">
  <div class="modal" style="max-width: 560px;">
    <div class="modal-header">
      <h2 class="modal-title">Chamada da turma</h2>
      <button class="modal-close" onclick="fecharFormChamada()">×</button>
    </div>
    <div class="form-group">
      <label class="form-label">Data da aula *</label>
      <input class="form-input" type="date" id="chamada-data" required>
    </div>
    <div class="form-group">
      <label class="form-label">Presentes</label>
      <div class="chamada-lista" id="chamada-lista"></div>
    </div>
    <div class="modal-actions">
      <button type="button" class="btn btn-ghost" onclick="fecharFormChamada()">Cancelar</button>
      <button type="button" class="btn btn-primary" onclick="salvarChamada()">Salvar chamada</button>
    </div>
  </div>
</div>
'''

if 'id="modal-form-turma"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)

# ============================================================
# 4. JS
# ============================================================
js = '''
// ============ ESTUDO — TURMAS E MATRICULAS ============
let turmasCache = [];
let turmaAtual = null;
let matriculasTurmaAtual = [];
let professoresCache = [];
let pessoasParaMatricula = [];

const STATUS_TURMA_LABEL = {
  planejada: "Planejada",
  em_andamento: "Em andamento",
  concluida: "Concluída",
  cancelada: "Cancelada",
};

const MODALIDADE_LABEL = {
  presencial: "Presencial",
  online: "Online",
  hibrido: "Híbrido",
};

function trocarSubAbaEstudo(sub) {
  document.querySelectorAll(".estudo-sub-aba").forEach(b => b.classList.toggle("ativa", b.dataset.subtab === sub));
  document.getElementById("estudo-sub-catalogo").style.display = sub === "catalogo" ? "block" : "none";
  document.getElementById("estudo-sub-turmas").style.display = sub === "turmas" ? "block" : "none";
  if (sub === "turmas") carregarTurmas();
}

async function carregarTurmas() {
  const container = document.getElementById("container-turmas");
  if (!container) return;
  container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⏳</div><div class="state-text">Carregando turmas...</div></div>`;

  const status = document.getElementById("filtro-status-turma").value;
  const params = new URLSearchParams();
  if (status) params.append("status_", status);

  try {
    const r = await apiFetch(`${API}/estudo/turmas/?${params}`);
    turmasCache = await r.json();
    renderizarTurmas();
  } catch (e) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-icon">⚠️</div><div class="state-text">${e.message}</div></div>`;
  }
}

function renderizarTurmas() {
  const container = document.getElementById("container-turmas");
  const contador = document.getElementById("contador-turmas");
  const busca = document.getElementById("busca-turma-estudo").value.toLowerCase().trim();

  const filtradas = turmasCache.filter(t => {
    if (!busca) return true;
    return [t.nome, t.local, t.horario].filter(Boolean).join(" ").toLowerCase().includes(busca);
  });

  const total = turmasCache.length;
  contador.textContent = `${total} turma${total !== 1 ? "s" : ""}`;

  if (turmasCache.length === 0) {
    container.innerHTML = `
      <div class="state" style="grid-column: 1/-1;"><div class="state-icon">🎓</div><div class="state-text">Nenhuma turma criada ainda.<br>Clique em "+ Nova Turma" para começar.</div></div>`;
    return;
  }

  let html = "";
  for (const t of filtradas) {
    const cls = t.ativa ? "" : "inativa";
    const cursoNome = t.curso?.nome || "Sem curso";
    const professorNome = t.professor?.nome ? "Prof. " + t.professor.nome : "Sem professor";
    const local = t.local ? "📍 " + t.local : "";
    const horario = t.horario ? "🕐 " + t.horario : "";
    const vagas = t.vagas ? `${t.total_matriculas || 0}/${t.vagas} vagas` : `${t.total_matriculas || 0} alunos`;
    html += `
      <div class="turma-card ${cls}" onclick="abrirDetalhesTurma('${t.id}')">
        <div class="turma-titulo">${t.nome}</div>
        <div class="turma-meta">📖 ${cursoNome}</div>
        <div class="turma-meta">👤 ${professorNome}</div>
        <div class="turma-meta">${[local, horario].filter(Boolean).join(" · ")}</div>
        <div class="turma-badges">
          <span class="turma-badge ${t.status}">${STATUS_TURMA_LABEL[t.status] || t.status}</span>
          <span class="turma-badge ${t.modalidade}">${MODALIDADE_LABEL[t.modalidade] || t.modalidade}</span>
          <span class="turma-badge planejada">${vagas}</span>
        </div>
      </div>
    `;
  }
  container.innerHTML = html;
}

async function carregarCursosParaTurma() {
  const sel = document.getElementById("select-curso-turma");
  if (!sel) return;
  try {
    const r = await apiFetch(`${API}/estudo/cursos/?apenas_ativos=true&limit=1000`);
    const cursos = await r.json();
    sel.innerHTML = '<option value="">Selecione o curso...</option>' +
      cursos.map(c => `<option value="${c.id}">${c.nome} (${c.nivel})</option>`).join("");
  } catch (e) { /* silencioso */ }
}

async function carregarProfessores() {
  const sel = document.getElementById("select-professor-turma");
  if (!sel) return;
  try {
    const r = await apiFetch(`${API}/auth/usuarios?apenas_ativos=true&limit=1000`);
    professoresCache = await r.json();
    sel.innerHTML = '<option value="">Sem professor definido</option>' +
      professoresCache.map(u => `<option value="${u.id}">${u.nome} (${u.role})</option>`).join("");
  } catch (e) { /* silencioso */ }
}

function abrirFormTurma(turma = null) {
  document.getElementById("form-turma").reset();
  carregarCursosParaTurma();
  carregarProfessores();
  const t = document.getElementById("form-turma-titulo");
  const b = document.getElementById("btn-salvar-turma");

  if (turma) {
    t.textContent = "Editar Turma"; b.textContent = "Salvar Alterações";
    document.getElementById("form-turma-id").value = turma.id;
    document.querySelector('#form-turma [name="nome"]').value = turma.nome || "";
    document.querySelector('#form-turma [name="horario"]').value = turma.horario || "";
    document.querySelector('#form-turma [name="local"]').value = turma.local || "";
    document.querySelector('#form-turma [name="vagas"]').value = turma.vagas || "";
    document.querySelector('#form-turma [name="data_inicio"]').value = turma.data_inicio || "";
    document.querySelector('#form-turma [name="data_fim"]').value = turma.data_fim || "";
    document.querySelector('#form-turma [name="modalidade"]').value = turma.modalidade || "presencial";
    setTimeout(() => {
      document.getElementById("select-curso-turma").value = turma.curso_id || "";
      document.getElementById("select-professor-turma").value = turma.professor_id || "";
    }, 150);
  } else {
    t.textContent = "Nova Turma"; b.textContent = "Criar Turma";
    document.getElementById("form-turma-id").value = "";
  }

  document.getElementById("modal-form-turma").classList.add("active");
  document.querySelector('#form-turma [name="nome"]').focus();
}

function fecharFormTurma() {
  document.getElementById("modal-form-turma").classList.remove("active");
}

async function salvarTurma(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-turma");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";

  const form = new FormData(e.target);
  const dados = {};
  for (const [k, v] of form.entries()) {
    if (k === "id") continue;
    if (k === "vagas") { if (v.trim()) dados[k] = parseInt(v); continue; }
    if (typeof v === "string" && v.trim()) dados[k] = v.trim();
  }

  const id = document.getElementById("form-turma-id").value;
  const url = id ? `${API}/estudo/turmas/${id}` : `${API}/estudo/turmas/`;
  const metodo = id ? "PUT" : "POST";
  try {
    const r = await apiFetch(url, { method: metodo, headers: {"Content-Type":"application/json"}, body: JSON.stringify(dados) });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormTurma();
    mostrarToast(id ? "✅ Turma atualizada!" : "✅ Turma criada!", "success");
    carregarTurmas();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

async function abrirDetalhesTurma(id) {
  const t = turmasCache.find(x => x.id === id); if (!t) return;
  turmaAtual = t;
  document.getElementById("detalhe-turma-titulo").textContent = t.nome;

  const linhas = [
    ["Curso", t.curso?.nome],
    ["Professor", t.professor?.nome],
    ["Status", STATUS_TURMA_LABEL[t.status] || t.status],
    ["Modalidade", MODALIDADE_LABEL[t.modalidade] || t.modalidade],
    ["Horário", t.horario],
    ["Local", t.local],
    ["Vagas", t.vagas ? String(t.vagas) : "Sem limite"],
    ["Início", t.data_inicio ? new Date(t.data_inicio + "T00:00:00").toLocaleDateString("pt-BR") : null],
    ["Fim", t.data_fim ? new Date(t.data_fim + "T00:00:00").toLocaleDateString("pt-BR") : null],
  ].filter(([,v]) => v);

  document.getElementById("detalhe-turma-corpo").innerHTML = linhas.map(([k,v])=>`<div class="detail-row"><div class="detail-label">${k}</div><div class="detail-value">${v}</div></div>`).join("");

  // Botão de status
  const b = document.getElementById("btn-status-turma");
  if (t.status === "planejada") { b.textContent = "Iniciar turma"; b.className = "btn btn-success"; }
  else if (t.status === "em_andamento") { b.textContent = "Concluir turma"; b.className = "btn btn-primary"; }
  else { b.textContent = "Turma finalizada"; b.className = "btn btn-ghost"; b.disabled = true; }

  document.getElementById("modal-detalhes-turma").classList.add("active");

  await carregarMatriculasTurma(id);
}

async function carregarMatriculasTurma(turmaId) {
  const div = document.getElementById("detalhe-turma-alunos");
  div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">Carregando alunos...</div></div>`;
  try {
    const r = await apiFetch(`${API}/estudo/turmas/${turmaId}/matriculas/`);
    matriculasTurmaAtual = await r.json();
    renderizarMatriculas();
  } catch (e) {
    div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">${e.message}</div></div>`;
  }
}

function renderizarMatriculas() {
  const div = document.getElementById("detalhe-turma-alunos");
  if (matriculasTurmaAtual.length === 0) {
    div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-icon">👥</div><div class="state-text">Nenhum aluno matriculado ainda.</div></div>`;
    return;
  }
  div.innerHTML = matriculasTurmaAtual.map(m => {
    const iniciais = (m.pessoa?.nome || "?").split(" ").slice(0, 2).map(s => s[0]).join("").toUpperCase();
    const pct = m.progresso_percentual || 0;
    const statusLabel = { matriculado: "Matriculado", aprovado: "Aprovado", reprovado: "Reprovado", desistente: "Desistente" };
    return `
      <div class="aluno-item">
        <div class="aluno-avatar">${iniciais}</div>
        <div class="aluno-corpo">
          <div class="aluno-nome">${m.pessoa?.nome || "?"}</div>
          <div class="aluno-meta">${statusLabel[m.status] || m.status} · ${pct}%</div>
          <div class="progresso-mini"><div class="progresso-mini-fill" style="width:${pct}%"></div></div>
        </div>
        <div class="aluno-acoes">
          <button class="btn-icon danger" onclick="deletarMatricula('${m.id}')" title="Remover">✕</button>
        </div>
      </div>`;
  }).join("");
}

function fecharDetalhesTurma() {
  document.getElementById("modal-detalhes-turma").classList.remove("active");
  turmaAtual = null;
  matriculasTurmaAtual = [];
}

function editarTurmaDoDetalhe() {
  if (!turmaAtual) return;
  const t = turmaAtual;
  fecharDetalhesTurma();
  abrirFormTurma(t);
}

async function alterarStatusTurma() {
  if (!turmaAtual) return;
  const t = turmaAtual;
  const acao = t.status === "planejada" ? "iniciar" : "concluir";
  try {
    const r = await apiFetch(`${API}/estudo/turmas/${t.id}/${acao}`, { method: "PATCH" });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharDetalhesTurma();
    mostrarToast("✅ Status atualizado!", "success");
    carregarTurmas();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
}

function confirmarDeletarTurma() {
  if (!turmaAtual) return;
  const t = turmaAtual;
  abrirConfirmar("Excluir turma?", `Tem certeza que deseja EXCLUIR "${t.nome}"? Se houver matrículas, a exclusão será bloqueada.`, async () => {
    try {
      const r = await apiFetch(`${API}/estudo/turmas/${t.id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      fecharDetalhesTurma(); mostrarToast("✅ Turma excluída.", "success"); carregarTurmas();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

// ============ MATRICULAS ============

async function carregarPessoasParaMatricula() {
  try {
    const r = await apiFetch(`${API}/pessoas/?apenas_ativos=true&limit=1000`);
    pessoasParaMatricula = await r.json();
    const sel = document.getElementById("select-pessoa-matricula");
    sel.innerHTML = '<option value="">Selecione a pessoa...</option>' +
      pessoasParaMatricula.map(p => `<option value="${p.id}">${p.nome}</option>`).join("");
  } catch (e) { /* silencioso */ }
}

function abrirFormMatricula() {
  if (!turmaAtual) return;
  document.getElementById("form-matricula").reset();
  carregarPessoasParaMatricula();
  document.getElementById("modal-form-matricula").classList.add("active");
}

function fecharFormMatricula() {
  document.getElementById("modal-form-matricula").classList.remove("active");
}

async function salvarMatricula(e) {
  e.preventDefault();
  if (!turmaAtual) return;
  const btn = document.getElementById("btn-salvar-matricula");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Matriculando...";
  const pessoaId = document.getElementById("select-pessoa-matricula").value;
  const obs = document.getElementById("input-obs-matricula").value.trim();
  if (!pessoaId) { mostrarToast("❌ Selecione uma pessoa", "error"); btn.disabled = false; btn.textContent = txt; return; }
  try {
    const r = await apiFetch(`${API}/estudo/turmas/${turmaAtual.id}/matriculas/`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ pessoa_id: pessoaId, observacoes: obs || null }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormMatricula();
    mostrarToast("✅ Aluno matriculado!", "success");
    await carregarMatriculasTurma(turmaAtual.id);
    carregarTurmas();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

async function deletarMatricula(id) {
  abrirConfirmar("Remover matrícula?", "Tem certeza que deseja remover este aluno da turma?", async () => {
    try {
      const r = await apiFetch(`${API}/estudo/matriculas/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Aluno removido.", "success");
      await carregarMatriculasTurma(turmaAtual.id);
      carregarTurmas();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

// ============ CHAMADA ============

function abrirFormChamada() {
  if (!turmaAtual) return;
  if (matriculasTurmaAtual.length === 0) {
    mostrarToast("❌ Nenhum aluno matriculado", "error");
    return;
  }
  const hoje = new Date().toISOString().split("T")[0];
  document.getElementById("chamada-data").value = hoje;

  const lista = document.getElementById("chamada-lista");
  lista.innerHTML = matriculasTurmaAtual.map(m => `
    <div class="chamada-item">
      <input type="checkbox" data-matricula="${m.id}" checked>
      <div class="chamada-nome">${m.pessoa?.nome || "?"}</div>
    </div>
  `).join("");

  document.getElementById("modal-chamada").classList.add("active");
}

function fecharFormChamada() {
  document.getElementById("modal-chamada").classList.remove("active");
}

async function salvarChamada() {
  if (!turmaAtual) return;
  const dataAula = document.getElementById("chamada-data").value;
  if (!dataAula) { mostrarToast("❌ Informe a data", "error"); return; }

  const presencas = [];
  document.querySelectorAll('#chamada-lista input[type="checkbox"]').forEach(cb => {
    presencas.push({
      matricula_id: cb.dataset.matricula,
      presente: cb.checked,
    });
  });

  try {
    const r = await apiFetch(`${API}/estudo/turmas/${turmaAtual.id}/chamada`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ data_aula: dataAula, presencas }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormChamada();
    mostrarToast("✅ Chamada registrada!", "success");
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
}
'''

if "// ============ ESTUDO — TURMAS E MATRICULAS ============" not in conteudo:
    marcador = "// ============ NOTIFICACOES ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("Aba Estudo -> sub-aba Turmas")
print("=" * 60)