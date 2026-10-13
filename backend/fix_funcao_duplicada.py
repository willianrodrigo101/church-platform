"""Remove a funcao trocarSubAbaEstudo duplicada (a antiga com 5 abas)."""
import re
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
INDEX = BACKEND.parent / "frontend" / "web" / "index.html"

print(f"Alvo: {INDEX}")

c = INDEX.read_text(encoding="utf-8")

# Conta quantas funções existem
ocorrencias = c.count("function trocarSubAbaEstudo(sub) {")
print(f"Funcoes encontradas: {ocorrencias}")

if ocorrencias <= 1:
    print("[SKIP] Nao ha duplicacao. Saindo.")
    raise SystemExit(0)

# Pega TODAS as definições (com o corpo)
padrao = r'function trocarSubAbaEstudo\(sub\) \{.*?\n\}\n'
matches = list(re.finditer(padrao, c, flags=re.DOTALL))

print(f"Blocos encontrados: {len(matches)}")

if len(matches) < 2:
    print("[AVISO] Regex nao pegou os blocos. Tentando outro jeito...")
    # Tenta pegar pela proxima function
    padrao2 = r'function trocarSubAbaEstudo\(sub\) \{[^}]*\}\s*(?=\n\s*(?:function|async function|//|\Z))'
    matches = list(re.finditer(padrao2, c, flags=re.DOTALL))
    print(f"Blocos (2a tentativa): {len(matches)}")

if len(matches) < 2:
    print("[ERRO] Nao consegui identificar os 2 blocos. Manual precisa ser feito.")
    print("       Vou remover a segunda ocorrencia por posicao de string.")
    # Remocao por string: procura a segunda ocorrencia textual
    first = c.find("function trocarSubAbaEstudo(sub) {")
    second = c.find("function trocarSubAbaEstudo(sub) {", first + 10)

    if second == -1:
        print("[ERRO] Segunda ocorrencia nao encontrada por posicao.")
        raise SystemExit(1)

    # Acha o final do bloco (proxima function ou async function ou // ==)
    resto = c[second:]
    # Procura o proximo "function " ou "async function " ou marcador grande
    fim_match = re.search(r'\n(function |async function |// =+|\Z)', resto)
    if fim_match:
        fim = second + fim_match.start()
    else:
        # Fallback: acha o proximo "async function" ou fim do arquivo
        fim = second + 3000  # limite seguro

    c = c[:second] + c[fim:]
    INDEX.write_text(c, encoding="utf-8")
    print("[OK] Segunda ocorrencia removida por posicao.")
    raise SystemExit(0)

# Remover todas EXCETO a primeira (mantém a boa)
# A primeira é a que tem "certificados" no corpo
primeira_boa = None
for m in matches:
    if "certificados" in m.group(0) and "ferramentas" in m.group(0):
        primeira_boa = m
        break

if not primeira_boa:
    print("[ERRO] Nenhuma das funcoes tem certificados+ferramentas.")
    raise SystemExit(1)

# Remove todas as outras
for m in reversed(matches):
    if m is primeira_boa:
        continue
    inicio, fim = m.span()
    c = c[:inicio] + c[fim:]
    print(f"[OK] Removida funcao duplicada (linha aprox.)")

INDEX.write_text(c, encoding="utf-8")
print()
print(f"Funcoes restantes: {c.count('function trocarSubAbaEstudo(sub) {')}")
print("[OK] Salvou o index.html")
print()
print("=" * 60)
print("Agora faca Ctrl+Shift+R no navegador e teste.")
print("=" * 60)