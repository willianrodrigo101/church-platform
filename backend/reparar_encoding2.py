"""Reparo agressivo: tenta todos os codecs e escolhe o que mais reduz mojibake."""
import shutil
from datetime import datetime
from pathlib import Path

INDEX = Path(r"C:\Users\PC\Documents\CHURCH_PLATFORM\frontend\web\index.html")

if not INDEX.exists():
    print(f"[ERRO] {INDEX} nao existe"); exit(1)

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP = INDEX.with_suffix(f".html.antes-reparo2.{STAMP}")
shutil.copy2(INDEX, BACKUP)
print(f"[BACKUP] {BACKUP.name}")

raw = INDEX.read_bytes()
print(f"[INFO] Tamanho: {len(raw)} bytes")

# Padroes de mojibake que NAO devem existir num texto limpo em pt-BR
MOJI = ["Ã§","Ã£","Ã¡","Ã©","Ã­","Ã³","Ãº","Ã¢","Ãª","Ã´","Ãµ","Ã ","Ã‰","Ã","Â¡","Âº","Âª","Â§","Â£","ðŸ","â€","â›","âœ","âš","â†","â•","Â·"]

def contar_moji(texto):
    return sum(texto.count(m) for m in MOJI)

def tentar(b, codec):
    try:
        return b.decode(codec)
    except Exception:
        return None

candidatos = []
# Estrategia 1: uma passada
for codec in ["utf-8","latin-1","cp1252","cp1250","iso-8859-15","cp850"]:
    t = tentar(raw, codec)
    if t:
        candidatos.append((f"raw.decode({codec})", t))
        # tenta uma segunda passada
        for codec2 in ["latin-1","cp1252"]:
            try:
                t2 = t.encode(codec2).decode("utf-8")
                candidatos.append((f"{codec} -> {codec2} -> utf-8", t2))
            except Exception:
                pass

# Estrategia 2: interpretar como bytes utf-8 com mojibake
try:
    as_text = raw.decode("utf-8")
    for codec in ["latin-1","cp1252"]:
        try:
            t = as_text.encode(codec).decode("utf-8")
            candidatos.append((f"utf-8 -> {codec} -> utf-8 (1x)", t))
            # 3 passadas (as vezes colou multiplo)
            t3 = t
            for _ in range(2):
                try:
                    t3 = t3.encode(codec).decode("utf-8")
                    candidatos.append((f"utf-8 -> {codec} -> utf-8 (mais)", t3))
                except Exception:
                    break
        except Exception:
            pass
except Exception:
    pass

# Escolhe o candidato com MENOS mojibake
melhor_nome, melhor_texto, melhor_score = None, None, 10**9
for nome, texto in candidatos:
    score = contar_moji(texto)
    print(f"  {nome:50s} -> mojibake score = {score}")
    if score < melhor_score and len(texto) > 1000:
        melhor_score = score
        melhor_nome = nome
        melhor_texto = texto

print()
if melhor_texto is None:
    print("[ERRO] Nenhum candidato valido")
    exit(1)

print(f"[MELHOR] {melhor_nome}")
print(f"[SCORE]  {melhor_score} ocorrencias de mojibake restantes")
print(f"[TAM]    {len(melhor_texto)} chars")

# Salva em UTF-8
INDEX.write_text(melhor_texto, encoding="utf-8")
print()
print(f"[OK] Arquivo salvo: {INDEX}")
print(f"[OK] Backup: {BACKUP.name}")
print()
print("=" * 60)
print("Abra http://localhost:5500/index.html e Ctrl+Shift+R")
print("=" * 60)