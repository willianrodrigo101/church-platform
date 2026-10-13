from pathlib import Path
from datetime import datetime

INDEX = Path(r"C:\Users\PC\Documents\CHURCH_PLATFORM\frontend\web\index.html")

# Backup de segurança
stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
INDEX.rename(INDEX.with_suffix(f".html.bkp.{stamp}"))
print(f"backup: index.html.bkp.{stamp}")

def char_para_byte(ch):
    """Converte 1 char de volta pro byte UTF-8 original."""
    cp = ord(ch)
    # ASCII puro: byte direto
    if cp < 128:
        return cp
    # Latin-1: byte direto
    if cp < 256:
        return cp
    # CP1252: alguns chars entre 0x80-0x9F
    cp1252 = {
        0x20AC: 0x80, 0x201A: 0x82, 0x0192: 0x83, 0x201E: 0x84,
        0x2026: 0x85, 0x2020: 0x86, 0x2021: 0x87, 0x02C6: 0x88,
        0x2030: 0x89, 0x0160: 0x8A, 0x2039: 0x8B, 0x0152: 0x8C,
        0x017D: 0x8E, 0x2018: 0x91, 0x2019: 0x92, 0x201C: 0x93,
        0x201D: 0x94, 0x2022: 0x95, 0x2013: 0x96, 0x2014: 0x97,
        0x02DC: 0x98, 0x2122: 0x99, 0x0161: 0x9A, 0x203A: 0x9B,
        0x0153: 0x9C, 0x017E: 0x9E, 0x0178: 0x9F,
    }
    return cp1252.get(cp, None)

def unmojibake(texto):
    bytes_out = bytearray()
    for ch in texto:
        b = char_para_byte(ch)
        if b is not None:
            bytes_out.append(b)
        else:
            # Já é emoji correto ou char fora do escopo — codifica direto
            bytes_out.extend(ch.encode("utf-8"))
    try:
        return bytes_out.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"  aviso em byte {e.start}: usando replace")
        return bytes_out.decode("utf-8", errors="replace")

# Lê o arquivo como utf-8
conteudo = INDEX.read_text(encoding="utf-8")
print(f"antes: {len(conteudo)} chars")

# Aplica 1 vez
novo = unmojibake(conteudo)

# Se AINDA tem mojibake, aplica de novo (o arquivo tem camadas)
for i in range(3):
    if "Ã§" in novo or "Ã£" in novo or "ðŸ" in novo:
        print(f"  camada {i+2}...")
        novo = unmojibake(novo)
    else:
        break

print(f"depois: {len(novo)} chars")
INDEX.write_text(novo, encoding="utf-8")
print()
print("=== PRONTO. Abre http://localhost:5500/index.html e Ctrl+Shift+R ===")