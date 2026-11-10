"""
setup_fase15_usuarios.py
------------------------
FASE 1.5 - Integracao Usuario + Pessoa

Faz:
1. models.py: adiciona pessoa_id (ForeignKey para pessoas)
2. schemas.py: adiciona pessoa_id no UsuarioResponse
3. service.py: ao criar usuario nao-admin, cria Pessoa automaticamente
4. Verifica se tudo foi aplicado

Blindado: backup, UTF-8 strict, restaura se der erro.
"""
from pathlib import Path
from datetime import datetime
import shutil
import sys
import io
import re

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
MODELS = BACKEND / "app" / "modules" / "usuarios" / "models.py"
SCHEMAS = BACKEND / "app" / "modules" / "usuarios" / "schemas.py"
SERVICE = BACKEND / "app" / "modules" / "usuarios" / "service.py"

print("=" * 72)
print("FASE 1.5 - INTEGRACAO USUARIO + PESSOA")
print("=" * 72)

for arq, nome in [(MODELS, "models.py"), (SCHEMAS, "schemas.py"), (SERVICE, "service.py")]:
    if not arq.exists():
        print(f"[ERRO] {nome} nao encontrado")
        sys.exit(1)

# ============================================================
# BACKUP
# ============================================================
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP_MODELS = MODELS.with_suffix(f".py.bak.fase15_{STAMP}")
BACKUP_SCHEMAS = SCHEMAS.with_suffix(f".py.bak.fase15_{STAMP}")
BACKUP_SERVICE = SERVICE.with_suffix(f".py.bak.fase15_{STAMP}")

shutil.copy2(MODELS, BACKUP_MODELS)
shutil.copy2(SCHEMAS, BACKUP_SCHEMAS)
shutil.copy2(SERVICE, BACKUP_SERVICE)
print(f"[OK] Backup models:  {BACKUP_MODELS.name}")
print(f"[OK] Backup schemas: {BACKUP_SCHEMAS.name}")
print(f"[OK] Backup service: {BACKUP_SERVICE.name}")
print()

def restaurar_tudo():
    print("[INFO] Restaurando TODOS os backups...")
    shutil.copy2(BACKUP_MODELS, MODELS)
    shutil.copy2(BACKUP_SCHEMAS, SCHEMAS)
    shutil.copy2(BACKUP_SERVICE, SERVICE)
    print("[INFO] Restauracao concluida.")

# ============================================================
# 1. MODELS.PY - adicionar pessoa_id
# ============================================================
try:
    with open(MODELS, "rb") as f:
        raw = f.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    models_txt = raw.decode("utf-8")
    print("[OK] models.py lido")
except Exception as e:
    print(f"[ERRO] Falha ao ler models.py: {e}")
    restaurar_tudo()
    sys.exit(1)

if "pessoa_id" in models_txt:
    print("[AVISO] pessoa_id ja existe em models.py - pulando")
else:
    # Inserir antes de "igreja = relationship("Igreja", lazy="joined")"
    ancora = '    igreja = relationship("Igreja", lazy="joined")'
    nova_linha = '''    pessoa_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    igreja = relationship("Igreja", lazy="joined")
    pessoa = relationship("Pessoa", lazy="joined")'''
    
    if ancora not in models_txt:
        print("[ERRO] Nao achei ancora em models.py")
        restaurar_tudo()
        sys.exit(1)
    
    models_txt = models_txt.replace(ancora, nova_linha, 1)
    print("[OK] models.py: pessoa_id + relationship adicionados")

# ============================================================
# 2. SCHEMAS.PY - adicionar pessoa_id no UsuarioResponse
# ============================================================
try:
    with open(SCHEMAS, "rb") as f:
        raw = f.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    schemas_txt = raw.decode("utf-8")
    print("[OK] schemas.py lido")
except Exception as e:
    print(f"[ERRO] Falha ao ler schemas.py: {e}")
    restaurar_tudo()
    sys.exit(1)

if "pessoa_id" in schemas_txt:
    print("[AVISO] pessoa_id ja existe em schemas.py - pulando")
else:
    ancora = '''class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    email: EmailStr
    role: str
    ativo: bool
    igreja_id: UUID | None = None
    created_at: datetime'''
    
    nova = '''class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    email: EmailStr
    role: str
    ativo: bool
    igreja_id: UUID | None = None
    pessoa_id: UUID | None = None
    created_at: datetime'''
    
    if ancora not in schemas_txt:
        print("[ERRO] Nao achei ancora em schemas.py")
        restaurar_tudo()
        sys.exit(1)
    
    schemas_txt = schemas_txt.replace(ancora, nova, 1)
    print("[OK] schemas.py: pessoa_id no UsuarioResponse")

# ============================================================
# 3. SERVICE.PY - criar Pessoa junto com Usuario
# ============================================================
try:
    with open(SERVICE, "rb") as f:
        raw = f.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    service_txt = raw.decode("utf-8")
    print("[OK] service.py lido")
