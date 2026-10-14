"""Adiciona responsividade mobile: menu hamburger + grids adaptáveis."""
import re
import shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
FRONTEND_WEB = PROJETO / "frontend" / "web"
INDEX = FRONTEND_WEB / "index.html"

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

print(f"Frontend: {FRONTEND_WEB}")

# Limpa backups antigos
for b in FRONTEND_WEB.glob("index.html.bak.*"):
    b.unlink()
    print(f"  [DEL] {b.name}")

# Backup
if INDEX.exists():
    backup = INDEX.with_suffix(f".html.bak.{STAMP}")
    shutil.copy2(INDEX, backup)
    print(f"[BACKUP] {backup.name}")

c = INDEX.read_text(encoding="utf-8")

# ============================================================
# 1. CSS MOBILE — Adiciona antes de </style> ou de @media existente
# ============================================================
css_mobile = '''
  /* ============ MOBILE RESPONSIVO ============ */

  /* Botão hamburger (só aparece em mobile) */
  .menu-hamburger {
    display: none;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
    width: 40px; height: 40px;
    font-size: 20px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .menu-hamburger:hover { border-color: var(--accent); }

  /* Drawer lateral mobile */
  .drawer-mobile {
    position: fixed;
    top: 0; left: 0; bottom: 0;
    width: 280px; max-width: 85vw;
    background: var(--bg-card);
    border-right: 1px solid var(--border);
    z-index: 2000;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    overflow-y: auto;
    padding: 20px 0;
  }
  .drawer-mobile.aberto { transform: translateX(0); }

  .drawer-mobile-header {
    padding: 0 20px 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 12px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .drawer-mobile-titulo {
    font-size: 16px; font-weight: 700;
    display: flex; align-items: center; gap: 8px;
  }
  .drawer-mobile-fechar {
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 24px;
    cursor: pointer;
    padding: 0 8px;
  }

  .drawer-mobile-item {
    display: flex; align-items: center; gap: 12px;
    padding: 14px 20px;
    font-size: 15px; font-weight: 600;
    color: var(--text);
    cursor: pointer;
    border: none; background: transparent;
    width: 100%;
    text-align: left;
    font-family: inherit;
  }
  .drawer-mobile-item:hover { background: var(--bg); }
  .drawer-mobile-item.ativo {
    background: rgba(99,102,241,0.15);
    color: var(--accent);
    border-left: 3px solid var(--accent);
  }

  /* Overlay escuro quando drawer aberto */
  .drawer-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 1999;
    display: none;
    opacity: 0;
    transition: opacity 0.25s ease;
  }
  .drawer-overlay.aberto { display: block; opacity: 1; }

  /* ============ MEDIA QUERIES ============ */
  @media (max-width: 768px) {
    /* Header */
    .header { padding: 12px 16px !important; }
    .header-logo { font-size: 16px !important; }
    .header-logo img, .header-logo .logo-icon { width: 32px !important; height: 32px !important; }
    .header-user-nome { display: none; }
    .header-user-info { font-size: 13px; }
    .btn-senha, .btn-sair { font-size: 12px !important; padding: 6px 10px !important; }

    /* Esconde abas horizontais */
    .tabs { display: none !important; }

    /* Mostra hamburger */
    .menu-hamburger { display: flex !important; }

    /* Container principal */
    main, .main-content, .conteudo { padding: 16px !important; }

    /* Título da página */
    .page-title { font-size: 22px !important; }
    .page-subtitle { font-size: 13px !important; }

    /* Hero do dashboard */
    .hero, .hero-dashboard {
      padding: 20px !important;
      border-radius: 16px !important;
    }
    .hero h1, .hero-titulo { font-size: 22px !important; }
    .hero p, .hero-subtitulo { font-size: 13px !important; }

    /* Grids → 1 coluna */
    .grid, .cards-grid, .grid-trilhas, .grid-turmas,
    .grid-cursos, .grid-pessoas, .grid-eventos,
    .grid-trilhas-estudo, .grid-badges {
      grid-template-columns: 1fr !important;
      gap: 12px !important;
    }

    /* KPIs → 2 colunas */
    .kpis, .dashboard-kpis, .kpi-grid {
      grid-template-columns: repeat(2, 1fr) !important;
      gap: 12px !important;
    }

    /* Cards */
    .card {
      padding: 16px !important;
      border-radius: 12px !important;
    }
    .card-titulo, .card-label { font-size: 12px !important; }
    .card-valor { font-size: 24px !important; }

    /* Toolbar (filtros) → empilhado */
    .toolbar {
      flex-direction: column !important;
      align-items: stretch !important;
      gap: 10px !important;
    }
    .toolbar-search, .toolbar-select {
      width: 100% !important;
      max-width: none !important;
    }
    .toolbar button { width: 100%; }
    .toolbar-count { text-align: center !important; }

    /* Sub-abas do Estudo → scroll horizontal */
    .estudo-sub-abas {
      overflow-x: auto !important;
      flex-wrap: nowrap !important;
      -webkit-overflow-scrolling: touch;
      padding-bottom: 4px;
      scrollbar-width: none;
    }
    .estudo-sub-abas::-webkit-scrollbar { display: none; }
    .estudo-sub-aba {
      flex-shrink: 0 !important;
      white-space: nowrap;
      font-size: 13px !important;
      padding: 10px 14px !important;
    }

    /* Modais → fullscreen */
    .modal {
      max-width: 100% !important;
      width: 100% !important;
      margin: 0 !important;
      border-radius: 0 !important;
      max-height: 100vh !important;
      height: 100vh !important;
      overflow-y: auto !important;
    }
    .modal-backdrop { padding: 0 !important; }
    .modal-header { padding: 16px !important; }
    .modal-title { font-size: 18px !important; }
    .modal-actions { flex-direction: column-reverse !important; gap: 8px !important; }
    .modal-actions .btn { width: 100% !important; }
    .modal-actions-3 { grid-template-columns: 1fr !important; }

    /* Forms */
    .form-input, .form-select, .form-textarea {
      font-size: 16px !important; /* evita zoom no iOS */
      padding: 12px !important;
    }
    .form-group { margin-bottom: 14px !important; }
    .form-row {
      flex-direction: column !important;
      gap: 0 !important;
    }

    /* Tabelas → cards empilhados */
    table { font-size: 13px !important; }
    th, td { padding: 8px 6px !important; }

    /* Botões maiores (toque) */
    .btn {
      min-height: 44px !important;
      font-size: 14px !important;
      padding: 12px 16px !important;
    }

    /* Anexos */
    .anexo-item, .aluno-item, .chamada-item {
      flex-wrap: wrap;
      gap: 8px;
    }

    /* Certificado card */
    .cert-card { padding: 16px !important; }

    /* Badge */
    .badge-card { padding: 14px !important; }
    .badge-icone { width: 48px !important; height: 48px !important; font-size: 22px !important; }

    /* Ranking */
    .ranking-item { padding: 12px !important; gap: 10px !important; }
    .ranking-nome { font-size: 14px !important; }

    /* Fórum */
    .comentario-item { padding: 12px !important; }
    .comentario-item.resposta { margin-left: 16px !important; }

    /* Quiz */
    .quiz-opcao { padding: 14px !important; font-size: 14px !important; }
    .resultado-nota { font-size: 48px !important; }
  }

  @media (max-width: 480px) {
    /* Header ainda mais compacto */
    .header { padding: 10px 12px !important; }
    .header-logo { font-size: 14px !important; }
    .header-logo span { display: none; }

    /* Botões secundários do header */
    .btn-senha { display: none !important; }

    /* KPIs em 1 coluna em telas muito pequenas */
    .kpis, .dashboard-kpis, .kpi-grid {
      grid-template-columns: 1fr 1fr !important;
    }
    .card-valor { font-size: 20px !important; }

    /* Títulos */
    .page-title { font-size: 20px !important; }
    .hero h1, .hero-titulo { font-size: 20px !important; }

    /* Padding geral */
    main, .main-content, .conteudo { padding: 12px !important; }
  }
'''

