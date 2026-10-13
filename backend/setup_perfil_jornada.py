"""Adiciona aba Jornada no perfil da pessoa + botao iniciar trilha."""
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
# 1. CSS adicional
# ============================================================
css = '''
  /* ============ JORNADA NO PERFIL ============ */
  .jornada-item {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px; margin-bottom: 14px;
  }
  .jornada-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    gap: 16px; margin-bottom: 14px;
  }
  .jornada-titulo {
    font-size: 16px; font-weight: 700;
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  }
  .jornada-status {
    font-size: 11px; font-weight: 700;
    padding: 4px 10px; border-radius: 6px;
    text-transform: uppercase; letter-spacing: 0.5px;
    white-space: nowrap;
  }
  .jornada-status.em_andamento { background: rgba(99,102,241,0.15); color: var(--accent); }
  .jornada-status.concluida    { background: rgba(16,185,129,0.15); color: var(--success); }
  .jornada-status.cancelada    { background: rgba(239,68,68,0.15); color: var(--danger); }

  .progress-bar {
    width: 100%; height: 8px;
    background: var(--bg); border-radius: 999px;
    overflow: hidden; margin-bottom: 14px;
  }
  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), #8b5cf6);
    border-radius: 999px;
    transition: width 0.3s ease;
  }
  .progress-labels {
    display: flex; justify-content: space-between;
    font-size: 11px; color: var(--text-muted);
    margin-top: -10px; margin-bottom: 16px;
  }

  .checklist { display: flex; flex-direction: column; gap: 8px; }
  .checklist-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    background: var(--bg); border: 1px solid var(--border);
    border-radius: 10px;
    cursor: pointer; transition: all 0.15s;
  }
  .checklist-item:hover { border-color: var(--accent); background: var(--bg-card-hover); }
  .checklist-item.concluida { opacity: 0.75; }
  .checklist-checkbox {
    width: 24px; height: 24px;
    border: 2px solid var(--border);
    border-radius: 6px;
    display: grid; place-items: center;
    font-size: 14px; font-weight: 700;
    color: transparent;
    flex-shrink: 0;
    transition: all 0.15s;
  }
  .checklist-item.concluida .checklist-checkbox {
    background: var(--success);
    border-color: var(--success);
    color: white;
  }
  .checklist-corpo { flex: 1; }
  .checklist-nome { font-size: 14px; font-weight: 600; }
  .checklist-item.concluida .checklist-nome { text-decoration: line-through; color: var(--text-muted); }
  .checklist-meta { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

  .jornada-acoes {
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-top: 14px; padding-top: 14px;
    border-top: 1px solid var(--border);
  }
'''

if ".jornada-item" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Modais
# ============================================================
modais = '''
<!-- Iniciar trilha (do perfil da pessoa) -->
<div class="modal-backdrop" id="modal-iniciar-trilha">
  <div class="modal" style="max-width: 460px;">
    <div class="modal-header">
      <h2 class="modal-title">Iniciar nova trilha</h2>
      <button class="modal-close" onclick="fecharFormIniciarTrilha()">×</button>
    </div>
    <div class="alerta-info" id="iniciar-trilha-info">Selecione a trilha que deseja iniciar.</div>
    <form id="form-iniciar-trilha" onsubmit="salvarIniciarTrilha(event)">
      <div class="form-group">
        <label class="form-label">Trilha *</label>
        <select class="form-select" id="select-trilha-iniciar" required></select>
      </div>
      <div class="form-group">
        <label class="form-label">Observações</label>
        <textarea class="form-input" id="iniciar-trilha-obs" rows="2" style="font-family:inherit; resize:vertical;" placeholder="Opcional"></textarea>
      </div>
      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick="fecharFormIniciarTrilha()">Cancelar</button>
        <button type="submit" class="btn btn-primary" id="btn-iniciar-trilha">Iniciar</button>
      </div>
    </form>
  </div>
</div>
'''

if 'id="modal-iniciar-trilha"' not in conteudo:
    marcador = '<div class="modal-backdrop" id="modal-confirmar">'
    conteudo = conteudo.replace(marcador, modais + "\n" + marcador, 1)

