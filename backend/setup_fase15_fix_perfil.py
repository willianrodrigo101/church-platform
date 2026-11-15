"""
setup_fase15_fix_perfil.py
--------------------------
Corrige:
1. service.py: perfil_completo inclui cargo_eclesiastico, data_filiacao, foto_url
2. index.html: renderizarPerfil mostra badge de cargo
3. index.html: renderizarCorpoPerfil mostra cargo + data_filiacao
4. index.html: avatar do perfil mostra foto real se tiver

Blindado: backup, UTF-8, restaura se der erro.
"""
from pathlib import Path
from datetime import datetime
import shutil
import sys
import io
import re

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
SERVICE = BACKEND / "app" / "modules" / "pessoas" / "service.py"
INDEX = PROJETO / "frontend" / "web" / "index.html"
INDEX_BACKEND = PROJETO / "backend" / "app" / "static" / "index.html"

print("=" * 72)
print("FASE 1.5 - FIX PERFIL (CARGO + DADOS)")
print("=" * 72)

if not SERVICE.exists() or not INDEX.exists():
    print("[ERRO] Arquivo nao encontrado")
    sys.exit(1)

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
B_SVC = SERVICE.with_suffix(f".py.bak.perfil_{STAMP}")
B_IDX = INDEX.with_suffix(f".html.bak.perfil_{STAMP}")
shutil.copy2(SERVICE, B_SVC)
shutil.copy2(INDEX, B_IDX)
print(f"[OK] Backups criados")

def restaurar():
    print("[INFO] Restaurando...")
    shutil.copy2(B_SVC, SERVICE)
    shutil.copy2(B_IDX, INDEX)
    sys.exit(1)

def ler(caminho):
    with open(caminho, "rb") as f:
        raw = f.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    return raw.decode("utf-8")

def salvar(caminho, txt):
    with io.open(caminho, "w", encoding="utf-8", newline="") as f:
        f.write(txt)

# ============================================================
# 1. SERVICE.PY — Adicionar campos no perfil_completo
# ============================================================
svc = ler(SERVICE)

if "cargo_eclesiastico" in svc and "perfil_completo" in svc:
    # verificar se ja foi adicionado
    idx_perfil = svc.find("async def perfil_completo")
    bloco = svc[idx_perfil:idx_perfil + 3000]
    if '"cargo_eclesiastico": pessoa.cargo_eclesiastico' in bloco:
        print("[AVISO] service.py: ja tem cargo_eclesiastico no perfil_completo")
    else:
        # Adicionar os 3 campos após "membro": pessoa.membro
        ancora = '"membro": pessoa.membro,\n            "observacoes": pessoa.observacoes,'
        novo = '"membro": pessoa.membro,\n            "observacoes": pessoa.observacoes,\n            "cargo_eclesiastico": pessoa.cargo_eclesiastico,\n            "data_filiacao": pessoa.data_filiacao,\n            "foto_url": pessoa.foto_url,'
        if ancora in bloco:
            # Substituir no bloco todo
            svc = svc[:idx_perfil] + bloco.replace(ancora, novo, 1) + svc[idx_perfil + 3000:]
            print("[OK] service.py: campos adicionados no perfil_completo")
        else:
            print("[AVISO] service.py: ancora nao encontrada no perfil_completo")
            print("[INFO] Tentando ancora alternativa...")
            # Alternativa: adicionar depois de "observacoes": pessoa.observacoes,
            padrao = re.compile(
                r'("observacoes":\s*pessoa\.observacoes,)(\s*"ativo":)',
                re.DOTALL
            )
            m = padrao.search(svc)
            if m:
                svc = svc[:m.start(1)] + '"observacoes": pessoa.observacoes,\n            "cargo_eclesiastico": pessoa.cargo_eclesiastico,\n            "data_filiacao": pessoa.data_filiacao,\n            "foto_url": pessoa.foto_url,' + svc[m.end(1):]
                print("[OK] service.py: campos adicionados (regex)")
            else:
                print("[ERRO] service.py: nao consegui adicionar")
                restaurar()
else:
    print("[AVISO] service.py: perfil_completo nao encontrado")

salvar(SERVICE, svc)
print("[OK] service.py salvo")


# ============================================================
# 2. INDEX.HTML — Correções no perfil
# ============================================================
html = ler(INDEX)

# --- 2.1 Adicionar badge de cargo nas tags (renderizarPerfil) ---
ancora_tags = '''  tags.push(`<span class="card-tag ${p.membro ? 'membro' : 'visitante'}">${p.membro ? 'Membro' : 'Visitante'}</span>`);
  if (p.batizado) tags.push(`<span class="card-tag batizado">Batizado</span>`);'''

nova_tags = '''  // FASE 1.5: Cargo eclesiastico (badge colorido)
  if (p.cargo_eclesiastico) {
    const cargoClass = p.cargo_eclesiastico.toLowerCase().replace(/[\\s\\/]+/g, '-');
    tags.push(`<span class="cargo-badge ${cargoClass}">${p.cargo_eclesiastico}</span>`);
  }
  tags.push(`<span class="card-tag ${p.membro ? 'membro' : 'visitante'}">${p.membro ? 'Membro' : 'Visitante'}</span>`);
  if (p.batizado) tags.push(`<span class="card-tag batizado">Batizado</span>`);'''

if ancora_tags in html and 'cargo-badge' not in html:
    html = html.replace(ancora_tags, nova_tags, 1)
    print("[OK] renderizarPerfil: badge de cargo adicionado")
else:
    print("[AVISO] renderizarPerfil: ancora das tags nao encontrada (ou ja existe)")