# Insere o CSS depois do último </style> existente ou antes de </head>
if ".menu-hamburger" not in c:
    # Tenta achar onde inserir — no último bloco de CSS
    if "@media (max-width: 640px)" in c:
        c = c.replace(
            "  @media (max-width: 640px) {",
            css_mobile + "\n  @media (max-width: 640px) {",
            1,
        )
    else:
        # Insere antes de </style>
        c = c.replace("</style>", css_mobile + "\n</style>", 1)
    print("[OK] CSS mobile adicionado")

# ============================================================
# 2. HTML — Botão hamburger no header + Drawer
# ============================================================
# Vamos procurar o header atual
# Procura "Church Platform" no header e adiciona o botão ANTES do nome
if 'class="menu-hamburger"' not in c:
    padrao_header = r'(<div class="header-logo[^"]*"[^>]*>)'
    if re.search(padrao_header, c):
        c = re.sub(
            padrao_header,
            '<button class="menu-hamburger" onclick="abrirMenuMobile()" aria-label="Menu">☰</button>\\1',
            c,
            count=1,
        )
        print("[OK] Botão hamburger adicionado")
    else:
        # Tenta outro padrão
        padrao_alt = r'(<header[^>]*>)'
        if re.search(padrao_alt, c):
            c = re.sub(
                padrao_alt,
                '\\1\n    <button class="menu-hamburger" onclick="abrirMenuMobile()" aria-label="Menu">☰</button>',
                c,
                count=1,
            )
            print("[OK] Botão hamburger adicionado (via <header>)")
        else:
            print("[AVISO] Nao encontrei o header para inserir o hamburger")

