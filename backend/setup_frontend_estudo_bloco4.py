"""Frontend do modulo Estudo — Bloco 4: Certificados + Anotacoes + Ferramentas."""
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
  /* ============ CERTIFICADOS ============ */
  .cert-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px; padding: 22px;
    transition: all 0.2s;
    position: relative; overflow: hidden;
  }
  .cert-card::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #fbbf24, #f59e0b);
  }
  .cert-card:hover { transform: translateY(-2px); border-color: #fbbf24; }
  .cert-card.cancelado { opacity: 0.5; }
  .cert-header {
    display: flex; gap: 14px; align-items: flex-start;
    margin-bottom: 14px;
  }
  .cert-icone {
    width: 50px; height: 50px;
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    border-radius: 14px;
    display: grid; place-items: center;
    font-size: 24px; flex-shrink: 0;
  }
  .cert-corpo { flex: 1; min-width: 0; }
  .cert-titulo { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
  .cert-aluno { font-size: 13px; color: var(--text-muted); }
  .cert-codigo {
    font-family: "Courier New", monospace;
    font-size: 12px; font-weight: 700;
    background: rgba(251,191,36,0.15); color: #fbbf24;
    padding: 4px 10px; border-radius: 6px;
    display: inline-block; margin-top: 8px;
  }
  .cert-meta {
    display: flex; gap: 16px; font-size: 12px;
    color: var(--text-muted); margin-top: 10px;
    padding-top: 10px; border-top: 1px solid var(--border);
  }
  .cert-acoes {
    display: flex; gap: 8px; margin-top: 12px;
    padding-top: 12px; border-top: 1px solid var(--border);
  }

  /* ============ FERRAMENTAS ============ */
  .ferramenta-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px;
    transition: all 0.15s; cursor: pointer;
    display: flex; gap: 14px; align-items: flex-start;
    text-decoration: none; color: inherit;
  }
  .ferramenta-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .ferramenta-icone {
    width: 48px; height: 48px;
    background: rgba(99,102,241,0.15);
    border-radius: 12px;
    display: grid; place-items: center;
    font-size: 22px; flex-shrink: 0;
  }
  .ferramenta-corpo { flex: 1; min-width: 0; }
  .ferramenta-nome { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
  .ferramenta-desc { font-size: 12px; color: var(--text-muted); line-height: 1.5; }
  .ferramenta-cat {
    font-size: 11px; font-weight: 600;
    padding: 3px 8px; border-radius: 6px;
    margin-top: 8px; display: inline-block;
    background: rgba(99,102,241,0.15); color: var(--accent);
    text-transform: uppercase; letter-spacing: 0.3px;
  }
  .ferramenta-cat.lexico      { background: rgba(16,185,129,0.15); color: #34d399; }
  .ferramenta-cat.interlinear { background: rgba(245,158,11,0.15); color: #fbbf24; }
  .ferramenta-cat.mapa        { background: rgba(59,130,246,0.15); color: #60a5fa; }
  .ferramenta-cat.gramatica   { background: rgba(236,72,153,0.15); color: #f472b6; }
  .ferramenta-cat.comentario  { background: rgba(139,92,246,0.15); color: #a78bfa; }

  /* ============ ANOTACOES ============ */
  .anotacao-item {
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px 16px;
    margin-bottom: 10px;
    transition: all 0.15s;
  }
  .anotacao-item:hover { border-color: var(--accent); }
  .anotacao-item.favorito { border-left: 3px solid #fbbf24; }
  .anotacao-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    gap: 10px; margin-bottom: 8px;
  }
  .anotacao-titulo { font-size: 14px; font-weight: 700; }
  .anotacao-data { font-size: 11px; color: var(--text-muted); }
  .anotacao-conteudo {
    font-size: 13px; line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
  }
  .anotacao-acoes {
    display: flex; gap: 6px; margin-top: 10px;
    justify-content: flex-end;
  }

  /* ============ VALIDACAO PUBLICA ============ */
  .validacao-container {
    max-width: 600px; margin: 40px auto;
    padding: 30px;
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 16px;
  }
  .validacao-resultado {
    margin-top: 20px; padding: 20px;
    border-radius: 12px;
    border: 2px solid;
  }
  .validacao-resultado.valido {
    background: rgba(16,185,129,0.1);
    border-color: rgba(16,185,129,0.4);
  }
  .validacao-resultado.invalido {
    background: rgba(239,68,68,0.1);
    border-color: rgba(239,68,68,0.4);
  }
  .validacao-status {
    font-size: 20px; font-weight: 800;
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 16px;
  }
  .validacao-status.valido { color: var(--success); }
  .validacao-status.invalido { color: var(--danger); }
  .validacao-linha {
    display: flex; justify-content: space-between;
    padding: 8px 0; border-bottom: 1px solid var(--border);
  }
  .validacao-linha:last-child { border-bottom: none; }
  .validacao-label { font-size: 12px; color: var(--text-muted); }
  .validacao-valor { font-size: 13px; font-weight: 600; text-align: right; }
'''

if ".cert-card" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)
    print("  [OK] CSS adicionado")

# ============================================================
# 2. Sub-abas — adiciona Certificados e Ferramentas
# ============================================================
old_sub_abas = '''      <div class="estudo-sub-abas">
        <button class="estudo-sub-aba ativa" data-subtab="catalogo" onclick="trocarSubAbaEstudo('catalogo')">📖 Catálogo</button>
        <button class="estudo-sub-aba" data-subtab="turmas" onclick="trocarSubAbaEstudo('turmas')">🎓 Turmas</button>
        <button class="estudo-sub-aba" data-subtab="gamificacao" onclick="trocarSubAbaEstudo('gamificacao')">🏆 Gamificação</button>
      </div>'''

new_sub_abas = '''      <div class="estudo-sub-abas">
        <button class="estudo-sub-aba ativa" data-subtab="catalogo" onclick="trocarSubAbaEstudo('catalogo')">📖 Catálogo</button>
        <button class="estudo-sub-aba" data-subtab="turmas" onclick="trocarSubAbaEstudo('turmas')">🎓 Turmas</button>
        <button class="estudo-sub-aba" data-subtab="quizzes" onclick="trocarSubAbaEstudo('quizzes')">📝 Quizzes</button>
        <button class="estudo-sub-aba" data-subtab="forum" onclick="trocarSubAbaEstudo('forum')">💬 Fórum</button>
        <button class="estudo-sub-aba" data-subtab="gamificacao" onclick="trocarSubAbaEstudo('gamificacao')">🏅 Gamificação</button>
        <button class="estudo-sub-aba" data-subtab="certificados" onclick="trocarSubAbaEstudo('certificados')">📜 Certificados</button>
        <button class="estudo-sub-aba" data-subtab="ferramentas" onclick="trocarSubAbaEstudo('ferramentas')">🔧 Ferramentas</button>
      </div>'''

if old_sub_abas in conteudo:
    # Verifica se já tem as sub-abas novas
    if 'data-subtab="certificados"' not in conteudo:
        conteudo = conteudo.replace(old_sub_abas, new_sub_abas, 1)
        print("  [OK] Sub-abas Certificados + Ferramentas adicionadas")
    else:
        print("  [SKIP] Sub-abas ja existem")

# ============================================================
# 3. HTML das novas sub-abas — inserir antes de </main>
# ============================================================
html_cert = '''
      <!-- SUB-ABA: CERTIFICADOS -->
      <div id="estudo-sub-certificados" style="display: none;">
        <div id="certificados-alertas" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px;"></div>

        <div class="toolbar" style="margin-bottom: 20px;">
          <button class="btn btn-primary" onclick="abrirFormEmitirCertificado()">🎓 Emitir Certificado</button>
          <button class="btn btn-success" onclick="abrirFormValidarCertificado()">✓ Validar Código</button>
          <div class="toolbar-count" id="contador-certificados"></div>
        </div>

        <div id="container-certificados" class="grid"></div>
      </div>

      <!-- SUB-ABA: FERRAMENTAS -->
      <div id="estudo-sub-ferramentas" style="display: none;">
        <div class="toolbar" style="margin-bottom: 20px;">
          <select class="toolbar-select" id="filtro-categoria-ferramenta" onchange="renderizarFerramentas()">
            <option value="">Todas as categorias</option>
            <option value="interlinear">Interlinear</option>
            <option value="lexico">Léxico</option>
            <option value="mapa">Mapa</option>
            <option value="gramatica">Gramática</option>
            <option value="comentario">Comentário</option>
            <option value="dicionario">Dicionário</option>
            <option value="referencia">Referência</option>
            <option value="outro">Outro</option>
          </select>
          <button class="btn btn-primary" onclick="abrirFormFerramenta()">+ Nova Ferramenta</button>
          <div class="toolbar-count" id="contador-ferramentas"></div>
        </div>

        <div id="container-ferramentas" class="grid"></div>
      </div>
'''

if 'id="estudo-sub-certificados"' not in conteudo:
    # Insere antes do fechamento da aba Estudo
    marcador = '''      <!-- SUB-ABA: GAMIFICACAO -->
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

    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, marcador + html_cert, 1)
        print("  [OK] HTML das sub-abas adicionado")
    else:
        print("  [AVISO] nao achei o bloco de gamificacao para inserir depois")

# ============================================================
# 4. Modais
# ============================================================
modais = '''
<!-- Emitir Certificado -->
<div class="modal-backdrop" id="modal-emitir-certificado">
  <div class="modal" style="max-width: 500px;">
    <div class="modal-header">
      <h2 class="modal-title">🎓 Emitir Certificado</h2>
      <button class="modal-close" onclick="fecharFormEmitirCertificado()">×</button>
    </div>
    <form id="form-emitir-certificado" onsubmit="salvarEmitirCertificado(event)">
      <div class="form-group">
        <label class="form-label">Matrícula (aprovada) *</label>
        <select class="form-select" id="select-matricula-certificado" required></select>
      </div>
      <div class="form-group">
        <label class="form-label">Carga horária (opcional)</label>
        <input class="form-input" type="number" id="input-carga-certificado" min="0" placeholder="Ex: 60">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormEmitirCertificado()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-emitir-certificado">Emitir Certificado</button>
      </div>
    </form>
  </div>
</div>

<!-- Validar Certificado -->
<div class="modal-backdrop" id="modal-validar-certificado">
  <div class="modal" style="max-width: 500px;">
    <div class="modal-header">
      <h2 class="modal-title">✓ Validar Certificado</h2>
      <button class="modal-close" onclick="fecharFormValidarCertificado()">×</button>
    </div>
    <form id="form-validar-certificado" onsubmit="validarCertificado(event)">
      <div class="form-group">
        <label class="form-label">Código do certificado *</label>
        <input class="form-input" id="input-codigo-validacao" required placeholder="CERT-XXXXXXXXXXXX" style="font-family: monospace; text-transform: uppercase;">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormValidarCertificado()">Cancelar</button>
        <button type="submit" class="btn btn-success" id="btn-validar-certificado">Validar</button>
      </div>
    </form>
    <div id="resultado-validacao"></div>
  </div>
</div>

<!-- Ferramenta: form -->
<div class="modal-backdrop" id="modal-form-ferramenta">
  <div class="modal" style="max-width: 560px;">
    <div class="modal-header">
      <h2 class="modal-title">🔧 Nova Ferramenta</h2>
      <button class="modal-close" onclick="fecharFormFerramenta()">×</button>
    </div>
    <form id="form-ferramenta" onsubmit="salvarFerramenta(event)">
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">Ícone</label>
          <input class="form-input" name="icone" maxlength="4" placeholder="🔗" value="🔗">
        </div>
        <div class="form-group">
          <label class="form-label">Categoria *</label>
          <select class="form-select" name="categoria" required>
            <option value="interlinear">Interlinear</option>
            <option value="lexico">Léxico</option>
            <option value="mapa">Mapa</option>
            <option value="gramatica">Gramática</option>
            <option value="comentario">Comentário</option>
            <option value="dicionario">Dicionário</option>
            <option value="referencia">Referência</option>
            <option value="outro" selected>Outro</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Nome *</label>
        <input class="form-input" name="nome" required maxlength="200" placeholder="STEP Bible">
      </div>
      <div class="form-group">
        <label class="form-label">Descrição</label>
        <textarea class="form-input" name="descricao" rows="2" style="font-family:inherit; resize:vertical;" placeholder="Interlinear grego/hebraico da Tyndale House"></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">URL *</label>
        <input class="form-input" name="url" type="url" required placeholder="https://www.stepbible.org">
      </div>
      <div class="form-group">
        <label class="form-label">Ordem</label>
        <input class="form-input" type="number" name="ordem" min="1" value="1">
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormFerramenta()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-ferramenta">Criar Ferramenta</button>
      </div>
    </form>
  </div>
</div>

<!-- Anotacoes: form -->
<div class="modal-backdrop" id="modal-anotacoes-modulo">
  <div class="modal" style="max-width: 640px;">
    <div class="modal-header">
      <h2 class="modal-title" id="anotacoes-titulo">📝 Anotações</h2>
      <button class="modal-close" onclick="fecharAnotacoesModulo()">×</button>
    </div>

    <div id="anotacoes-lista" style="max-height: 400px; overflow-y: auto; margin-bottom: 16px;"></div>

    <form id="form-anotacao" onsubmit="salvarAnotacaoModulo(event)">
      <input type="hidden" id="form-anotacao-id">
      <div class="form-group">
        <label class="form-label">Título *</label>
        <input class="form-input" id="input-anotacao-titulo" required maxlength="200" placeholder="Dúvida sobre...">
      </div>
      <div class="form-group">
        <label class="form-label">Conteúdo *</label>
        <textarea class="form-input" id="input-anotacao-conteudo" required rows="4" style="font-family:inherit; resize:vertical;" placeholder="Escreva sua anotação..."></textarea>
      </div>
      <div class="form-group">
        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
          <input type="checkbox" id="input-anotacao-favorito" style="width:18px; height:18px; accent-color:#fbbf24;">
          <span style="font-size: 13px;">Marcar como favorita</span>
        </label>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharAnotacoesModulo()">Fechar</button>
        <button type="submit" class="btn btn-primary" id="btn-salvar-anotacao">Salvar Anotação</button>
      </div>
    </form>
  </div>
</div>
'''

if 'id="modal-emitir-certificado"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)
    print("  [OK] Modais adicionados")

# ============================================================
# 5. JAVASCRIPT — Certificados + Ferramentas + Anotacoes
# ============================================================
js = '''
// ============ ESTUDO BL 4 — CERTIFICADOS ============
let certificadosCache = [];
let ferramentasCache = [];
let moduloAtualAnotacoes = null;
let anotacoesModuloCache = [];

async function carregarCertificados() {
  const divAlertas = document.getElementById("certificados-alertas");
  if (!divAlertas) return;
  divAlertas.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-text">Carregando...</div></div>`;

  try {
    const r = await apiFetch(`${API}/estudo/certificados/`);
    certificadosCache = await r.json();

    const total = certificadosCache.length;
    const ativos = certificadosCache.filter(c => !c.cancelado).length;
    const comPdf = certificadosCache.filter(c => c.url_pdf).length;

    divAlertas.innerHTML = `
      <div class="card" style="cursor:default;">
        <div style="font-size:24px; margin-bottom:8px;">📜</div>
        <div style="font-size:28px; font-weight:700; color:#fbbf24;">${total}</div>
        <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Certificados</div>
      </div>
      <div class="card" style="cursor:default;">
        <div style="font-size:24px; margin-bottom:8px;">✅</div>
        <div style="font-size:28px; font-weight:700; color:var(--success);">${ativos}</div>
        <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Ativos</div>
      </div>
      <div class="card" style="cursor:default;">
        <div style="font-size:24px; margin-bottom:8px;">📄</div>
        <div style="font-size:28px; font-weight:700; color:var(--accent);">${comPdf}</div>
        <div style="font-size:12px; color:var(--text-muted); margin-top:4px;">Com PDF</div>
      </div>
    `;

    renderizarCertificados();
  } catch (e) {
    divAlertas.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-text">${e.message}</div></div>`;
  }
}

function renderizarCertificados() {
  const container = document.getElementById("container-certificados");
  const contador = document.getElementById("contador-certificados");
  if (!container) return;

  contador.textContent = `${certificadosCache.length} certificado${certificadosCache.length !== 1 ? "s" : ""}`;

  if (certificadosCache.length === 0) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1; padding:24px;"><div class="state-icon">📜</div><div class="state-text">Nenhum certificado emitido ainda.</div></div>`;
    return;
  }

  container.innerHTML = certificadosCache.map(c => {
    const data = new Date(c.emitido_em).toLocaleDateString("pt-BR");
    return `
      <div class="cert-card ${c.cancelado ? 'cancelado' : ''}">
        <div class="cert-header">
          <div class="cert-icone">📜</div>
          <div class="cert-corpo">
            <div class="cert-titulo">Certificado de Conclusão</div>
            <div class="cert-aluno">Aluno ID: ${c.pessoa_id.slice(0,8)}</div>
            <div class="cert-codigo">${c.codigo}</div>
          </div>
        </div>
        <div class="cert-meta">
          <span>📅 ${data}</span>
          ${c.carga_horaria ? `<span>⏱️ ${c.carga_horaria}h</span>` : ""}
          ${c.nota_final != null ? `<span>🎯 Nota: ${c.nota_final}</span>` : ""}
        </div>
        <div class="cert-acoes">
          ${c.url_pdf ? `<button class="btn btn-primary" style="padding:6px 12px; font-size:12px;" onclick="baixarCertificadoPDF('${c.codigo}')">⬇ PDF</button>` : ""}
          <button class="btn btn-ghost" style="padding:6px 12px; font-size:12px;" onclick="copiarCodigoCertificado('${c.codigo}')">📋 Copiar código</button>
          ${!c.cancelado ? `<button class="btn btn-danger" style="padding:6px 12px; font-size:12px;" onclick="cancelarCertificado('${c.id}')">✕ Cancelar</button>` : ""}
        </div>
      </div>
    `;
  }).join("");
}

async function abrirFormEmitirCertificado() {
  document.getElementById("form-emitir-certificado").reset();
  const sel = document.getElementById("select-matricula-certificado");
  sel.innerHTML = `<option value="">Carregando matrículas aprovadas...</option>`;
  document.getElementById("modal-emitir-certificado").classList.add("active");

  try {
    const r = await apiFetch(`${API}/estudo/matriculas/?status_=aprovado`);
    if (!r.ok) throw new Error("Erro ao carregar matrículas");
    const mats = await r.json();
    if (mats.length === 0) {
      sel.innerHTML = `<option value="">Nenhuma matrícula aprovada disponível</option>`;
    } else {
      sel.innerHTML = `<option value="">Selecione a matrícula...</option>` +
        mats.map(m => `<option value="${m.id}">${m.pessoa?.nome || "Aluno"} — ${m.status}</option>`).join("");
    }
  } catch (e) {
    sel.innerHTML = `<option value="">Erro: ${e.message}</option>`;
  }
}

function fecharFormEmitirCertificado() {
  document.getElementById("modal-emitir-certificado").classList.remove("active");
}

async function salvarEmitirCertificado(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-emitir-certificado");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Emitindo...";

  const matriculaId = document.getElementById("select-matricula-certificado").value;
  const carga = document.getElementById("input-carga-certificado").value;
  if (!matriculaId) { mostrarToast("❌ Selecione uma matrícula", "error"); btn.disabled=false; btn.textContent=txt; return; }

  try {
    const body = carga ? { carga_horaria: parseInt(carga) } : {};
    const r = await apiFetch(`${API}/estudo/matriculas/${matriculaId}/certificado`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(body),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormEmitirCertificado();
    mostrarToast("🎓 Certificado emitido!", "success");
    carregarCertificados();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

function abrirFormValidarCertificado() {
  document.getElementById("form-validar-certificado").reset();
  document.getElementById("resultado-validacao").innerHTML = "";
  document.getElementById("modal-validar-certificado").classList.add("active");
  document.getElementById("input-codigo-validacao").focus();
}

function fecharFormValidarCertificado() {
  document.getElementById("modal-validar-certificado").classList.remove("active");
}

async function validarCertificado(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-validar-certificado");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Validando...";

  const codigo = document.getElementById("input-codigo-validacao").value.trim().toUpperCase();
  const div = document.getElementById("resultado-validacao");

  try {
    const r = await fetch(`${API}/publico/certificados/validar/${codigo}`);
    const data = await r.json();

    if (r.ok && data.valido) {
      div.innerHTML = `
        <div class="validacao-resultado valido">
          <div class="validacao-status valido">✅ CERTIFICADO VÁLIDO</div>
          <div class="validacao-linha"><span class="validacao-label">Aluno</span><span class="validacao-valor">${data.nome_aluno || "—"}</span></div>
          <div class="validacao-linha"><span class="validacao-label">Curso</span><span class="validacao-valor">${data.nome_curso || "—"}</span></div>
          <div class="validacao-linha"><span class="validacao-label">Igreja</span><span class="validacao-valor">${data.nome_igreja || "—"}</span></div>
          ${data.carga_horaria ? `<div class="validacao-linha"><span class="validacao-label">Carga horária</span><span class="validacao-valor">${data.carga_horaria}h</span></div>` : ""}
          ${data.nota_final != null ? `<div class="validacao-linha"><span class="validacao-label">Nota</span><span class="validacao-valor">${data.nota_final}</span></div>` : ""}
          <div class="validacao-linha"><span class="validacao-label">Emitido em</span><span class="validacao-valor">${new Date(data.emitido_em).toLocaleDateString("pt-BR")}</span></div>
        </div>`;
    } else {
      div.innerHTML = `
        <div class="validacao-resultado invalido">
          <div class="validacao-status invalido">❌ CERTIFICADO INVÁLIDO</div>
          <div style="font-size:13px;">${data.detail || data.mensagem || "Código não encontrado"}</div>
        </div>`;
    }
  } catch (err) {
    div.innerHTML = `<div class="validacao-resultado invalido"><div class="validacao-status invalido">❌ ERRO</div><div>${err.message}</div></div>`;
  } finally { btn.disabled = false; btn.textContent = txt; }
}

function baixarCertificadoPDF(codigo) {
  window.open(`http://127.0.0.1:8000/media/certificados/${codigo}.pdf`, "_blank");
}

function copiarCodigoCertificado(codigo) {
  navigator.clipboard.writeText(codigo).then(() => {
    mostrarToast("📋 Código copiado!", "success");
  }).catch(() => {
    prompt("Copie o código:", codigo);
  });
}

async function cancelarCertificado(id) {
  abrirConfirmar("Cancelar certificado?", "O certificado deixará de ser válido para validação pública.", async () => {
    try {
      const r = await apiFetch(`${API}/estudo/certificados/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Certificado cancelado.", "success");
      carregarCertificados();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

// ============ FERRAMENTAS ============

async function carregarFerramentas() {
  const container = document.getElementById("container-ferramentas");
  if (!container) return;
  container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-text">Carregando ferramentas...</div></div>`;

  try {
    const r = await apiFetch(`${API}/estudo/ferramentas/`);
    ferramentasCache = await r.json();
    renderizarFerramentas();
  } catch (e) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1;"><div class="state-text">${e.message}</div></div>`;
  }
}

function renderizarFerramentas() {
  const container = document.getElementById("container-ferramentas");
  const contador = document.getElementById("contador-ferramentas");
  if (!container) return;

  const cat = document.getElementById("filtro-categoria-ferramenta").value;
  const filtradas = cat ? ferramentasCache.filter(f => f.categoria === cat) : ferramentasCache;

  contador.textContent = `${filtradas.length} ferramenta${filtradas.length !== 1 ? "s" : ""}`;

  if (filtradas.length === 0) {
    container.innerHTML = `<div class="state" style="grid-column: 1/-1; padding:24px;"><div class="state-icon">🔧</div><div class="state-text">Nenhuma ferramenta cadastrada. Clique em "+ Nova Ferramenta" ou recomendamos STEP Bible, Blue Letter Bible, etc.</div></div>`;
    return;
  }

  container.innerHTML = filtradas.map(f => `
    <div class="ferramenta-card" style="position:relative;">
      <div class="ferramenta-icone">${f.icone || "🔗"}</div>
      <div class="ferramenta-corpo">
        <div class="ferramenta-nome">${f.nome}</div>
        ${f.descricao ? `<div class="ferramenta-desc">${f.descricao}</div>` : ""}
        <div class="ferramenta-cat ${f.categoria}">${f.categoria}</div>
      </div>
      <div style="display:flex; flex-direction:column; gap:6px; align-items:flex-end;">
        <a href="${f.url}" target="_blank" class="btn-icon" title="Abrir" style="text-decoration:none;">↗</a>
        <button class="btn-icon danger" onclick="event.stopPropagation(); deletarFerramenta('${f.id}')" title="Excluir">✕</button>
      </div>
    </div>
  `).join("");
}

function abrirFormFerramenta() {
  document.getElementById("form-ferramenta").reset();
  document.querySelector('#form-ferramenta [name="icone"]').value = "🔗";
  document.querySelector('#form-ferramenta [name="ordem"]').value = 1;
  document.getElementById("modal-form-ferramenta").classList.add("active");
  document.querySelector('#form-ferramenta [name="nome"]').focus();
}

function fecharFormFerramenta() {
  document.getElementById("modal-form-ferramenta").classList.remove("active");
}

async function salvarFerramenta(e) {
  e.preventDefault();
  const btn = document.getElementById("btn-salvar-ferramenta");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";

  const dados = {};
  for (const [k, v] of new FormData(e.target).entries()) {
    if (k === "ordem") { dados[k] = parseInt(v) || 1; continue; }
    if (typeof v === "string" && v.trim()) dados[k] = v.trim();
  }

  try {
    const r = await apiFetch(`${API}/estudo/ferramentas/`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(dados),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormFerramenta();
    mostrarToast("✅ Ferramenta criada!", "success");
    carregarFerramentas();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

async function deletarFerramenta(id) {
  abrirConfirmar("Excluir ferramenta?", "Esta ferramenta será removida do catálogo.", async () => {
    try {
      const r = await apiFetch(`${API}/estudo/ferramentas/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Ferramenta removida.", "success");
      carregarFerramentas();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

// ============ ANOTACOES (por modulo) ============

async function abrirAnotacoesModulo(moduloId, moduloTitulo) {
  moduloAtualAnotacoes = moduloId;
  document.getElementById("anotacoes-titulo").textContent = `📝 Anotações — ${moduloTitulo || "Módulo"}`;
  document.getElementById("form-anotacao-id").value = "";
  document.getElementById("input-anotacao-titulo").value = "";
  document.getElementById("input-anotacao-conteudo").value = "";
  document.getElementById("input-anotacao-favorito").checked = false;
  document.getElementById("modal-anotacoes-modulo").classList.add("active");
  await carregarAnotacoesModulo(moduloId);
}

function fecharAnotacoesModulo() {
  document.getElementById("modal-anotacoes-modulo").classList.remove("active");
  moduloAtualAnotacoes = null;
  anotacoesModuloCache = [];
}

async function carregarAnotacoesModulo(moduloId) {
  const div = document.getElementById("anotacoes-lista");
  div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">Carregando...</div></div>`;

  // Precisa do pessoa_id — usa prompt temporário ou um ID fixo em dev
  const pessoaId = prompt("ID da pessoa (deixe vazio para ver apenas)"); // simplificado
  if (!pessoaId) {
    div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">Informe o ID da pessoa para ver suas anotações.</div></div>`;
    return;
  }

  try {
    const r = await apiFetch(`${API}/estudo/pessoas/${pessoaId}/anotacoes/?modulo_id=${moduloId}`);
    anotacoesModuloCache = await r.json();
    renderizarAnotacoesModulo();
  } catch (e) {
    div.innerHTML = `<div class="state" style="padding:16px;"><div class="state-text">${e.message}</div></div>`;
  }
}

function renderizarAnotacoesModulo() {
  const div = document.getElementById("anotacoes-lista");
  if (anotacoesModuloCache.length === 0) {
    div.innerHTML = `<div class="state" style="padding:20px;"><div class="state-icon">📝</div><div class="state-text">Nenhuma anotação ainda. Crie a primeira abaixo.</div></div>`;
    return;
  }

  div.innerHTML = anotacoesModuloCache.map(a => {
    const data = new Date(a.updated_at).toLocaleDateString("pt-BR");
    return `
      <div class="anotacao-item ${a.favorito ? 'favorito' : ''}">
        <div class="anotacao-header">
          <div class="anotacao-titulo">${a.favorito ? "⭐ " : ""}${a.titulo}</div>
          <div class="anotacao-data">${data}</div>
        </div>
        <div class="anotacao-conteudo">${a.conteudo}</div>
        <div class="anotacao-acoes">
          <button class="btn-icon" onclick="toggleFavoritoAnotacao('${a.id}', ${!a.favorito})" title="Favoritar">⭐</button>
          <button class="btn-icon" onclick="editarAnotacaoModulo('${a.id}')" title="Editar">✏</button>
          <button class="btn-icon danger" onclick="deletarAnotacaoModulo('${a.id}')" title="Excluir">✕</button>
        </div>
      </div>
    `;
  }).join("");
}

async function salvarAnotacaoModulo(e) {
  e.preventDefault();
  if (!moduloAtualAnotacoes) return;

  const btn = document.getElementById("btn-salvar-anotacao");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Salvando...";

  const id = document.getElementById("form-anotacao-id").value;
  const titulo = document.getElementById("input-anotacao-titulo").value.trim();
  const conteudo = document.getElementById("input-anotacao-conteudo").value.trim();
  const favorito = document.getElementById("input-anotacao-favorito").checked;

  const pessoaId = prompt("ID da pessoa (para criar/editar):");
  if (!pessoaId) { btn.disabled=false; btn.textContent=txt; return; }

  try {
    let r;
    if (id) {
      r = await apiFetch(`${API}/estudo/anotacoes/${id}`, {
        method: "PUT",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ titulo, conteudo, favorito }),
      });
    } else {
      r = await apiFetch(`${API}/estudo/pessoas/${pessoaId}/anotacoes/`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ modulo_id: moduloAtualAnotacoes, titulo, conteudo, favorito }),
      });
    }
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }

    document.getElementById("form-anotacao-id").value = "";
    document.getElementById("input-anotacao-titulo").value = "";
    document.getElementById("input-anotacao-conteudo").value = "";
    document.getElementById("input-anotacao-favorito").checked = false;
    mostrarToast("✅ Anotação salva!", "success");
    await carregarAnotacoesModulo(moduloAtualAnotacoes);
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}

function editarAnotacaoModulo(id) {
  const a = anotacoesModuloCache.find(x => x.id === id);
  if (!a) return;
  document.getElementById("form-anotacao-id").value = a.id;
  document.getElementById("input-anotacao-titulo").value = a.titulo;
  document.getElementById("input-anotacao-conteudo").value = a.conteudo;
  document.getElementById("input-anotacao-favorito").checked = a.favorito;
}

async function toggleFavoritoAnotacao(id, valor) {
  try {
    const r = await apiFetch(`${API}/estudo/anotacoes/${id}`, {
      method: "PUT",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ favorito: valor }),
    });
    if (!r.ok) throw new Error("Erro");
    await carregarAnotacoesModulo(moduloAtualAnotacoes);
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
}

async function deletarAnotacaoModulo(id) {
  abrirConfirmar("Excluir anotação?", "Esta anotação será removida permanentemente.", async () => {
    try {
      const r = await apiFetch(`${API}/estudo/anotacoes/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) throw new Error("Erro");
      mostrarToast("✅ Anotação removida.", "success");
      await carregarAnotacoesModulo(moduloAtualAnotacoes);
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}
'''

if "// ============ ESTUDO BL 4 — CERTIFICADOS ============" not in conteudo:
    marcador = "// ============ GAMIFICACAO ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)
        print("  [OK] JS de certificados + ferramentas + anotacoes adicionado")

# ============================================================
# 6. Atualizar trocarSubAbaEstudo
# ============================================================
import re
novo_sub = '''function trocarSubAbaEstudo(sub) {
  document.querySelectorAll(".estudo-sub-aba").forEach(b => b.classList.toggle("ativa", b.dataset.subtab === sub));
  const tabs = ["catalogo", "turmas", "quizzes", "forum", "gamificacao", "certificados", "ferramentas"];
  for (const t of tabs) {
    const el = document.getElementById("estudo-sub-" + t);
    if (el) el.style.display = sub === t ? "block" : "none";
  }
  if (sub === "catalogo") carregarTrilhasEstudo();
  else if (sub === "turmas") carregarTurmas();
  else if (sub === "gamificacao") carregarGamificacao();
  else if (sub === "certificados") carregarCertificados();
  else if (sub === "ferramentas") carregarFerramentas();
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
print("Aba Estudo -> sub-abas Certificados e Ferramentas")
print("=" * 60)