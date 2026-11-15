"""Conserta encoding do index.html: Latin-1 -> UTF-8 corretamente."""
from pathlib import Path
import re

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
INDEX = PROJETO / "frontend" / "web" / "index.html"

print(f"Alvo: {INDEX}")
print()

# Le como bytes (raw)
raw = INDEX.read_bytes()

# Tenta decodificar como UTF-8 estrito primeiro
try:
    c = raw.decode("utf-8")
    print("[OK] Ja esta em UTF-8 valido — verificando se tem caracteres suspeitos...")
    # Verifica se tem padrao Latin-1 disfarcado (ex: ðŸ aparece quando UTF-8 foi mal decodificado)
    suspeitos = ["ðŸ", "Ã§", "Ã£", "Ã©", "Ã", "âœ", "â˜", "â›", "â€"]
    achou_suspeito = any(s in c for s in suspeitos)
    if achou_suspeito:
        print("[!] Mas contem caracteres corrompidos (Latin-1 disfarcado)")
        print("    Vou fazer a correcao dupla: encode latin-1 + decode utf-8")
        try:
            c = c.encode("latin-1").decode("utf-8")
            print("[OK] Corrigido!")
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            print(f"[ERRO] Nao consegui corrigir: {e}")
    else:
        print("[OK] Arquivo esta correto. Nada a fazer.")
except UnicodeDecodeError:
    print("[!] Nao e UTF-8. Tentando decodificar como Latin-1...")
    c = raw.decode("latin-1")
    print("[OK] Lido como Latin-1. Agora convertendo para UTF-8...")

# Salva em UTF-8
backup = INDEX.with_suffix(f".html.bak.encoding_{__import__('datetime').datetime.now().strftime('%Y%m%d-%H%M%S')}")
backup.write_bytes(raw)
print(f"[BACKUP] {backup.name}")

INDEX.write_text(c, encoding="utf-8")
print(f"[OK] Salvo em UTF-8")

# Verifica o resultado
teste = INDEX.read_text(encoding="utf-8")
emojis_testados = ["🎯", "🏠", "🔔", "👥", "⛪"]
emojis_ok = [e for e in emojis_testados if e in teste]
emojis_falta = [e for e in emojis_testados if e not in teste]
print(f"[INFO] Emojis encontrados: {len(emojis_ok)}/{len(emojis_testados)}: {emojis_ok}")
if emojis_falta:
    print(f"[AVISO] Emojis faltando: {emojis_falta}")

print()
print("=" * 60)
print("PRONTO! Agora teste abrindo o index.html no navegador.")
print("Os emojis devem aparecer corretos (🎯, 🏠, 🔔, etc)")
print("=" * 60)