except Exception as e:
    print(f"[ERRO] Falha ao ler service.py: {e}")
    restaurar_tudo()
    sys.exit(1)

if "PessoaRepository" in service_txt:
    print("[AVISO] Integracao ja existe em service.py - pulando")
else:
    # 3.1 - Adicionar imports (Pessoa e PessoaRepository)
    imports_antigos = "from app.modules.igreja.repository import IgrejaRepository\nfrom app.modules.usuarios.models import TokenResetSenha, Usuario"
    imports_novos = "from app.modules.igreja.repository import IgrejaRepository\nfrom app.modules.pessoas.repository import PessoaRepository\nfrom app.modules.usuarios.models import TokenResetSenha, Usuario"
    
    if imports_antigos not in service_txt:
        print("[ERRO] Nao achei imports em service.py")
        restaurar_tudo()
        sys.exit(1)
    
    service_txt = service_txt.replace(imports_antigos, imports_novos, 1)
    print("[OK] service.py: imports adicionados")

    # 3.2 - Adicionar PessoaRepository no __init__
    init_antigo = "        self.repo = UsuarioRepository(db)\n        self.igreja_repo = IgrejaRepository(db)\n        self.db = db"
    init_novo = "        self.repo = UsuarioRepository(db)\n        self.igreja_repo = IgrejaRepository(db)\n        self.pessoa_repo = PessoaRepository(db)\n        self.db = db"
    
    if init_antigo not in service_txt:
        print("[ERRO] Nao achei __init__ em service.py")
        restaurar_tudo()
        sys.exit(1)
    
    service_txt = service_txt.replace(init_antigo, init_novo, 1)
    print("[OK] service.py: pessoa_repo adicionado no __init__")

    # 3.3 - Modificar o metodo criar()
    criar_antigo = '''        dados["senha_hash"] = hash_senha(dados.pop("senha"))
        return await self.repo.criar(dados)'''
    
    criar_novo = '''        # ============================================================
        # INTEGRACAO (FASE 1.5): Cria Pessoa automaticamente se nao for admin
        # ============================================================
        pessoa_id = None
        if role != "admin" and igreja_id:
            # Extrai os dados pastorais que podem vir do frontend
            pessoa_dados = {
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
            # Remove campos None para nao quebrar o schema
            pessoa_dados = {k: v for k, v in pessoa_dados.items() if v is not None}
            
            # Cria a Pessoa
            try:
                pessoa = await self.pessoa_repo.criar(pessoa_dados)
                pessoa_id = pessoa.id
                dados["pessoa_id"] = pessoa_id
            except Exception as e:
                raise BusinessRuleError(f"Erro ao criar perfil pastoral da pessoa: {str(e)}")

        # Salva os dados do usuario (incluindo pessoa_id)
        dados["senha_hash"] = hash_senha(dados.pop("senha"))
        return await self.repo.criar(dados)'''
    
    if criar_antigo not in service_txt:
        print("[ERRO] Nao achei bloco criar() em service.py")
        restaurar_tudo()
        sys.exit(1)
    
    service_txt = service_txt.replace(criar_antigo, criar_novo, 1)
    print("[OK] service.py: logica de criar Pessoa adicionada")

# ============================================================
# SALVAR
# ============================================================
try:
    with io.open(MODELS, "w", encoding="utf-8", newline="") as f:
        f.write(models_txt)
    with io.open(SCHEMAS, "w", encoding="utf-8", newline="") as f:
        f.write(schemas_txt)
    with io.open(SERVICE, "w", encoding="utf-8", newline="") as f:
        f.write(service_txt)
    print("[OK] Arquivos salvos em UTF-8")
except Exception as e:
    print(f"[ERRO] Falha ao salvar: {e}")
    restaurar_tudo()
    sys.exit(1)

# ============================================================
# VERIFICACAO
# ============================================================
print()
print("=" * 72)
print("VERIFICACAO FINAL")
print("=" * 72)

with open(MODELS, "r", encoding="utf-8") as f: v_m = f.read()
with open(SCHEMAS, "r", encoding="utf-8") as f: v_s = f.read()
with open(SERVICE, "r", encoding="utf-8") as f: v_svc = f.read()

checks = [
    ("models.py: pessoa_id", "pessoa_id: Mapped" in v_m),
    ("models.py: relationship Pessoa", 'relationship("Pessoa"' in v_m),
    ("schemas.py: pessoa_id no Response", "pessoa_id: UUID | None = None" in v_s),
    ("service.py: import PessoaRepository", "from app.modules.pessoas.repository import PessoaRepository" in v_svc),
    ("service.py: criar Pessoa automaticamente", "Cria Pessoa automaticamente" in v_svc),
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
    restaurar_tudo()
    sys.exit(1)

print()
print("=" * 72)
print("PRONTO! BACKEND INTEGRADO")
print("=" * 72)
print()
print("Proximos passos:")
print("  1. Criar migration (alembic)")
print("  2. Aplicar no banco")
print()