"""Fix Bloco 4 — adiciona Anotacao + FerramentaEstudo + registra router_publico."""
import shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")


def escrever_se_faltar(caminho, marcador, conteudo_extra, ajuste_topo=None):
    """Adiciona conteudo_extra no fim se o marcador nao existir."""
    if not caminho.exists():
        print(f"  [ERRO] {caminho.name} nao existe")
        return
    c = caminho.read_text(encoding="utf-8")
    if marcador in c:
        print(f"  [SKIP] {caminho.name} ja tem '{marcador}'")
        return
    if ajuste_topo:
        for antigo, novo in ajuste_topo:
            if antigo in c and novo not in c:
                c = c.replace(antigo, novo, 1)
    c = c.rstrip() + conteudo_extra
    backup = caminho.with_suffix(caminho.suffix + f".bak.{STAMP}")
    shutil.copy2(caminho, backup)
    caminho.write_text(c, encoding="utf-8")
    print(f"  [BACKUP] {backup.name}")
    print(f"  [OK] {caminho.name} atualizado")


# ============================================================
# 1. MODELS — Anotacao + FerramentaEstudo
# ============================================================
models_extra = '''


class Anotacao(Base, UUIDMixin, TimestampMixin):
    """Anotacoes pessoais do aluno sobre um modulo."""
    __tablename__ = "anotacoes"

    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    modulo_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("modulos_curso.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    favorito: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pessoa = relationship("Pessoa", lazy="joined")
    modulo = relationship("ModuloCurso", lazy="joined")


class FerramentaEstudo(Base, UUIDMixin, TimestampMixin):
    """Catalogo curado de ferramentas externas de estudo."""
    __tablename__ = "ferramentas_estudo"

    igreja_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=True, index=True,
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, default="outro", index=True)
    icone: Mapped[str] = mapped_column(String(10), nullable=False, default="🔗")
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
'''


# ============================================================
# 2. SCHEMAS — Anotacao + Ferramenta
# ============================================================
schemas_extra = '''


# ============ ANOTACAO ============

class AnotacaoCreate(BaseModel):
    modulo_id: UUID
    titulo: str = Field(..., min_length=1, max_length=200)
    conteudo: str = Field(..., min_length=1)
    favorito: bool = False


class AnotacaoUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=1, max_length=200)
    conteudo: str | None = None
    favorito: bool | None = None


class AnotacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    pessoa_id: UUID
    modulo_id: UUID
    igreja_id: UUID
    titulo: str
    conteudo: str
    favorito: bool
    created_at: datetime
    updated_at: datetime


# ============ FERRAMENTA ============

class FerramentaCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: str | None = None
    url: str = Field(..., min_length=5, max_length=1000)
    categoria: str = Field("outro", pattern="^(interlinear|lexico|mapa|gramatica|comentario|dicionario|referencia|outro)$")
    icone: str = "🔗"
    ordem: int = 1


class FerramentaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID | None = None
    nome: str
    descricao: str | None = None
    url: str
    categoria: str
    icone: str
    ordem: int
    ativo: bool
    created_at: datetime
'''


# ============================================================
# 3. REPOSITORY — Anotacao + Ferramenta
# ============================================================
repo_extra = '''


class AnotacaoRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Anotacao
        a = Anotacao(**dados)
        self.db.add(a)
        await self.db.flush()
        await self.db.refresh(a)
        return a

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Anotacao
        r = await self.db.execute(select(Anotacao).where(Anotacao.id == obj_id))
        return r.scalar_one_or_none()

    async def listar_por_pessoa(self, pessoa_id, modulo_id=None):
        from app.modules.estudo.models import Anotacao
        stmt = select(Anotacao).where(Anotacao.pessoa_id == pessoa_id)
        if modulo_id:
            stmt = stmt.where(Anotacao.modulo_id == modulo_id)
        stmt = stmt.order_by(Anotacao.favorito.desc(), Anotacao.updated_at.desc())
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class FerramentaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import FerramentaEstudo
        f = FerramentaEstudo(**dados)
        self.db.add(f)
        await self.db.flush()
        await self.db.refresh(f)
        return f

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import FerramentaEstudo
        r = await self.db.execute(
            select(FerramentaEstudo).where(FerramentaEstudo.id == obj_id)
        )
        return r.scalar_one_or_none()

    async def listar(self, igreja_id=None, categoria=None, apenas_ativas=True):
        from app.modules.estudo.models import FerramentaEstudo
        from sqlalchemy import or_
        stmt = select(FerramentaEstudo)
        if igreja_id:
            stmt = stmt.where(
                or_(
                    FerramentaEstudo.igreja_id == igreja_id,
                    FerramentaEstudo.igreja_id.is_(None),
                )
            )
        if categoria:
            stmt = stmt.where(FerramentaEstudo.categoria == categoria)
        if apenas_ativas:
            stmt = stmt.where(FerramentaEstudo.ativo.is_(True))
        stmt = stmt.order_by(FerramentaEstudo.ordem.asc(), FerramentaEstudo.nome.asc())
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()
'''