# Adiciona drawer no final do body
if 'class="drawer-mobile"' not in c:
    drawer_html = '''
<!-- Drawer mobile (menu lateral) -->
<div class="drawer-overlay" id="drawer-overlay" onclick="fecharMenuMobile()"></div>
<aside class="drawer-mobile" id="drawer-mobile">
  <div class="drawer-mobile-header">
    <div class="drawer-mobile-titulo">🏠 Church Platform</div>
    <button class="drawer-mobile-fechar" onclick="fecharMenuMobile()">×</button>
  </div>
  <button class="drawer-mobile-item" data-tab="inicio" onclick="irParaAba('inicio')">🏠 Início</button>
  <button class="drawer-mobile-item" data-tab="igrejas" onclick="irParaAba('igrejas')">🏛️ Igrejas</button>
  <button class="drawer-mobile-item" data-tab="pessoas" onclick="irParaAba('pessoas')">👥 Pessoas</button>
  <button class="drawer-mobile-item" data-tab="cuidado" onclick="irParaAba('cuidado')">🕊️ Cuidado</button>
  <button class="drawer-mobile-item" data-tab="oracao" onclick="irParaAba('oracao')">🙏 Oração</button>
  <button class="drawer-mobile-item" data-tab="eventos" onclick="irParaAba('eventos')">📅 Eventos</button>
  <button class="drawer-mobile-item" data-tab="jornada" onclick="irParaAba('jornada')">🎯 Jornada</button>
  <button class="drawer-mobile-item" data-tab="estudo" onclick="irParaAba('estudo')">📚 Estudo</button>
  <button class="drawer-mobile-item" data-tab="usuarios" onclick="irParaAba('usuarios')" id="drawer-item-usuarios" style="display:none;">👤 Usuários</button>
</aside>
'''
    c = c.replace("</body>", drawer_html + "\n</body>", 1)
    print("[OK] Drawer mobile adicionado")

# ============================================================
# 3. JS — funções do menu mobile
# ============================================================
js_mobile = '''
// ============ MENU MOBILE ============
function abrirMenuMobile() {
  document.getElementById("drawer-mobile").classList.add("aberto");
  document.getElementById("drawer-overlay").classList.add("aberto");
}

function fecharMenuMobile() {
  document.getElementById("drawer-mobile").classList.remove("aberto");
  document.getElementById("drawer-overlay").classList.remove("aberto");
}

function irParaAba(nome) {
  fecharMenuMobile();
  trocarAba(nome);
}

// Sincroniza o item ativo do drawer quando muda de aba
function sincronizarDrawer(nome) {
  document.querySelectorAll(".drawer-mobile-item").forEach(b => {
    b.classList.toggle("ativo", b.dataset.tab === nome);
  });
}

// Sobrescreve trocarAba para sincronizar o drawer
(function() {
  const trocarOriginal = window.trocarAba;
  if (typeof trocarOriginal === "function") {
    window.trocarAba = function(nome) {
      trocarOriginal.apply(this, arguments);
      sincronizarDrawer(nome);
    };
  }
})();

// Sincroniza visibilidade do item Usuários
(function() {
  setInterval(() => {
    const tabUsuarios = document.getElementById("tab-usuarios");
    const drawerItem = document.getElementById("drawer-item-usuarios");
    if (tabUsuarios && drawerItem) {
      drawerItem.style.display = tabUsuarios.style.display === "none" ? "none" : "block";
    }
  }, 500);
})();
'''

if "function abrirMenuMobile" not in c:
    marcador = "// ============ NOTIFICACOES ============"
    if marcador in c:
        c = c.replace(marcador, js_mobile + "\n" + marcador, 1)
        print("[OK] JS do menu mobile adicionado")
    else:
        # Adiciona antes do </script> final
        c = c.replace("</script>", js_mobile + "\n</script>", 1)
        print("[OK] JS do menu mobile adicionado (final do script)")

INDEX.write_text(c, encoding="utf-8")
print(f"[OK] {INDEX.relative_to(PROJETO)} ({len(c)} bytes)")
print()
print("=" * 60)
print("PRONTO! Abra o index.html e teste em tela pequena.")
print("No celular: http://<IP-DO-PC>:8000/")
print("=" * 60)