# ============================================================
# 3. JS — perfil jornada + iniciar trilha
# ============================================================
js = '''
// ============ PERFIL: JORNADA ============
let trilhasDisponiveis = [];

async function carregarPerfilJornada() {
  const div = document.getElementById("perfil-jornada-corpo");
  if (!div || !pessoaPerfilAtual) return;

  div.innerHTML = `<div class="state"><div class="state-icon">⏳</div><div class="state-text">Carregando jornadas...</div></div>`;

  try {
    const r = await apiFetch(`${API}/jornada/progressos/?pessoa_id=${pessoaPerfilAtual.id}&limit=1000`);
    const progressos = await r.json();

    if (progressos.length === 0) {
      div.innerHTML = `
        <div class="state">
          <div class="state-icon">🎯</div>
          <div class="state-text">Esta pessoa ainda não está em nenhuma trilha.</div>
          <button class="btn btn-primary" style="margin-top:16px;" onclick="abrirFormIniciarTrilha()">+ Iniciar primeira trilha</button>
        </div>`;
      return;
    }

    div.innerHTML = progressos.map(p => renderJornadaItem(p)).join("");
    div.innerHTML += `<button class="btn btn-primary" style="margin-top:16px;" onclick="abrirFormIniciarTrilha()">+ Iniciar nova trilha</button>`;
  } catch (e) {
    div.innerHTML = `<div class="state"><div class="state-icon">⚠️</div><div class="state-text">${e.message}</div></div>`;
  }
}

function renderJornadaItem(p) {
  const trilhaNome = p.trilha?.nome || "Trilha";
  const tipoLabel = { batismo: "💧", discipulado: "📖", lideranca: "👑", outro: "📌" };
  const tipoIcon = tipoLabel[p.trilha?.tipo] || "🎯";

  const total = p.total_etapas || 0;
  const concluidas = p.etapas_concluidas || 0;
  const pct = p.progresso_percentual || 0;
  const statusLabel = { em_andamento: "Em andamento", concluida: "Concluída", cancelada: "Cancelada" };

  const etapasHtml = (p.etapas || []).map(pe => {
    const etapaNome = pe.etapa?.nome || "Etapa";
    const obrigatoria = pe.etapa?.obrigatoria;
    const tag = obrigatoria ? "" : ' <span class="etapa-tag opcional">OPCIONAL</span>';
    const data = pe.concluida && pe.concluida_em ? `<div class="checklist-meta">✓ ${new Date(pe.concluida_em + "T00:00:00").toLocaleDateString("pt-BR")}</div>` : "";
    return `
      <div class="checklist-item ${pe.concluida ? "concluida" : ""}" onclick="toggleEtapaJornada('${p.id}', '${pe.etapa_id}', ${!pe.concluida})">
        <div class="checklist-checkbox">✓</div>
        <div class="checklist-corpo">
          <div class="checklist-nome">${etapaNome}${tag}</div>
          ${data}
        </div>
      </div>`;
  }).join("");

  const acoes = [];
  if (p.status === "em_andamento") {
    acoes.push(`<button class="btn btn-success" onclick="concluirJornada('${p.id}')">✓ Concluir trilha</button>`);
    acoes.push(`<button class="btn btn-warning" onclick="cancelarJornada('${p.id}')">Cancelar</button>`);
  } else if (p.status === "cancelada") {
    acoes.push(`<button class="btn btn-primary" onclick="concluirJornada('${p.id}')">Reativar como concluída</button>`);
  }
  acoes.push(`<button class="btn btn-danger" onclick="deletarJornada('${p.id}')">Excluir</button>`);

  return `
    <div class="jornada-item">
      <div class="jornada-header">
        <div class="jornada-titulo">${tipoIcon} ${trilhaNome}</div>
        <div class="jornada-status ${p.status}">${statusLabel[p.status] || p.status}</div>
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width: ${pct}%;"></div></div>
      <div class="progress-labels">
        <span>${concluidas} de ${total} etapas</span>
        <span>${pct}%</span>
      </div>
      <div class="checklist">${etapasHtml}</div>
      <div class="jornada-acoes">${acoes.join("")}</div>
    </div>
  `;
}

async function toggleEtapaJornada(progressoId, etapaId, concluir) {
  try {
    const r = await apiFetch(`${API}/jornada/progressos/${progressoId}/etapas/${etapaId}`, {
      method: "PATCH",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ concluida: concluir }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    mostrarToast(concluir ? "✅ Etapa concluída!" : "↩ Etapa desmarcada", "success");
    await carregarPerfilJornada();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
}

function confirmarAcao(titulo, msg, cb) {
  abrirConfirmar(titulo, msg, cb);
}

async function concluirJornada(id) {
  confirmarAcao("Concluir trilha?", "Marcar como concluída manualmente?", async () => {
    try {
      const r = await apiFetch(`${API}/jornada/progressos/${id}/concluir`, { method: "PATCH" });
      if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Trilha concluída!", "success");
      await carregarPerfilJornada();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

async function cancelarJornada(id) {
  confirmarAcao("Cancelar trilha?", "A pessoa deixa de fazer esta trilha.", async () => {
    try {
      const r = await apiFetch(`${API}/jornada/progressos/${id}/cancelar`, { method: "PATCH" });
      if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Trilha cancelada.", "success");
      await carregarPerfilJornada();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

async function deletarJornada(id) {
  confirmarAcao("Excluir progresso?", "Remove a pessoa desta trilha completamente. Não pode ser desfeito.", async () => {
    try {
      const r = await apiFetch(`${API}/jornada/progressos/${id}`, { method: "DELETE" });
      if (!r.ok && r.status !== 204) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
      mostrarToast("✅ Progresso removido.", "success");
      await carregarPerfilJornada();
    } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  });
}

// ============ INICIAR TRILHA ============

async function abrirFormIniciarTrilha() {
  if (!pessoaPerfilAtual) return;
  document.getElementById("form-iniciar-trilha").reset();
  document.getElementById("iniciar-trilha-info").innerHTML =
    `Iniciar uma trilha para <strong>${pessoaPerfilAtual.nome}</strong>.`;
  // Carrega trilhas ativas
  try {
    const r = await apiFetch(`${API}/jornada/trilhas/?apenas_ativas=true&limit=1000`);
    trilhasDisponiveis = await r.json();
    const sel = document.getElementById("select-trilha-iniciar");
    if (trilhasDisponiveis.length === 0) {
      sel.innerHTML = '<option value="">Nenhuma trilha ativa disponível</option>';
    } else {
      sel.innerHTML = '<option value="">Selecione a trilha...</option>' +
        trilhasDisponiveis.map(t => `<option value="${t.id}">${t.nome} (${t.etapas?.length || 0} etapas)</option>`).join("");
    }
  } catch (e) { /* silencioso */ }

  document.getElementById("modal-iniciar-trilha").classList.add("active");
}

function fecharFormIniciarTrilha() {
  document.getElementById("modal-iniciar-trilha").classList.remove("active");
}

async function salvarIniciarTrilha(e) {
  e.preventDefault();
  if (!pessoaPerfilAtual) return;
  const btn = document.getElementById("btn-iniciar-trilha");
  btn.disabled = true; const txt = btn.textContent; btn.textContent = "Iniciando...";
  const trilhaId = document.getElementById("select-trilha-iniciar").value;
  const obs = document.getElementById("iniciar-trilha-obs").value.trim();
  if (!trilhaId) {
    mostrarToast("❌ Selecione uma trilha", "error");
    btn.disabled = false; btn.textContent = txt;
    return;
  }
  try {
    const r = await apiFetch(`${API}/jornada/progressos/`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        pessoa_id: pessoaPerfilAtual.id,
        trilha_id: trilhaId,
        observacoes: obs || null,
      }),
    });
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail || "Erro"); }
    fecharFormIniciarTrilha();
    mostrarToast("✅ Trilha iniciada!", "success");
    await carregarPerfilJornada();
  } catch (err) { mostrarToast("❌ " + err.message, "error"); }
  finally { btn.disabled = false; btn.textContent = txt; }
}
'''

