"""Frontend de aniversariantes: card no dashboard + badge no sino + 🎂 no card."""
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
# 1. CSS para aniversariantes
# ============================================================
css = '''
  /* ============ ANIVERSARIANTES ============ */
  .aniv-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
  }
  .aniv-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 16px;
    display: flex;
    gap: 14px;
    align-items: center;
    transition: all 0.2s;
  }
  .aniv-card:hover { transform: translateY(-2px); border-color: var(--accent); }
  .aniv-card.hoje {
    background: linear-gradient(135deg, rgba(236,72,153,0.15), rgba(139,92,246,0.15));
    border-color: rgba(236,72,153,0.4);
  }
  .aniv-avatar {
    width: 48px; height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent), #ec4899);
    display: grid; place-items: center;
    font-size: 16px; font-weight: 700; color: white;
    flex-shrink: 0;
    position: relative;
  }
  .aniv-card.hoje .aniv-avatar::after {
    content: "🎂";
    position: absolute;
    top: -6px; right: -6px;
    font-size: 18px;
  }
  .aniv-info { flex: 1; min-width: 0; }
  .aniv-nome { font-size: 14px; font-weight: 700; margin-bottom: 2px; }
  .aniv-data { font-size: 12px; color: var(--text-muted); }
  .aniv-dias {
    font-size: 11px; font-weight: 700;
    padding: 4px 10px;
    border-radius: 999px;
    white-space: nowrap;
  }
  .aniv-dias.hoje    { background: rgba(236,72,153,0.2); color: #f472b6; }
  .aniv-dias.futuro  { background: rgba(99,102,241,0.15); color: var(--accent); }
  .aniv-dias.passado { background: rgba(139,149,168,0.15); color: var(--text-muted); }

  .aniv-secao-titulo {
    font-size: 15px; font-weight: 700;
    margin: 20px 0 12px;
    display: flex; align-items: center; gap: 8px;
  }

  .aniv-empty {
    padding: 24px;
    text-align: center;
    color: var(--text-muted);
    background: var(--bg-card);
    border: 1px dashed var(--border);
    border-radius: 14px;
    font-size: 13px;
    margin-bottom: 24px;
  }
'''

if ".aniv-grid" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Adicionar bloco de aniversariantes no dashboard (aba Início)
# ============================================================
# Insere depois dos gráficos, antes da timeline
marcador_timeline = '<div class="timeline-titulo">📋 Atividades recentes</div>'
bloco_aniv = '''<div id="dashboard-aniversariantes"></div>

      <div class="timeline-titulo">📋 Atividades recentes</div>'''

if 'id="dashboard-aniversariantes"' not in conteudo and marcador_timeline in conteudo:
    conteudo = conteudo.replace(marcador_timeline, bloco_aniv, 1)

# ============================================================
# 3. JS
# ============================================================
js = '''
// ============ ANIVERSARIANTES ============
let aniversariantesCache = null;

async function carregarAniversariantes() {
  const div = document.getElementById("dashboard-aniversariantes");
  if (!div) return;

  try {
    const r = await apiFetch(`${API}/pessoas/aniversariantes/`);
    if (!r.ok) return;
    aniversariantesCache = await r.json();
    renderizarAniversariantes();
  } catch (e) { /* silencioso */ }
}

function renderizarAniversariantes() {
  const div = document.getElementById("dashboard-aniversariantes");
  if (!div || !aniversariantesCache) return;

  const d = aniversariantesCache;
  const total = d.total_hoje + d.total_semana + d.ultimos_7_dias.length;

  if (total === 0) {
    div.innerHTML = `
      <div class="aniv-secao-titulo">🎂 Aniversariantes</div>
      <div class="aniv-empty">Nenhum aniversariante nos próximos 7 dias. Cadastre a data de nascimento das pessoas para ver aqui.</div>`;
    return;
  }

  let html = "";

  // Hoje
  if (d.hoje.length > 0) {
    html += `<div class="aniv-secao-titulo">🎉 Aniversariantes de hoje</div><div class="aniv-grid">`;
    for (const p of d.hoje) {
      html += renderAnivCard(p, "hoje");
    }
    html += `</div>`;
  }

  // Próximos 7 dias
  if (d.proximos_7_dias.length > 0) {
    html += `<div class="aniv-secao-titulo">🎂 Próximos 7 dias</div><div class="aniv-grid">`;
    for (const p of d.proximos_7_dias) {
      html += renderAnivCard(p, "futuro");
    }
    html += `</div>`;
  }

  // Últimos 7 dias
  if (d.ultimos_7_dias.length > 0) {
    html += `<div class="aniv-secao-titulo">📅 Fizeram nos últimos 7 dias</div><div class="aniv-grid">`;
    for (const p of d.ultimos_7_dias) {
      html += renderAnivCard(p, "passado");
    }
    html += `</div>`;
  }

  div.innerHTML = html;
}

function renderAnivCard(p, tipo) {
  const iniciais = p.nome.split(" ").slice(0, 2).map(s => s[0]).join("").toUpperCase();
  const dn = new Date(p.data_nascimento + "T00:00:00");
  const dataFmt = dn.toLocaleDateString("pt-BR", { day: "2-digit", month: "long" });

  let diasLabel = "";
  if (p.dias_ate === 0) diasLabel = "HOJE 🎉";
  else if (p.dias_ate > 0) diasLabel = `Em ${p.dias_ate} dia${p.dias_ate !== 1 ? "s" : ""}`;
  else diasLabel = `Há ${Math.abs(p.dias_ate)} dia${Math.abs(p.dias_ate) !== 1 ? "s" : ""}`;

  return `
    <div class="aniv-card ${tipo === 'hoje' ? 'hoje' : ''}" onclick="abrirPerfilPessoa('${p.id}')" style="cursor:pointer;">
      <div class="aniv-avatar">${iniciais}</div>
      <div class="aniv-info">
        <div class="aniv-nome">${p.nome}</div>
        <div class="aniv-data">${dataFmt} · ${p.idade} anos</div>
      </div>
      <div class="aniv-dias ${tipo}">${diasLabel}</div>
    </div>
  `;
}

// ============ BADGE NO SINO (integra com notificacoes) ============
async function carregarBadgeAniversariantes() {
  const badge = document.getElementById("sino-badge");
  if (!badge || !aniversariantesCache) return;

  const totalHoje = aniversariantesCache.total_hoje;

  // Se já tem badge de notificações, soma (não substitui)
  if (totalHoje > 0) {
    const atual = parseInt(badge.textContent) || 0;
    const novo = atual + totalHoje;
    badge.textContent = novo > 99 ? "99+" : novo;
    badge.style.display = "grid";
  }
}
'''

if "// ============ ANIVERSARIANTES ============" not in conteudo:
    marcador = "// ============ PERFIL: JORNADA ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)

# ============================================================
# 4. Adicionar chamada no carregarDashboard
# ============================================================
# Dentro de carregarDashboard, depois de desenhar graficos e timeline
conteudo = conteudo.replace(
    "carregarAlertasOracao();",
    "carregarAlertasOracao();\n    carregarAniversariantes();",
    1,
)

# Se não achou o carregarAlertasOracao, tenta outro ponto
if "carregarAniversariantes();" not in conteudo.split("async function carregarDashboard")[1][:3000] if "async function carregarDashboard" in conteudo else False:
    # Adiciona no final de carregarDashboard
    conteudo = conteudo.replace(
        "desenharGraficoOracao(d);",
        "desenharGraficoOracao(d);\n    carregarAniversariantes();",
        1,
    )

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("=" * 60)