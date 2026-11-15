from pathlib import Path

WEB = Path(r"C:\Users\PC\Documents\CHURCH_PLATFORM\frontend\web")
SAIDA = WEB / "index.html"

# --- 1. Achar fonte boa ---
fonte = WEB / "index.html.antes-reparo2.20261010-024832"
if not fonte.exists():
    print("ERRO: fonte boa nao encontrada")
    print("\nArquivos em frontend/web:")
    for p in sorted(WEB.glob("index.html*")):
        print(f"  {p.name}  ({p.stat().st_size} bytes)")
    raise SystemExit(1)

print(f"Fonte: {fonte.name}  ({fonte.stat().st_size} bytes)")

# --- 2. Ler como UTF-8 ---
texto = fonte.read_text(encoding="utf-8")
print(f"Lido: {len(texto)} chars")
print(f"Inicio: {texto[:150]!r}")
print()

# --- 3. Reversao mojibake: cada char -> byte original ---
CP1252 = {
    0x20AC:0x80, 0x201A:0x82, 0x0192:0x83, 0x201E:0x84, 0x2026:0x85,
    0x2020:0x86, 0x2021:0x87, 0x02C6:0x88, 0x2030:0x89, 0x0160:0x8A,
    0x2039:0x8B, 0x0152:0x8C, 0x017D:0x8E, 0x2018:0x91, 0x2019:0x92,
    0x201C:0x93, 0x201D:0x94, 0x2022:0x95, 0x2013:0x96, 0x2014:0x97,
    0x02DC:0x98, 0x2122:0x99, 0x0161:0x9A, 0x203A:0x9B, 0x0153:0x9C,
    0x017E:0x9E, 0x0178:0x9F,
}

def char_para_byte(ch):
    cp = ord(ch)
    if cp < 256:
        return cp
    return CP1252.get(cp)

def unmojibake(s):
    out = bytearray()
    perdidos = 0
    for ch in s:
        b = char_para_byte(ch)
        if b is not None:
            out.append(b)
        else:
            perdidos += 1
            out.extend(ch.encode("utf-8"))
    if perdidos:
        print(f"  ({perdidos} chars mantidos como estao)")
    return out.decode("utf-8", errors="replace")

# Aplica ate 3 vezes (as vezes tem camadas)
atual = texto
for i in range(3):
    novo = unmojibake(atual)
    if novo == atual:
        break
    atual = novo
    print(f"  camada {i+1}: {len(atual)} chars")
    if not ("Ã" in atual or "ðŸ" in atual or "â€" in atual):
        break

print(f"\nDepois: {len(atual)} chars")
print(f"Amostra: {atual[:200]!r}")

# --- 4. Salva ---
if SAIDA.exists():
    SAIDA.rename(WEB / f"index.html.cp850-destruido.bak")
SAIDA.write_text(atual, encoding="utf-8")
print(f"\nSALVO: {SAIDA}")

# --- 5. Confere ---
print("\nVerificacao:")
for chave in ["Início", "Oração", "Usuários", "Igrejas", "SÁBADO", "🙏", "🏠", "📚"]:
    if chave in atual:
        print(f"  OK   {chave!r}")
    else:
        print(f"  FALTA {chave!r}")