if "// ============ PERFIL: JORNADA ============" not in conteudo:
    marcador = "// ============ NOTIFICACOES ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)

# ============================================================
# 4. Adicionar aba Jornada dentro do modal de perfil
# ============================================================
# Vamos alterar o HTML do container do perfil
old_tabs = '''<div class="perfil-abas" style="margin-top: 24px;">
      <button class="perfil-aba ${perfilAbaAtiva === "info" ? "ativa" : ""}" onclick="mudarAbaPerfil('info')">📋 Informações</button>
      <button class="perfil-aba ${perfilAbaAtiva === "acomp" ? "ativa" : ""}" onclick="mudarAbaPerfil('acomp')">🕊️ Acompanhamentos (${p.acompanhamentos.length})</button>
    </div>'''

new_tabs = '''<div class="perfil-abas" style="margin-top: 24px;">
      <button class="perfil-aba ${perfilAbaAtiva === "info" ? "ativa" : ""}" onclick="mudarAbaPerfil('info')">📋 Informações</button>
      <button class="perfil-aba ${perfilAbaAtiva === "acomp" ? "ativa" : ""}" onclick="mudarAbaPerfil('acomp')">🕊️ Acompanhamentos (${p.acompanhamentos.length})</button>
      <button class="perfil-aba ${perfilAbaAtiva === "jornada" ? "ativa" : ""}" onclick="mudarAbaPerfil('jornada')">🎯 Jornada</button>
    </div>'''

if "mudarAbaPerfil('jornada')" not in conteudo and old_tabs in conteudo:
    conteudo = conteudo.replace(old_tabs, new_tabs, 1)
    print("  [OK] Aba Jornada adicionada ao perfil")

# ============================================================
# 5. Atualizar renderizarCorpoPerfil para lidar com "jornada"
# ============================================================
old_render = '''  if (perfilAbaAtiva === "acomp") {
    if (p.acompanhamentos.length === 0) {'''
new_render = '''  if (perfilAbaAtiva === "jornada") {
    corpo.innerHTML = `<div id="perfil-jornada-corpo"></div>`;
    carregarPerfilJornada();
    return;
  }

  if (perfilAbaAtiva === "acomp") {
    if (p.acompanhamentos.length === 0) {'''

if "carregarPerfilJornada" not in conteudo.split("function renderizarCorpoPerfil")[1][:2000] if "function renderizarCorpoPerfil" in conteudo else False:
    if old_render in conteudo:
        conteudo = conteudo.replace(old_render, new_render, 1)
        print("  [OK] renderizarCorpoPerfil atualizado")

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("Abra uma pessoa -> aba Jornada.")
print("=" * 60)