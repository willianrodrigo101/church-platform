"""Remove emojis e caracteres non-ASCII do JavaScript (dentro de <script>)."""
import re
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
INDEX = BACKEND.parent / "frontend" / "web" / "index.html"

print(f"Alvo: {INDEX}")

# Le como bytes (raw), pra nao se preocupar com encoding ainda
raw = INDEX.read_bytes()

# Tenta decodificar como UTF-8
try:
    c = raw.decode("utf-8")
    print("[OK] Arquivo decodificado como UTF-8")
except UnicodeDecodeError:
    print("[AVISO] Nao e UTF-8 puro. Decodificando com errors='replace'")
    c = raw.decode("utf-8", errors="replace")

# ============================================================
# Estrategia: apagar QUALQUER caractere non-ASCII dentro de <script>
# HTML <body> aceita emoji, <script> nao precisa
# ============================================================

def limpar_script(match):
    bloco = match.group(0)
    limpo = ''.join(ch if ord(ch) < 128 else '' for ch in bloco)
    return limpo

antes = len(c)
c = re.sub(r'<script[^>]*>.*?</script>', limpar_script, c, flags=re.DOTALL)
depois = len(c)
print(f"[OK] Removidos {antes - depois} caracteres non-ASCII de <script>")

# Conta quanto sobrou fora do script (HTML) — nao mexe
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, flags=re.DOTALL)
non_ascii_em_scripts = sum(1 for s in scripts for ch in s if ord(ch) > 127)
if non_ascii_em_scripts == 0:
    print("[OK] Todos os <script> estao em ASCII puro agora")
else:
    print(f"[AVISO] Ainda tem {non_ascii_em_scripts} caracteres non-ASCII em <script>")

# Salva
backup = INDEX.with_suffix(".html.bak.encoding_fix")
backup.write_bytes(raw)
print(f"[BACKUP] {backup.name}")

INDEX.write_bytes(c.encode("utf-8"))
print(f"[OK] {INDEX.name} salvo em UTF-8")
print()
print("=" * 60)
print("PRONTO! Recarregue o navegador com Ctrl+Shift+R.")
print("=" * 60)