# ============================================================
# MARCADOR — PARTE 2 CONTINUA AQUI
# ============================================================# ============================================================
# 4. SERVICES — Anotacao + Ferramenta
# ============================================================
service_extra = '''


class AnotacaoService:
    def __init__(self, db):
        self.db = db
        self.repo = AnotacaoRepository(db)

    async def criar(self, pessoa_id, dados, autor):
        from app.modules.igreja.repository import IgrejaRepository
        from app.modules.pessoas.repository import PessoaRepository

        pessoa = await PessoaRepository(self.db).buscar_por_id(pessoa_id)
        if not pessoa:
            raise NotFoundError("Pessoa", str(pessoa_id))

        igreja_id = getattr(autor, "igreja_id", None) or pessoa.igreja_id
        if not igreja_id:
            igrejas = await IgrejaRepository(self.db).listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            igreja_id = igrejas[0].id

        dados_full = {
            "pessoa_id": pessoa_id,
            "modulo_id": dados["modulo_id"],
            "igreja_id": igreja_id,
            "titulo": dados["titulo"],
            "conteudo": dados["conteudo"],
            "favorito": dados.get("favorito", False),
        }
        return await self.repo.criar(dados_full)

    async def listar(self, pessoa_id, modulo_id=None):
        return await self.repo.listar_por_pessoa(pessoa_id, modulo_id)

    async def atualizar(self, obj_id, dados, autor):
        a = await self.repo.buscar_por_id(obj_id)
        if not a:
            raise NotFoundError("Anotacao", str(obj_id))
        return await self.repo.atualizar(a, dados)

    async def deletar(self, obj_id, autor):
        a = await self.repo.buscar_por_id(obj_id)
        if not a:
            raise NotFoundError("Anotacao", str(obj_id))
        await self.repo.deletar(a)


class FerramentaService:
    def __init__(self, db):
        self.db = db
        self.repo = FerramentaRepository(db)

    async def criar(self, dados, autor):
        from app.modules.igreja.repository import IgrejaRepository
        igreja_id = getattr(autor, "igreja_id", None)
        if not igreja_id:
            igrejas = await IgrejaRepository(self.db).listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            igreja_id = igrejas[0].id
        dados["igreja_id"] = igreja_id
        return await self.repo.criar(dados)

    async def listar(self, autor, categoria=None):
        igreja_id = getattr(autor, "igreja_id", None)
        return await self.repo.listar(igreja_id=igreja_id, categoria=categoria)

    async def deletar(self, obj_id, autor):
        f = await self.repo.buscar_por_id(obj_id)
        if not f:
            raise NotFoundError("Ferramenta", str(obj_id))
        await self.repo.deletar(f)
'''


# ============================================================
# 5. ROUTER — endpoints Anotacao + Ferramenta
# ============================================================
router_extra = '''


# ============ ANOTACOES ============

@router.post("/pessoas/{pessoa_id}/anotacoes/", response_model=AnotacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_anotacao(
    pessoa_id: UUID,
    dados: AnotacaoCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await AnotacaoService(db).criar(pessoa_id, dados.model_dump(), usuario)


@router.get("/pessoas/{pessoa_id}/anotacoes/", response_model=list[AnotacaoResponse])
async def listar_anotacoes(
    pessoa_id: UUID,
    modulo_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await AnotacaoService(db).listar(pessoa_id, modulo_id)


@router.put("/anotacoes/{anotacao_id}", response_model=AnotacaoResponse)
async def atualizar_anotacao(
    anotacao_id: UUID,
    dados: AnotacaoUpdate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await AnotacaoService(db).atualizar(anotacao_id, dados.model_dump(exclude_unset=True), usuario)


@router.delete("/anotacoes/{anotacao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_anotacao(
    anotacao_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await AnotacaoService(db).deletar(anotacao_id, usuario)


# ============ FERRAMENTAS ============

@router.post("/ferramentas/", response_model=FerramentaResponse, status_code=status.HTTP_201_CREATED)
async def criar_ferramenta(
    dados: FerramentaCreate,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await FerramentaService(db).criar(dados.model_dump(), usuario)


@router.get("/ferramentas/", response_model=list[FerramentaResponse])
async def listar_ferramentas(
    categoria: str | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await FerramentaService(db).listar(usuario, categoria)


@router.delete("/ferramentas/{ferramenta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_ferramenta(
    ferramenta_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await FerramentaService(db).deletar(ferramenta_id, usuario)
'''


# ============================================================
# FUNCOES DE APLICACAO
# ============================================================

def aplicar_models():
    escrever_se_faltar(
        BACKEND / "app" / "modules" / "estudo" / "models.py",
        "class Anotacao(",
        models_extra,
    )


def aplicar_schemas():
    escrever_se_faltar(
        BACKEND / "app" / "modules" / "estudo" / "schemas.py",
        "class AnotacaoCreate",
        schemas_extra,
    )


def aplicar_repositorios():
    escrever_se_faltar(
        BACKEND / "app" / "modules" / "estudo" / "repository.py",
        "class AnotacaoRepository",
        repo_extra,
    )