# --- 2.2 Adicionar Cargo e Data de Filiação no renderizarCorpoPerfil ---
ancora_itens = '''      ["CPF", p.cpf],
      ["Email", p.email],
      ["Telefone", p.telefone],
      ["Nascimento", p.data_nascimento ? new Date(p.data_nascimento + "T00:00:00").toLocaleDateString("pt-BR") : null],'''

novos_itens = '''      ["CPF", p.cpf],
      ["Email", p.email],
      ["Telefone", p.telefone],
      ["Nascimento", p.data_nascimento ? new Date(p.data_nascimento + "T00:00:00").toLocaleDateString("pt-BR") : null],
      ["Cargo Eclesiástico", p.cargo_eclesiastico],
      ["Data de Filiação", p.data_filiacao ? new Date(p.data_filiacao + "T00:00:00").toLocaleDateString("pt-BR") : null],'''

if ancora_itens in html and 'Cargo Eclesiástico", p.cargo_eclesiastico' not in html:
    html = html.replace(ancora_itens, novos_itens, 1)
    print("[OK] renderizarCorpoPerfil: cargo + filiacao adicionados")
else:
    print("[AVISO] renderizarCorpoPerfil: ancora nao encontrada (ou ja existe)")

# --- 2.3 Mostrar foto real no avatar do perfil ---
ancora_avatar = '''      <div class="perfil-avatar">${iniciais}</div>'''

novo_avatar = '''      ${getFotoAvatarHtml(p, "") || `<div class="perfil-avatar">${iniciais}</div>`}'''

if ancora_avatar in html and 'getFotoAvatarHtml(p, "") || `<div class="perfil-avatar"' not in html:
    html = html.replace(ancora_avatar, novo_avatar, 1)
    print("[OK] renderizarPerfil: avatar com foto")
else:
    print("[AVISO] renderizarPerfil: avatar nao encontrado (ou ja existe)")

# --- 2.4 CSS do cargo-badge (se ainda nao existe) ---
if ".cargo-badge" not in html:
    css = '''
  /* ============ FASE 1.5: BADGE DE CARGO NO PERFIL ============ */
  .perfil-tags .cargo-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 10px; border-radius: 12px;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.4px;
    background: rgba(99, 102, 241, 0.15);
    color: #818cf8;
    border: 1px solid rgba(99, 102, 241, 0.3);
  }
  .perfil-tags .cargo-badge.pastor,
  .perfil-tags .cargo-badge.pastora {
    background: rgba(236, 72, 153, 0.15); color: #ec4899;
    border-color: rgba(236, 72, 153, 0.3);
  }
  .perfil-tags .cargo-badge.lider-de-louvor,
  .perfil-tags .cargo-badge.lider-de-jovens,
  .perfil-tags .cargo-badge.lider-de-criancas,
  .perfil-tags .cargo-badge.lider-de-celula {
    background: rgba(16, 185, 129, 0.15); color: #10b981;
    border-color: rgba(16, 185, 129, 0.3);
  }
  .perfil-tags .cargo-badge.diacono,
  .perfil-tags .cargo-badge.presbitero,
  .perfil-tags .cargo-badge.evangelista {
    background: rgba(245, 158, 11, 0.15); color: #f59e0b;
    border-color: rgba(245, 158, 11, 0.3);
  }
  .perfil-tags .cargo-badge.secretario,
  .perfil-tags .cargo-badge.tesoureiro {
    background: rgba(59, 130, 246, 0.15); color: #3b82f6;
    border-color: rgba(59, 130, 246, 0.3);
  }
'''
    pos_style = html.rfind("</style>")
    if pos_style > -1:
        html = html[:pos_style] + css + html[pos_style:]
        print("[OK] CSS do badge de cargo adicionado")

# Verificar emojis
emojis = ["🏠", "🔔", "⛪", "🎂", "☰", "🙏", "🕊️"]
faltando = [e for e in emojis if e not in html]
if faltando:
    print(f"[ERRO] Emojis sumiram: {faltando}")
    restaurar()
print("[OK] Emojis intactos")

salvar(INDEX, html)
shutil.copy2(INDEX, INDEX_BACKEND)
print("[OK] index.html salvo e sincronizado")

# VERIFICACAO FINAL
print()
print("=" * 72)
print("VERIFICACAO FINAL")
print("=" * 72)

v_svc = ler(SERVICE)
v_html = ler(INDEX)

checks = [
    ("service.py: cargo no perfil_completo", '"cargo_eclesiastico": pessoa.cargo_eclesiastico' in v_svc),
    ("service.py: data_filiacao no perfil_completo", '"data_filiacao": pessoa.data_filiacao' in v_svc),
    ("service.py: foto_url no perfil_completo", '"foto_url": pessoa.foto_url' in v_svc),
    ("HTML: badge de cargo", 'cargo-badge ${cargoClass}' in v_html),
    ("HTML: cargo no info-grid", '["Cargo Eclesiástico", p.cargo_eclesiastico]' in v_html),
    ("HTML: filiacao no info-grid", '["Data de Filiação", p.data_filiacao' in v_html),
    ("HTML: avatar com foto", 'getFotoAvatarHtml(p, "") || `<div class="perfil-avatar"' in v_html),
]

todos_ok = True
for desc, ok in checks:
    if ok:
        print(f"  [OK] {desc}")
    else:
        print(f"  [FALHOU] {desc}")
        todos_ok = False

if not todos_ok:
    print()
    print("[ERRO] Check falhou. Restaurando...")
    restaurar()

print()
print("=" * 72)
print("PRONTO! PERFIL CORRIGIDO")
print("=" * 72)
print()
print("Proximos passos:")
print("  1. docker compose cp frontend\\web\\index.html backend:/app/app/static/index.html")
print("  2. docker compose restart backend")
print("  3. Testar no navegador")
print()

sys.exit(0)