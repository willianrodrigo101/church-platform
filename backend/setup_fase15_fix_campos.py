"""
setup_fase15_fix_campos.py
--------------------------
Corrige:
1. service.py: converte "" para None e strings "true"/"false" para booleanos
2. Sincroniza com o Docker
"""
from pathlib import Path
from datetime import datetime
import shutil
import sys
import io
import re

BACKEND = Path(__file__).parent.resolve()
SERVICE = BACKEND / "app" / "modules" / "usuarios" / "service.py"

if not SERVICE.exists():
    print("[ERRO] service.py nao encontrado")
    sys.exit(1)

STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP = SERVICE.with_suffix(f".py.bak.fix_{STAMP}")
shutil.copy2(SERVICE, BACKUP)
print(f"[OK] Backup: {BACKUP.name}")

with open(SERVICE, "rb") as f:
    raw = f.read()
if raw[:3] == b"\xef\xbb\xbf":
    raw = raw[3:]
svc = raw.decode("utf-8")

if "campos_string_para_bool" in svc:
    print("[AVISO] Correcao ja aplicada")
else:
    # --- 1. Corrigir o bloco de criar Pessoa ---
    ancora = '''            pessoa_dados = {
                "nome": dados.get("nome"),
                "email": dados.get("email"),
                "telefone": dados.get("telefone"),
                "data_nascimento": dados.get("data_nascimento"),
                "cargo_eclesiastico": dados.get("cargo_eclesiastico"),
                "data_filiacao": dados.get("data_filiacao"),
                "batizado": dados.get("batizado", False),
                "membro": dados.get("membro", True),
                "igreja_id": igreja_id,
                "ativo": True,
            }
            # Limpa campos None
            pessoa_dados = {k: v for k, v in pessoa_dados.items() if v is not None}'''
    
    novo = '''            # Helpers locais para normalizar dados do frontend
            def _s(v):
                if v is None or v == "":
                    return None
                return v.strip() if isinstance(v, str) else v
            
            def _b(v, padrao=False):
                if v is None or v == "":
                    return padrao
                if isinstance(v, bool):
                    return v
                if isinstance(v, str):
                    return v.lower() in ("true", "1", "sim", "yes", "on")
                return bool(v)
            
            pessoa_dados = {
                "nome": _s(dados.get("nome")),
                "email": _s(dados.get("email")),
                "telefone": _s(dados.get("telefone")),
                "data_nascimento": _s(dados.get("data_nascimento")),
                "cargo_eclesiastico": _s(dados.get("cargo_eclesiastico")),
                "data_filiacao": _s(dados.get("data_filiacao")),
                "batizado": _b(dados.get("batizado"), False),
                "membro": _b(dados.get("membro"), True),
                "igreja_id": igreja_id,
                "ativo": True,
            }
            # Limpa campos None
            pessoa_dados = {k: v for k, v in pessoa_dados.items() if v is not None}'''
    
    if ancora not in svc:
        print("[ERRO] Bloco criar Pessoa nao encontrado")
        print("[INFO] Tentando versao com regex...")
        padrao = re.compile(
            r'pessoa_dados\s*=\s*\{.*?\}\s*\n\s*#\s*Limpa campos None\s*\n\s*pessoa_dados\s*=\s*\{[^\}]*\}',
            re.DOTALL
        )
        m = padrao.search(svc)
        if not m:
            print("[ERRO] Nao consegui encontrar o bloco mesmo com regex")
            shutil.copy2(BACKUP, SERVICE)
            sys.exit(1)
        svc = svc[:m.start()] + novo + svc[m.end():]
        print("[OK] Bloco criar Pessoa corrigido (regex)")
    else:
        svc = svc.replace(ancora, novo, 1)
        print("[OK] Bloco criar Pessoa corrigido")

try:
    with io.open(SERVICE, "w", encoding="utf-8", newline="") as f:
        f.write(svc)
    print("[OK] service.py salvo")
except Exception as e:
    print(f"[ERRO] Falha ao salvar: {e}")
    shutil.copy2(BACKUP, SERVICE)
    sys.exit(1)

# Verificar
with open(SERVICE, "r", encoding="utf-8") as f:
    v = f.read()
checks = [
    ("helper _s", "def _s(" in v),
    ("helper _b", "def _b(" in v),
    ("cargo_eclesiastico", '"cargo_eclesiastico": _s(' in v),
    ("membro booleano", '"membro": _b(' in v),
    ("batizado booleano", '"batizado": _b(' in v),
]
print()
print("VERIFICACAO:")
for desc, ok in checks:
    print(f"  [{'OK' if ok else 'FALHOU'}] {desc}")

print()
print("=" * 72)
print("PRONTO! service.py corrigido")
print("=" * 72)
print()
print("Proximos passos:")
print("  1. docker compose restart backend")
print("  2. Testar no navegador (localhost:8000)")
print("  3. Depois git commit + push (Railway)")
print()