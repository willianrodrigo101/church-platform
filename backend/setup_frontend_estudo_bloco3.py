code .\setup_frontend_estudo_bloco3.py
"""Frontend do modulo Estudo — Bloco 3: Quizzes + Forum + Badges + Gamificacao."""
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
  /* ============ GAMIFICACAO ============ */
  .gamificacao-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px;
    transition: all 0.15s;
  }
  .gamificacao-card:hover { border-color: var(--accent); }

  .ranking-item {
    display: flex; align-items: center; gap: 14px;
    padding: 14px 16px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; margin-bottom: 8px;
  }
  .ranking-pos {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: grid; place-items: center;
    font-size: 14px; font-weight: 700; color: white;
    flex-shrink: 0;
  }
  .ranking-pos.ouro    { background: linear-gradient(135deg, #fbbf24, #f59e0b); }
  .ranking-pos.prata   { background: linear-gradient(135deg, #d1d5db, #9ca3af); }
  .ranking-pos.bronze  { background: linear-gradient(135deg, #d97706, #92400e); }
  .ranking-pos.normal  { background: rgba(99,102,241,0.3); color: var(--accent); }
  .ranking-info { flex: 1; min-width: 0; }
  .ranking-nome { font-size: 15px; font-weight: 600; }
  .ranking-pontos { font-size: 13px; color: var(--text-muted); margin-top: 2px; }

  .badge-card {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px;
    text-align: center;
    transition: all 0.15s;
  }
  .badge-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .badge-icone {
    width: 60px; height: 60px; margin: 0 auto 10px;
    background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15));
    border-radius: 50%;
    display: grid; place-items: center;
    font-size: 28px;
  }
  .badge-nome { font-size: 14px; font-weight: 700; margin-bottom: 4px; }
  .badge-desc { font-size: 11px; color: var(--text-muted); line-height: 1.4; }
  .badge-pontos {
    margin-top: 10px; font-size: 11px; font-weight: 700;
    padding: 3px 10px; border-radius: 999px;
    background: rgba(16,185,129,0.15); color: var(--success);
    display: inline-block;
  }

  .quiz-card {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px;
    margin-bottom: 10px;
  }
  .quiz-titulo { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
  .quiz-meta { font-size: 12px; color: var(--text-muted); }

  .quiz-pergunta {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 18px;
    margin-bottom: 14px;
  }
  .quiz-pergunta-enunciado {
    font-size: 15px; font-weight: 600;
    margin-bottom: 14px; line-height: 1.5;
  }
  .quiz-opcao {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 14px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; margin-bottom: 8px;
    cursor: pointer; transition: all 0.15s;
  }
  .quiz-opcao:hover { border-color: var(--accent); background: var(--bg-card-hover); }
  .quiz-opcao input[type="radio"] {
    width: 18px; height: 18px; accent-color: var(--accent);
    cursor: pointer; flex-shrink: 0;
  }
  .quiz-opcao.selecionada { border-color: var(--accent); background: var(--bg-card-hover); }

  .comentario-item {
    display: flex; gap: 12px;
    padding: 14px 16px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px; margin-bottom: 8px;
  }
  .comentario-item.resposta { margin-left: 32px; opacity: 0.85; }
  .comentario-avatar {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    border-radius: 50%; display: grid; place-items: center;
    font-size: 12px; font-weight: 700; color: white; flex-shrink: 0;
  }
  .comentario-corpo { flex: 1; min-width: 0; }
  .comentario-autor { font-size: 13px; font-weight: 700; }
  .comentario-data { font-size: 11px; color: var(--text-muted); margin-left: 6px; font-weight: 400; }
  .comentario-texto { font-size: 13px; margin-top: 4px; line-height: 1.5; }
  .comentario-acoes { display: flex; gap: 6px; margin-top: 6px; }

  /* Resultado da tentativa */
  .resultado-quiz {
    text-align: center; padding: 30px 20px;
  }
  .resultado-nota {
    font-size: 64px; font-weight: 800;
    background: linear-gradient(135deg, var(--accent), #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 10px 0;
  }
  .resultado-status {
    font-size: 16px; font-weight: 700;
    padding: 8px 20px; border-radius: 999px;
    display: inline-block; margin-top: 10px;
  }
  .resultado-status.aprovado { background: rgba(16,185,129,0.15); color: var(--success); }
  .resultado-status.reprovado { background: rgba(239,68,68,0.15); color: var(--danger); }
'''

if ".gamificacao-card" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Atualizar HTML da aba Estudo — adicionar sub-aba Gamificacao
# ============================================================
old_sub_abas = '''      <div class="estudo-sub-abas">
        <button class="estudo-sub-aba ativa" data-subtab="catalogo" onclick="trocarSubAbaEstudo('catalogo')">📖 Catálogo</button>
        <button class="estudo-sub-aba" data-subtab="turmas" onclick="trocarSubAbaEstudo('turmas')">🎓 Turmas</button>
      </div>'''

new_sub_abas = '''      <div class="estudo-sub-abas">
        <button class="estudo-sub-aba ativa" data-subtab="catalogo" onclick="trocarSubAbaEstudo('catalogo')">📖 Catálogo</button>
        <button class="estudo-sub-aba" data-subtab="turmas" onclick="trocarSubAbaEstudo('turmas')">🎓 Turmas</button>
        <button class="estudo-sub-aba" data-subtab="gamificacao" onclick="trocarSubAbaEstudo('gamificacao')">🏆 Gamificação</button>
      </div>'''

if old_sub_abas in conteudo and 'data-subtab="gamificacao"' not in conteudo:
    conteudo = conteudo.replace(old_sub_abas, new_sub_abas, 1)
    print("  [OK] Sub-aba Gamificacao adicionada")

# Adicionar bloco HTML da gamificacao depois do bloco de turmas
old_turmas_block_end = '''      <!-- SUB-ABA: TURMAS -->
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
      </div>'''

new_gamificacao_block = old_turmas_block_end + '''

      <!-- SUB-ABA: GAMIFICACAO -->
      <div id="estudo-sub-gamificacao" style="display: none;">
        <div id="gamificacao-alertas" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px;"></div>

        <div class="toolbar" style="margin-bottom: 20px;">
          <button class="btn btn-primary" onclick="abrirFormBadge()">+ Novo Badge</button>
          <button class="btn btn-success" onclick="abrirFormConcederBadge()">🏅 Conceder Badge</button>
          <div class="toolbar-count" id="contador-badges"></div>
        </div>

        <h3 style="font-size:16px; margin: 24px 0 14px;">🏅 Badges da igreja</h3>
        <div id="container-badges" class="grid"></div>

        <h3 style="font-size:16px; margin: 32px 0 14px;">🥇 Ranking geral</h3>
        <div id="container-ranking"></div>
      </div>'''

if 'id="estudo-sub-gamificacao"' not in conteudo and old_turmas_block_end in conteudo:
    conteudo = conteudo.replace(old_turmas_block_end, new_gamificacao_block, 1)
    print("  [OK] Bloco de gamificacao adicionado")

# ============================================================
# 3. Modais — Badge + Conceder Badge + Quiz + Responder Quiz + Comentario
# ============================================================
modais = '''
<!-- Badge: form -->
<div class="modal-backdrop" id="modal-form-badge">
  <div class="modal" style="max-width: 500px;">
    <div class="modal-header">
      <h2 class="modal-title">Novo Badge</h2>
      <button class="modal-close" onclick="fecharFormBadge()">×</button>
    </div>
    <form id="form-badge" onsubmit="salvarBadge(event)">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Ícone *</label>
          <input class="form-input" name="icone" required maxlength="4" placeholder="🏅" value="🏅">
        </div>
        <div class="form-group">
          <label class="form-label">Código *</label>
          <input class="form-input" name="codigo" required maxlength="50" placeholder="primeiro_curso">
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Nome *</label>
        <input class="form-input" name="nome" required maxlength="100" placeholder="Primeiro Curso Concluído">
      </div>
      <div class="form-group">
        <label class="form-label">Descrição</label>
        <textarea class="form-input" name="descricao" rows="2" style="font-family:inherit; resize:vertical;" placeholder="Conquistado ao concluir o primeiro curso"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Pontos *</label>
        <input class="form-input" type="number" name="pontos" required min="1" value="10">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormBadge()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-badge">Criar Badge</button>
      </div>
    </form>
  </div>
</div>

<!-- Conceder Badge -->
<div class="modal-backdrop" id="modal-conceder-badge">
  <div class="modal" style="max-width: 500px;">
    <div class="modal-header">
      <h2 class="modal-title">Conceder Badge</h2>
      <button class="modal-close" onclick="fecharFormConcederBadge()">×</button>
    </div>
    <form id="form-conceder-badge" onsubmit="salvarConcederBadge(event)">
      <div class="form-group">
        <label class="form-label">Badge *</label>
        <select class="form-select" id="select-badge-conceder" required></select>
      </div>
      <div class="form-group">
        <label class="form-label">Pessoa *</label>
        <select class="form-select" id="select-pessoa-conceder" required></select>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormConcederBadge()">Cancelar</button>
        <button type="submit" class="btn btn-success" id="btn-conceder-badge">Conceder</button>
      </div>
    </form>
  </div>
</div>

<!-- Quiz: form -->
<div class="modal-backdrop" id="modal-form-quiz">
  <div class="modal" style="max-width: 720px;">
    <div class="modal-header">
      <h2 class="modal-title" id="form-quiz-titulo">Novo Quiz</h2>
      <button class="modal-close" onclick="fecharFormQuiz()">×</button>
    </div>
    <form id="form-quiz" onsubmit="salvarQuiz(event)">
      <input type="hidden" id="form-quiz-modulo-id">
      <div class="form-group">
        <label class="form-label">Título *</label>
        <input class="form-input" name="titulo" required maxlength="200" placeholder="Quiz do módulo 1">
      </div>
      <div class="form-group">
        <label class="form-label">Descrição</label>
        <textarea class="form-input" name="descricao" rows="2" style="font-family:inherit; resize:vertical;"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Nota mínima *</label>
          <input class="form-input" type="number" name="nota_minima" required min="0" max="10" step="0.1" value="7.0">
        </div>
        <div class="form-group">
          <label class="form-label">Tentativas máximas</label>
          <input class="form-input" type="number" name="tentativas_max" min="1" placeholder="Ilimitado">
        </div>
      </div>

      <div style="margin: 16px 0 10px; display:flex; justify-content:space-between; align-items:center;">
        <label class="form-label" style="margin:0;">Perguntas</label>
        <button type="button" class="btn btn-ghost" style="padding:6px 12px; font-size:12px;" onclick="adicionarPerguntaQuiz()">+ Adicionar pergunta</button>
      </div>
      <div id="perguntas-builder"></div>

      <div class="modal-actions" style="margin-top: 20px;">
        <button type="button" class="btn btn-ghost" onclick="fecharFormQuiz()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-quiz">Criar Quiz</button>
      </div>
    </form>
  </div>
</div>

<!-- Responder Quiz -->
<div class="modal-backdrop" id="modal-responder-quiz">
  <div class="modal" style="max-width: 620px;">
    <div class="modal-header">
      <h2 class="modal-title" id="responder-quiz-titulo">Quiz</h2>
      <button class="modal-close" onclick="fecharResponderQuiz()">×</button>
    </div>
    <div id="responder-quiz-corpo"></div>
  </div>
</div>

<!-- Comentario: form -->
<div class="modal-backdrop" id="modal-comentarios">
  <div class="modal" style="max-width: 620px;">
    <div class="modal-header">
      <h2 class="modal-title" id="comentarios-titulo">Fórum de dúvidas</h2>
      <button class="modal-close" onclick="fecharComentarios()">×</button>
    </div>
    <div id="comentarios-lista" style="max-height: 400px; overflow-y: auto; margin-bottom: 16px;"></div>
    <form id="form-comentario" onsubmit="salvarComentario(event)">
      <div class="form-group">
        <label class="form-label">Sua dúvida ou comentário *</label>
        <textarea class="form-input" id="input-comentario" required rows="2" style="font-family:inherit; resize:vertical;" placeholder="Escreva sua dúvida..."></textarea>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharComentarios()">Fechar</button>
        <button type="submit" class="btn btn-primary" id="btn-enviar-comentario">Enviar</button>
      </div>
    </form>
  </div>
</div>
'''

if 'id="modal-form-badge"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)
    print("  [OK] Modais adicionados")

# ============================================================
# 4. JS — Gamificacao, Badges, Quiz, Comentarios
# ============================================================
js = '''
// ============ GAMIFICACAO ============
let badgesCache = [];
let rankingCache = [];
let quizAtual = null;
let moduloAtualParaQuiz = null;
let comentariosModuloAtual = null;

async function carregarGamificacao() {
  const divAlertas = document.getElementById("gamificacao-alertas");
  if (!divAlertas) return;
  divAlertas.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-text">Carregando...</div></div>`;

  try {
    const [r1, r2] = await Promise.all([
      apiFetch(`${API}/estudo/badges/`),
      apiFetch(`${API}/estudo/gamificacao/dashboard`),
    ]);
    badgesCache = await r1.json();
    const dash = await r2.json();
    rankingCache = dash.ranking || [];

    renderizarAlertasGamificacao(dash);
    renderizarBadges();
    renderizarRanking();
  } catch (e) {
    divAlertas.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-text">${e.message}</div></div>`;
  }
}

function renderizarAlertasGamificacao(dash) {
  const div = document.getElementById("gamificacao-alertas");
  const cards = [
    { label: "Badges criados", valor: dash.total_badges || 0, cor: "var(--accent)", icon: "🏅" },
    { label: "Conquistas", valor: dash.total_conquistas || 0, cor: "var(--success)", icon: "🏆" },
    { label: "No ranking", valor: rankingCache.length, cor: "var(--warning)", icon: "📊" },
  ];
  div.innerHTML = cards.map(c => `
    <div class="card" style="cursor:default;">
      <div style="font-size:24px; margin-bottom:8px;">${c.icon}</div>
      <div style="font-size:28px; font-weight:700; color:${c.cor};">${c.valor}</div>
      <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">${c.label}</div>
    </div>
  `).join("");
}

function renderizarBadges() {
  const container = document.getElementById("container-badges");
  const contador = document.getElementById("contador-badges");
  if (!container) return;

  contador.textContent = `${badgesCache.length} badge${badgesCache.length !== 1 ? "s" : ""}`;

  if (badgesCache.length === 0) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1; padding:24px;"><div class="state-icon">🏅</div><div class="state-text">Nenhum badge criado ainda.<br>Clique em "+ Novo Badge" para começar.</div></div>`;
    return;
  }

  container.innerHTML = badgesCache.map(b => `
    <div class="badge-card">
      <div class="badge-icone">${b.icone || "🏅"}</div>
      <div class="badge-nome">${b.nome}</div>
      ${b.descricao ? `<div class="badge-desc">${b.descricao}</div>` : ""}
      <div class="badge-pontos">${b.pontos} pontos</div>
    </div>
  `).join("");
}

function renderizarRanking() {
  const container = document.getElementById("container-ranking");
  if (!container) return;

  if (rankingCache.length === 0) {
    container.innerHTML = `<div class="state" style="padding:24px;"><div class="state-icon">🥇</div><div class="state-text">Ninguém conquistou badges ainda.</div></div>`;
    return;
  }

  container.innerHTML = rankingCache.map((item, i) => {
    const pos = i + 1;
    const cls = pos === 1 ? "ouro" : pos === 2 ? "prata" : pos === 3 ? "bronze" : "normal";
    return `
      <div class="ranking-item">
        <div class="ranking-pos ${cls}">${pos}º</div>
        <div class="ranking-info">
          <div class="ranking-nome">${item.nome}</div>
          <div class="ranking-pontos">${item.pontos} pontos</div>
        </div>
      </div>
    `;
  }).join("");
}

// ============ CRIAR BADGE ============
function abrirFormBadge() {
  document.getElementById("form-badge").reset();
  document.querySelector('#form-badge [name="icone"]').value = "🏅";
  document.querySelector('#form-badge [name="pontos"]').value = 10;
  document.getElementById("modal-form-badge").classList.add("active");
}

function fecharFormBadge() {
  document.getElementById("modal-form-badge").classList.remove("active");
}

async function salvarBadge(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-badge");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";

  const dados = {};
  for (const [k, v] of new FormData(e.target).entries()) {
    if (k === "pontos") { dados[k] = parseInt(v) || 10; continue; }
    if (typeof v === "string" && v.trim()) dados[k] = v.trim();
  }

  try {
    const r = await apiFetch(`${API}/estudo/badges/`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(dados),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormBadge();
    mostrarToast("✅ Badge criado!", "success");
    carregarGamificacao();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

// ============ CONCEDER BADGE ============
async function abrirFormConcederBadge() {
  if (badgesCache.length === 0) {
    mostrarToast("❌ Crie um badge primeiro", "error");
    return;
  }
  document.getElementById("form-conceder-badge").reset();

  const selBadge = document.getElementById("select-badge-conceder");
  selBadge.innerHTML = '<option value="">Selecione...</option>' +
    badgesCache.map(b => `<option value="${b.id}">${b.icone} ${b.nome} (${b.pontos} pts)</option>`).join("");

  // Carrega pessoas
  try {
    const r = await apiFetch(`${API}/pessoas/?apenas_ativos=true&limit=1000`);
    const pessoas = await r.json();
    const selPessoa = document.getElementById("select-pessoa-conceder");
    selPessoa.innerHTML = '<option value="">Selecione...</option>' +
      pessoas.map(p => `<option value="${p.id}">${p.nome}</option>`).join("");
  } catch (e) { /* silencioso */ }

  document.getElementById("modal-conceder-badge").classList.add("active");
}

function fecharFormConcederBadge() {
  document.getElementById("modal-conceder-badge").classList.remove("active");
}

async function salvarConcederBadge(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-conceder-badge");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Concedendo...";

  const badgeId = document.getElementById("select-badge-conceder").value;
  const pessoaId = document.getElementById("select-pessoa-conceder").value;

  if (!badgeId || !pessoaId) {
    mostrarToast("❌ Selecione badge e pessoa", "error");
    btn.disabled = false; btn.textContent = txt;
    return;
  }

  try {
    const r = await apiFetch(`${API}/estudo/badges/${badgeId}/conceder?pessoa_id=${pessoaId}`, {
      method: "POST",
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormConcederBadge();
    mostrarToast("🏅 Badge concedido!", "success");
    carregarGamificacao();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

// ============ QUIZ ============

function abrirFormQuiz(moduloId, moduloTitulo) {
  document.getElementById("form-quiz").reset();
  document.getElementById("perguntas-builder").innerHTML = "";
  document.getElementById("form-quiz-modulo-id").value = moduloId;
  document.getElementById("form-quiz-titulo").textContent = `Novo Quiz — ${moduloTitulo || ""}`;

  adicionarPerguntaQuiz();
  document.getElementById("modal-form-quiz").classList.add("active");
}

function fecharFormQuiz() {
  document.getElementById("modal-form-quiz").classList.remove("active");
}

function adicionarPerguntaQuiz() {
  const builder = document.getElementById("perguntas-builder");
  const div = document.createElement("div");
  div.className = "modulo-builder";
  div.style.marginBottom = "10px";
  div.innerHTML = `
    <div class="modulo-builder-header">
      <input type="text" placeholder="Enunciado da pergunta" data-field="enunciado" required>
      <button type="button" class="btn-icon danger" onclick="this.closest('.modulo-builder').remove()">✕</button>
    </div>
    <div class="opcoes-builder" style="display:flex; flex-direction:column; gap:6px; margin-bottom:10px;">
      <div style="display:flex; gap:6px; align-items:center;">
        <input type="radio" name="correta-${Date.now()}" data-field="correta" value="0" checked style="width:18px; height:18px; accent-color:var(--success);">
        <input type="text" placeholder="Opção A" data-field="opcao" required style="flex:1;">
      </div>
      <div style="display:flex; gap:6px; align-items:center;">
        <input type="radio" name="correta-${Date.now()}" data-field="correta" value="1" style="width:18px; height:18px; accent-color:var(--success);">
        <input type="text" placeholder="Opção B" data-field="opcao" required style="flex:1;">
      </div>
      <div style="display:flex; gap:6px; align-items:center;">
        <input type="radio" name="correta-${Date.now()}" data-field="correta" value="2" style="width:18px; height:18px; accent-color:var(--success);">
        <input type="text" placeholder="Opção C" data-field="opcao" required style="flex:1;">
      </div>
      <div style="display:flex; gap:6px; align-items:center;">
        <input type="radio" name="correta-${Date.now()}" data-field="correta" value="3" style="width:18px; height:18px; accent-color:var(--success);">
        <input type="text" placeholder="Opção D" data-field="opcao" required style="flex:1;">
      </div>
    </div>
  `;
  builder.appendChild(div);
}

function coletarPerguntasQuiz() {
  const builders = document.querySelectorAll("#perguntas-builder .modulo-builder");
  const perguntas = [];
  builders.forEach((b, i) => {
    const enunciado = b.querySelector('[data-field="enunciado"]').value.trim();
    if (!enunciado) return;

    const opcoes = [];
    let correta = 0;
    b.querySelectorAll('[data-field="opcao"]').forEach((inp, j) => {
      const texto = inp.value.trim();
      if (!texto) return;
      opcoes.push(texto);
      const radio = b.querySelector(`[data-field="correta"][value="${j}"]`);
      if (radio && radio.checked) correta = opcoes.length - 1;
    });

    if (opcoes.length >= 2) {
      perguntas.push({
        ordem: i + 1,
        enunciado,
        opcoes,
        resposta_correta: correta,
        pontuacao: 1.0,
      });
    }
  });
  return perguntas;
}

async function salvarQuiz(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-quiz");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";

  const moduloId = document.getElementById("form-quiz-modulo-id").value;
  const form = new FormData(e.target);
  const dados = {
    modulo_id: moduloId,
    titulo: form.get("titulo"),
    descricao: form.get("descricao") || null,
    nota_minima: parseFloat(form.get("nota_minima") || "7.0"),
    tentativas_max: form.get("tentativas_max") ? parseInt(form.get("tentativas_max")) : null,
    perguntas: coletarPerguntasQuiz(),
  };

  if (dados.perguntas.length === 0) {
    mostrarToast("❌ Adicione pelo menos 1 pergunta válida", "error");
    btn.disabled = false; btn.textContent = txt;
    return;
  }

  try {
    const r = await apiFetch(`${API}/estudo/quizzes/`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(dados),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormQuiz();
    mostrarToast("✅ Quiz criado!", "success");
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

// ============ RESPONDER QUIZ ============
async function abrirResponderQuiz(quizId) {
  document.getElementById("responder-quiz-corpo").innerHTML = `<div class="state" style="padding:24px;"><div class="state-text">Carregando quiz...</div></div>`;
  document.getElementById("modal-responder-quiz").classList.add("active");

  try {
    const r = await apiFetch(`${API}/estudo/quizzes/${quizId}`);
    if (!r.ok) throw new Error("Erro ao carregar");
    quizAtual = await r.json();
    renderizarResponderQuiz();
  } catch (err) {
    document.getElementById("responder-quiz-corpo").innerHTML = `<div class="state" style="padding:24px;"><div class="state-text">❌ ${err.message}</div></div>`;
  }
}

function renderizarResponderQuiz() {
  const q = quizAtual;
  document.getElementById("responder-quiz-titulo").textContent = q.titulo;

  if (!q.perguntas || q.perguntas.length === 0) {
    document.getElementById("responder-quiz-corpo").innerHTML = `<div class="state" style="padding:24px;"><div class="state-text">Este quiz não tem perguntas.</div></div>`;
    return;
  }

  let html = '';
  q.perguntas.forEach((p, i) => {
    let opcoes = [];
    try { opcoes = JSON.parse(p.opcoes); } catch (e) { opcoes = []; }

    html += `
      <div class="quiz-pergunta">
        <div class="quiz-pergunta-enunciado">${i+1}. ${p.enunciado}</div>
        ${opcoes.map((op, j) => `
          <label class="quiz-opcao">
            <input type="radio" name="pergunta-${p.id}" value="${j}">
            <span>${op}</span>
          </label>
        `).join("")}
      </div>
    `;
  });

  html += `
    <div class="modal-actions" style="margin-top:20px;">
      <button class="btn btn-ghost" onclick="fecharResponderQuiz()">Cancelar</button>
      <button class="btn btn-primary" onclick="enviarRespostasQuiz()">Enviar respostas</button>
    </div>
  `;

  document.getElementById("responder-quiz-corpo").innerHTML = html;
}

function fecharResponderQuiz() {
  document.getElementById("modal-responder-quiz").classList.remove("active");
  quizAtual = null;
}

async function enviarRespostasQuiz() {
  if (!quizAtual) return;

  // Coleta respostas
  const respostas = {};
  document.querySelectorAll('#responder-quiz-corpo input[type="radio"]:checked').forEach(inp => {
    const perguntaId = inp.name.replace("pergunta-", "");
    respostas[perguntaId] = parseInt(inp.value);
  });

  // Verifica se respondeu tudo
  const faltam = quizAtual.perguntas.filter(p => !(p.id in respostas));
  if (faltam.length > 0) {
    mostrarToast(`❌ Faltam ${faltam.length} pergunta(s)`, "error");
    return;
  }

  // Precisa de matrícula — usa pessoa do usuário logado (simplificação MVP)
  // Em produção, seria escolhida a matrícula do aluno
  const matriculaId = prompt("Digite o ID da matrícula do aluno (ou deixe vazio para simular):");
  if (!matriculaId) {
    mostrarToast("⚠️ Simulação apenas. Não salvou tentativa.", "warning");
    return;
  }

  try {
    const r = await apiFetch(`${API}/estudo/quizzes/${quizAtual.id}/responder?matricula_id=${matriculaId}`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ respostas }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    const tentativa = await r.json();
    renderizarResultadoQuiz(tentativa);
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
}

function renderizarResultadoQuiz(t) {
  const statusCls = t.aprovado ? "aprovado" : "reprovado";
  const statusLabel = t.aprovado ? "APROVADO ✅" : "NÃO ATINGIU A NOTA ❌";
  document.getElementById("responder-quiz-corpo").innerHTML = `
    <div class="resultado-quiz">
      <div style="font-size:14px; color:var(--text-muted);">Sua nota</div>
      <div class="resultado-nota">${t.nota}</div>
      <div style="font-size:14px; color:var(--text-muted);">${t.acertos} de ${t.total} corretas</div>
      <div class="resultado-status ${statusCls}">${statusLabel}</div>
    </div>
    <div class="modal-actions" style="margin-top:20px;">
      <button class="btn btn-primary" onclick="fecharResponderQuiz()">Fechar</button>
    </div>
  `;
}

// ============ COMENTARIOS / FORUM ============
async function abrirComentarios(moduloId, moduloTitulo) {
  comentariosModuloAtual = moduloId;
  document.getElementById("comentarios-titulo").textContent = `Fórum — ${moduloTitulo || "Módulo"}`;
  document.getElementById("input-comentario").value = "";
  document.getElementById("modal-comentarios").classList.add("active");
  await carregarComentarios(moduloId);
}

function fecharComentarios() {
  document.getElementById("modal-comentarios").classList.remove("active");
  comentariosModuloAtual = null;
}

async function carregarComentarios(moduloId) {
  const div = document.getElementById("comentarios-lista");
  div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">Carregando...</div></div>`;

  try {
    const r = await apiFetch(`${API}/estudo/modulos/${moduloId}/comentarios/`);
    const lista = await r.json();

    if (lista.length === 0) {
      div.innerHTML = `<div class="state" style="padding:24px;"><div class="state-icon">💬</div><div class="state-text">Nenhum comentário ainda. Seja o primeiro!</div></div>`;
      return;
    }

    div.innerHTML = lista.map(c => {
      const iniciais = (c.pessoa?.nome || "?").split(" ").slice(0, 2).map(s => s[0]).join("").toUpperCase();
      const data = new Date(c.created_at).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
      const cls = c.parent_id ? "resposta" : "";
      return `
        <div class="comentario-item ${cls}">
          <div class="comentario-avatar">${iniciais}</div>
          <div class="comentario-corpo">
            <div class="comentario-autor">${c.pessoa?.nome || "?"}<span class="comentario-data">${data}</span></div>
            <div class="comentario-texto">${c.texto}</div>
            <div class="comentario-acoes">
              <button class="btn-icon danger" onclick="deletarComentario('${c.id}')" title="Excluir">✕</button>
            </div>
          </div>
        </div>
      `;
    }).join("");
  } catch (e) {
    div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">${e.message}</div></div>`;
  }
}

async function salvarComentario(e) {
  e.preventDefault();
  if (!comentariosModuloAtual) return;

  const btn = document.getElementById("btn-enviar-comentario");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Enviando...";

  const texto = document.getElementById("input-comentario").value.trim();
  if (!texto) { btn.disabled = false; btn.textContent = txt; return; }

  // Precisa do pessoa_id — usa prompt temporário
  // Em produção, usa a pessoa logada
  const pessoaId = prompt("ID da pessoa (simulação MVP):");
  if (!pessoaId) {
    btn.disabled = false; btn.textContent = txt;
    return;
  }

  try {
    const r = await apiFetch(`${API}/estudo/modulos/${comentariosModuloAtual}/comentarios/?pessoa_id=${pessoaId}`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ texto }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    document.getElementById("input-comentario").value = "";
    mostrarToast("✅ Comentário enviado!", "success");
    await carregarComentarios(comentariosModuloAtual);
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

async function deletarComentario(id) {
  abrirConfirmar("Excluir comentário?", "Esta ação não pode ser desfeita.", async () => {
    try {
      const r = await apiFetch(`${API}/estudo/comentarios/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Comentário removido.", "success");
      await carregarComentarios(comentariosModuloAtual);
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}
'''

if "// ============ GAMIFICACAO ============" not in conteudo:
    marcador = "// ============ NOTIFICACOES ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)
        print("  [OK] JS de gamificacao adicionado")

# ============================================================
# 5. Atualizar trocarSubAbaEstudo para incluir gamificacao
# ============================================================
import re
novo_sub = '''function trocarSubAbaEstudo(sub) {
  document.querySelectorAll(".estudo-sub-aba").forEach(b => b.classList.toggle("ativa", b.dataset.subtab === sub));
  const cat = document.getElementById("estudo-sub-catalogo");
  if (cat) cat.style.display = sub === "catalogo" ? "block" : "none";
  const tur = document.getElementById("estudo-sub-turmas");
  if (tur) tur.style.display = sub === "turmas" ? "block" : "none";
  const gam = document.getElementById("estudo-sub-gamificacao");
  if (gam) gam.style.display = sub === "gamificacao" ? "block" : "none";
  if (sub === "turmas") carregarTurmas();
  else if (sub === "gamificacao") carregarGamificacao();
}'''

conteudo = re.sub(
    r'function trocarSubAbaEstudo\(sub\) \{.*?\n\}',
    novo_sub,
    conteudo,
    count=1,
    flags=re.DOTALL,
)

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("Aba Estudo -> sub-aba Gamificação")
print("=" * 60)