def aplicar_services():
    p = BACKEND / "app" / "modules" / "estudo" / "service.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class AnotacaoService" in c:
        print(f"  [SKIP] service.py ja tem AnotacaoService")
        return

    # Adiciona imports
    if "AnotacaoRepository" not in c and "from app.modules.estudo.repository import" in c:
        if "CertificadoRepository" in c:
            c = c.replace(
                "CertificadoRepository,",
                "AnotacaoRepository,\n    CertificadoRepository,\n    FerramentaRepository,",
                1,
            )
        else:
            c = c.replace(
                "from app.modules.estudo.repository import (",
                "from app.modules.estudo.repository import (\n    AnotacaoRepository,\n    FerramentaRepository,",
                1,
            )

    c = c.rstrip() + service_extra
    backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
    shutil.copy2(p, backup)
    p.write_text(c, encoding="utf-8")
    print(f"  [BACKUP] {backup.name}")
    print(f"  [OK] service.py atualizado")


def aplicar_router_endpoints():
    p = BACKEND / "app" / "modules" / "estudo" / "router.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "/anotacoes/" in c:
        print(f"  [SKIP] router.py ja tem anotacoes")
        return

    # Imports de schemas
    if "AnotacaoCreate" not in c:
        c = c.replace(
            "from app.modules.estudo.schemas import (",
            "from app.modules.estudo.schemas import (\n    AnotacaoCreate,\n    AnotacaoResponse,\n    AnotacaoUpdate,",
            1,
        )
    if "FerramentaCreate" not in c:
        c = c.replace(
            "    DashboardTurmas,",
            "    DashboardTurmas,\n    FerramentaCreate,\n    FerramentaResponse,",
            1,
        )

    # Imports de services
    if "AnotacaoService" not in c:
        c = c.replace(
            "from app.modules.estudo.service import (",
            "from app.modules.estudo.service import (\n    AnotacaoService,",
            1,
        )
    if "FerramentaService" not in c:
        c = c.replace(
            "from app.modules.estudo.service import (",
            "from app.modules.estudo.service import (\n    FerramentaService,",
            1,
        )

    c = c.rstrip() + router_extra
    backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
    shutil.copy2(p, backup)
    p.write_text(c, encoding="utf-8")
    print(f"  [BACKUP] {backup.name}")
    print(f"  [OK] router.py atualizado")


def registrar_router_publico():
    p = BACKEND / "app" / "api" / "router.py"
    if not p.exists():
        print(f"  [ERRO] api/router.py nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "estudo_publico_router" in c:
        print(f"  [SKIP] api/router.py ja tem estudo_publico_router")
        return

    # Import
    c = c.replace(
        "from app.modules.estudo.router import router as estudo_router",
        "from app.modules.estudo.router import router as estudo_router\n"
        "from app.modules.estudo.router_publico import router as estudo_publico_router",
        1,
    )
    # Include
    c = c.replace(
        "api_router.include_router(estudo_router)",
        "api_router.include_router(estudo_router)\n"
        "api_router.include_router(estudo_publico_router)",
        1,
    )

    backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
    shutil.copy2(p, backup)
    p.write_text(c, encoding="utf-8")
    print(f"  [BACKUP] {backup.name}")
    print(f"  [OK] api/router.py atualizado")


def adicionar_static_media():
    p = BACKEND / "app" / "main.py"
    if not p.exists():
        print(f"  [ERRO] main.py nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if 'app.mount("/media"' in c or "app.mount('/media'" in c:
        print(f"  [SKIP] main.py ja tem /media montado")
        return

    # 1. Import StaticFiles
    if "from fastapi.staticfiles import StaticFiles" not in c:
        c = c.replace(
            "from fastapi import FastAPI, Request, status",
            "from fastapi import FastAPI, Request, status\nfrom fastapi.staticfiles import StaticFiles",
            1,
        )

    # 2. Mount apos include_router
    marcador = "app.include_router(api_router, prefix=settings.API_V1_PREFIX)"
    if marcador in c:
        c = c.replace(
            marcador,
            marcador + "\n\n\n"
            "# ============================================================\n"
            "# STATIC FILES — certificados PDF\n"
            "# ============================================================\n"
            "from pathlib import Path as _Path\n"
            "_media_dir = _Path(__file__).parent.parent / 'media'\n"
            "_media_dir.mkdir(exist_ok=True)\n"
            "app.mount('/media', StaticFiles(directory=str(_media_dir)), name='media')",
            1,
        )

    backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
    shutil.copy2(p, backup)
    p.write_text(c, encoding="utf-8")
    print(f"  [BACKUP] {backup.name}")
    print(f"  [OK] main.py atualizado (com /media)")


# ============================================================
# EXECUTAR
# ============================================================
print(f"Backend: {BACKEND}")
print()
print("Fix Bloco 4 — Anotacao + FerramentaEstudo + Public Router + Static")
print()

aplicar_models()
aplicar_schemas()
aplicar_repositorios()
aplicar_services()
aplicar_router_endpoints()
registrar_router_publico()
adicionar_static_media()

print()
print("=" * 60)
print("PRONTO! Rode agora:")
print("  alembic revision --autogenerate -m 'estudo bloco 4'")
print("  alembic upgrade head")
print("=" * 60)