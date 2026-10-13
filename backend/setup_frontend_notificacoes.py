"""Adiciona sininho de notificacoes no header do frontend."""
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
  /* ============ NOTIFICACOES ============ */
  .sino-wrapper { position: relative; }
  .sino-btn {
    position: relative;
    background: var(--bg-card); border: 1px solid var(--border);
    color: var(--text-muted); width: 36px; height: 36px;
    border-radius: 50%; font-size: 16px; cursor: pointer;
    display: grid; place-items: center;
    transition: all 0.15s;
  }
  .sino-btn:hover { color: var(--text); border-color: var(--text-muted); }
  .sino-badge {
    position: absolute; top: -4px; right: -4px;
    background: var(--danger); color: white;
    font-size: 10px; font-weight: 700;
    min-width: 18px; height: 18px;
    border-radius: 9px; padding: 0 5px;
    display: grid; place-items: center;
    border: 2px solid var(--bg);
    animation: pulsar 2s ease-in-out infinite;
  }
  @keyframes pulsar {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }

  .sino-dropdown {
    position: absolute; top: calc(100% + 12px); right: 0;
    width: 380px; max-height: 500px; overflow-y: auto;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    padding: 0;
    display: none;
    z-index: 500;
  }
  .sino-dropdown.active { display: block; }

  .sino-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: center;
    position: sticky; top: 0;
    background: var(--bg-card);
    border-radius: 14px 14px 0 0;
    z-index: 1;
  }
  .sino-header-titulo { font-size: 15px; font-weight: 700; }
  .sino-header-total {
    font-size: 11px; color: var(--text-muted);
    background: var(--bg); padding: 2px 8px; border-radius: 10px;
  }

  .sino-grupo { padding: 12px 0; border-bottom: 1px solid var(--border); }
  .sino-grupo:last-child { border-bottom: none; }
  .sino-grupo-titulo {
    font-size: 11px; font-weight: 700; color: var(--text-muted);
    text-transform: uppercase; letter-spacing: 0.5px;
    padding: 0 20px 8px;
    display: flex; align-items: center; gap: 8px;
  }
  .sino-item {
    padding: 10px 20px;
    display: flex; align-items: center; gap: 12px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .sino-item:hover { background: var(--bg-card-hover); }
  .sino-item-icon { font-size: 18px; width: 32px; text-align: center; flex-shrink: 0; }
  .sino-item-corpo { flex: 1; min-width: 0; }
  .sino-item-titulo {
    font-size: 13px; font-weight: 600;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    display: flex; align-items: center; gap: 6px;
  }
  .sino-item-sub {
    font-size: 11px; color: var(--text-muted);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .sino-item-dias {
    font-size: 11px; font-weight: 600;
    padding: 3px 8px; border-radius: 6px;
    white-space: nowrap; flex-shrink: 0;
  }
  .sino-item-dias.urgente { background: rgba(239,68,68,0.15); color: var(--danger); }
  .sino-item-dias.atencao { background: rgba(245,158,11,0.15); color: var(--warning); }
  .sino-item-dias.ok { background: rgba(99,102,241,0.15); color: var(--accent); }

  .sino-vazio {
    padding: 48px 24px; text-align: center; color: var(--text-muted);
  }
  .sino-vazio-icon { font-size: 42px; margin-bottom: 12px; opacity: 0.4; }
  .sino-vazio-text { font-size: 14px; }
'''

if ".sino-wrapper" not in conteudo:
    conteudo = conteudo.replace("  @media (max-width: 640px) {", css + "\n  @media (max-width: 640px) {", 1)

# ============================================================
# 2. Adicionar o sino no header (antes do theme-toggle)
# ============================================================
sino_html = '''<div class="sino-wrapper" id="sino-wrapper">
        <button class="sino-btn" onclick="toggleSino(event)" id="sino-btn" title="Notificações">
          🔔
          <span class="sino-badge" id="sino-badge" style="display:none;">0</span>
        </button>
        <div class="sino-dropdown" id="sino-dropdown">
          <div class="sino-header">
            <div class="sino-header-titulo">Notificações</div>
            <div class="sino-header-total" id="sino-total">0</div>
          </div>
          <div id="sino-conteudo"></div>
        </div>
      </div>
      <button class="theme-toggle" onclick="toggleTema()" title="Alternar tema">🌙</button>'''

if 'id="sino-btn"' not in conteudo:
    marcador = '<button class="theme-toggle" onclick="toggleTema()" title="Alternar tema">🌙</button>'
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, sino_html, 1)

# ============================================================
# 3. JS
# ============================================================
js = '''
// ============ NOTIFICACOES ============
let notificacoesCache = null;
let sinoAberto = false;

const NOTIF_META = {
  acompanhamento_vencido: { icon: "🕊️", grupo: "Acompanhamentos vencidos", cor: "urgente" },
  retorno_proximo:        { icon: "📅", grupo: "Retornos próximos",       cor: "atencao" },
  pessoa_sem_interacao:   { icon: "⏰", grupo: "Sem interação",           cor: "urgente" },
  pedido_sem_resposta:    { icon: "🙏", grupo: "Pedidos sem resposta",    cor: "atencao" },
};

async function carregarNotificacoes() {
  const badge = document.getElementById("sino-badge");
  if (!badge) return;

  try {
    const r = await apiFetch(`${API}/notificacoes/`);
    if (!r.ok) return;
    notificacoesCache = await r.json();

    // Atualiza badge
    if (notificacoesCache.total > 0) {
      badge.textContent = notificacoesCache.total > 99 ? "99+" : notificacoesCache.total;
      badge.style.display = "grid";
    } else {
      badge.style.display = "none";
    }

    // Se o dropdown estiver aberto, re-renderiza
    if (sinoAberto) renderizarSino();
  } catch (e) { /* silencioso */ }
}

function toggleSino(e) {
  e.stopPropagation();
  const dd = document.getElementById("sino-dropdown");
  sinoAberto = !sinoAberto;
  if (sinoAberto) {
    renderizarSino();
    dd.classList.add("active");
  } else {
    dd.classList.remove("active");
  }
}

function fecharSino() {
  const dd = document.getElementById("sino-dropdown");
  if (dd) dd.classList.remove("active");
  sinoAberto = false;
}

function renderizarSino() {
  const conteudo = document.getElementById("sino-conteudo");
  const total = document.getElementById("sino-total");
  if (!conteudo || !notificacoesCache) return;

  total.textContent = `${notificacoesCache.total} item${notificacoesCache.total !== 1 ? "s" : ""}`;

  if (notificacoesCache.total === 0) {
    conteudo.innerHTML = `
      <div class="sino-vazio">
        <div class="sino-vazio-icon">✓</div>
        <div class="sino-vazio-text">Tudo em ordem!<br>Nenhuma pendência no momento.</div>
      </div>`;
    return;
  }

  // Agrupa por tipo
  const grupos = {};
  for (const item of notificacoesCache.itens) {
    const meta = NOTIF_META[item.tipo] || { grupo: "Outros", icon: "📌", cor: "ok" };
    if (!grupos[item.tipo]) grupos[item.tipo] = { meta, itens: [] };
    grupos[item.tipo].itens.push(item);
  }

  let html = "";
  for (const tipo in grupos) {
    const g = grupos[tipo];
    html += `<div class="sino-grupo">
      <div class="sino-grupo-titulo">${g.meta.icon} ${g.meta.grupo} (${g.itens.length})</div>
      ${g.itens.map(item => {
        const corClass = g.meta.cor;
        const diasLabel = item.dias > 0 ? `${item.dias}d` : "hoje";
        return `<div class="sino-item" onclick="irParaNotificacao('${item.aba_destino}', '${item.tipo}')">
          <div class="sino-item-icon">${g.meta.icon}</div>
          <div class="sino-item-corpo">
            <div class="sino-item-titulo">
              ${item.titulo}
              ${item.sigiloso ? '<span class="card-tag" style="background:rgba(239,68,68,0.15);color:var(--danger);font-size:9px;">SIGILOSO</span>' : ""}
            </div>
            <div class="sino-item-sub">${item.subtitulo || "—"}</div>
          </div>
          <div class="sino-item-dias ${corClass}">${diasLabel}</div>
        </div>`;
      }).join("")}
    </div>`;
  }

  conteudo.innerHTML = html;
}

function irParaNotificacao(aba, tipo) {
  fecharSino();

  // Vai para a aba
  trocarAba(aba);

  // Aplica filtro após a aba carregar
  setTimeout(() => {
    if (aba === "cuidado") {
      if (tipo === "acompanhamento_vencido") {
        document.getElementById("filtro-vencidos-acomp").checked = true;
        carregarAcompanhamentos();
      } else if (tipo === "retorno_proximo") {
        document.getElementById("filtro-vencidos-acomp").checked = false;
        document.getElementById("mostrar-concluidos-acomp").checked = false;
        carregarAcompanhamentos();
      }
    } else if (aba === "oracao") {
      document.getElementById("filtro-status-oracao").value = "aberto";
      carregarOracoes();
    }
    // aba "pessoas" — sem filtro específico
  }, 300);
}

// Fecha o dropdown ao clicar fora
document.addEventListener("click", (e) => {
  const wrapper = document.getElementById("sino-wrapper");
  if (wrapper && !wrapper.contains(e.target)) {
    fecharSino();
  }
});

// Polling a cada 60s
setInterval(() => {
  if (getToken()) carregarNotificacoes();
}, 60000);
'''

if "// ============ NOTIFICACOES ============" not in conteudo:
    marcador = "// ============ CONFIRMAR ============"
    if marcador in conteudo:
        conteudo = conteudo.replace(marcador, js + "\n" + marcador, 1)

# ============================================================
# 4. Chamar carregarNotificacoes() ao logar / abrir app
# ============================================================
if "carregarNotificacoes();" not in conteudo.split("function mostrarApp")[1][:800]:
    # Adiciona no final do mostrarApp, depois do trocarAba
    conteudo = conteudo.replace(
        'trocarAba("inicio");\n}',
        'trocarAba("inicio");\n  carregarNotificacoes();\n}',
        1,
    )

INDEX.write_text(conteudo, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(conteudo)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e Ctrl+Shift+R.")
print("=" * 60)