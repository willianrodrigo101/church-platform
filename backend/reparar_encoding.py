"""Repara mojibake no index.html (UTF-8 lido como Latin-1, uma ou mais vezes)."""
import shutil
from datetime import datetime
from pathlib import Path

FRONTEND = Path(r"C:\Users\PC\Documents\CHURCH_PLATFORM\frontend\web")
INDEX = FRONTEND / "index.html"

if not INDEX.exists():
    print(f"[ERRO] {INDEX} nao existe")
    exit(1)

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP = INDEX.with_suffix(f".html.antes-reparo.{STAMP}")
shutil.copy2(INDEX, BACKUP)
print(f"[BACKUP] {BACKUP.name}")

# Le bytes originais
raw = INDEX.read_bytes()
print(f"[INFO] Tamanho original: {len(raw)} bytes")

# Reparar mojibake: quantas vezes for necessario
def corrigir_mojibake(b: bytes) -> tuple[bytes, int]:
    """Tenta reverter mojibake. Retorna (bytes_novos, num_passos)."""
    passos = 0
    for _ in range(5):
        try:
            # 1) bytes -> texto (utf-8)
            texto = b.decode("utf-8")
        except UnicodeDecodeError:
            break  # nao e utf-8 valido, para

        # 2) Verifica se ainda ha mojibake tipico
        tem_mojibake = (
            "\u00c3" in texto or  # Ã
            "\u00c2" in texto or  # Â
            "\u00e2\u20ac" in texto or  # â€
            "\u00f0\u0178" in texto or  # ðŸ
            "\u00e2\u2039" in texto      # â›
        )
        if not tem_mojibake:
            break

        try:
            # 3) texto -> bytes interpretando como latin-1
            b = texto.encode("latin-1")
            passos += 1
            print(f"[PASSO {passos}] mojibake detectado, revertendo...")
        except UnicodeEncodeError:
            # Tem caractere que nao cabe em latin-1 = ja foi parcialmente consertado
            break

    # 4) Reencoda em utf-8 final
    try:
        final_texto = b.decode("utf-8")
    except UnicodeDecodeError:
        # Se falhou, tenta preservar como latin-1 -> utf-8
        final_texto = b.decode("latin-1", errors="replace")

    return final_texto.encode("utf-8"), passos


novo, passos = corrigir_mojibake(raw)
print(f"[INFO] Passos de reparo aplicados: {passos}")
print(f"[INFO] Tamanho novo: {len(novo)} bytes")

# Sanity check — procura por padroes que NAO deveriam existir mais
texto_final = novo.decode("utf-8")
suspeitos = ["Ã§", "Ã£", "Ã¡", "Ã©", "Ã­", "Ã³", "Ãº", "Ã", "ðŸ", "â›", "â€"]
encontrados = {s: texto_final.count(s) for s in suspeitos if s in texto_final}

if encontrados:
    print("\n[AVISO] Ainda encontrados padroes suspeitos:")
    for k, v in encontrados.items():
        print(f"    {k!r}: {v} ocorrencias")
    print("\n[ACAO] O reparo pode ter sido parcial. Confirme visualmente.")
else:
    print("\n[OK] Nenhum padrao suspeito restante!")

# Salva
INDEX.write_bytes(novo)
print(f"\n[OK] Arquivo reparado: {INDEX}")
print(f"[OK] Backup em: {BACKUP.name}")
print()
print("=" * 60)
print("PRONTO! Abra http://localhost:5500/index.html e Ctrl+Shift+R.")
print("=" * 60)