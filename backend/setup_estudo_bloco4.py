"""Estudo Bloco 4 — Certificados + Anotacoes + Ferramentas de Estudo."""
import argparse, shutil
from datetime import datetime
from pathlib import Path

BACKEND = Path(__file__).parent.resolve()
PROJETO = BACKEND.parent

parser = argparse.ArgumentParser()
parser.add_argument("--force", action="store_true")
args = parser.parse_args()
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")


def escrever(caminho: Path, conteudo: str):
    if caminho.exists():
        if not args.force:
            print(f"  [SKIP] {caminho.relative_to(PROJETO)}")
            return
        backup = caminho.with_suffix(caminho.suffix + f".bak.{STAMP}")
        shutil.copy2(caminho, backup)
        print(f"  [BACKUP] {backup.name}")
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    print(f"  [OK] {caminho.relative_to(PROJETO)}")


# ============================================================
# 1. MODELS
# ============================================================
models_extra = '''

class Certificado(Base, UUIDMixin, TimestampMixin):
    """Certificado de conclusao de curso."""
    __tablename__ = "certificados"
    __table_args__ = (
        UniqueConstraint("matricula_id", name="uq_certificados_matricula"),
        UniqueConstraint("codigo", name="uq_certificados_codigo"),
    )

    matricula_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("matriculas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    pessoa_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("pessoas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    curso_id: Mapped["PGUUID | None"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("cursos.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    igreja_id: Mapped["PGUUID"] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("igrejas.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    codigo: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    carga_horaria: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nota_final: Mapped[float | None] = mapped_column("nota_final", nullable=True)
    emitido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    url_pdf: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cancelado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    matricula = relationship("Matricula", lazy="joined")
    pessoa = relationship("Pessoa", lazy="joined")
    curso = relationship("Curso", lazy="joined")


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


def adicionar_models():
    p = BACKEND / "app" / "modules" / "estudo" / "models.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class Certificado(" in c:
        print("  [SKIP] models.py ja tem Certificado")
        return
    # Ajusta imports no topo
    if "from datetime import datetime" not in c:
        c = "from datetime import datetime\n" + c
    if "DateTime" not in c:
        c = c.replace(
            "from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint",
            "from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint",
        )
    c = c.rstrip() + models_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] models.py atualizado (+3 tabelas)")


# ============================================================
# 2. SCHEMAS
# ============================================================
schemas_extra = '''

# ============ CERTIFICADO ============

class CertificadoCreate(BaseModel):
    carga_horaria: int | None = None


class CertificadoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    matricula_id: UUID
    pessoa_id: UUID
    curso_id: UUID | None = None
    igreja_id: UUID
    codigo: str
    carga_horaria: int | None = None
    nota_final: float | None = None
    emitido_em: datetime
    url_pdf: str | None = None
    cancelado: bool


class CertificadoValidacao(BaseModel):
    valido: bool
    codigo: str
    nome_aluno: str | None = None
    nome_curso: str | None = None
    nome_igreja: str | None = None
    carga_horaria: int | None = None
    nota_final: float | None = None
    emitido_em: datetime | None = None
    mensagem: str | None = None


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


def adicionar_schemas():
    p = BACKEND / "app" / "modules" / "estudo" / "schemas.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class CertificadoCreate" in c:
        print("  [SKIP] schemas.py ja tem Certificado")
        return
    c = c.rstrip() + schemas_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] schemas.py atualizado")


# ============================================================
# 3. REPOSITORY
# ============================================================
repo_extra = '''

class CertificadoRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Certificado
        c = Certificado(**dados)
        self.db.add(c)
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Certificado
        r = await self.db.execute(select(Certificado).where(Certificado.id == obj_id))
        return r.scalar_one_or_none()

    async def buscar_por_matricula(self, matricula_id):
        from app.modules.estudo.models import Certificado
        r = await self.db.execute(
            select(Certificado).where(Certificado.matricula_id == matricula_id)
        )
        return r.scalar_one_or_none()

    async def buscar_por_codigo(self, codigo):
        from app.modules.estudo.models import Certificado
        r = await self.db.execute(
            select(Certificado).where(Certificado.codigo == codigo)
        )
        return r.scalar_one_or_none()

    async def listar_por_igreja(self, igreja_id):
        from app.modules.estudo.models import Certificado
        r = await self.db.execute(
            select(Certificado)
            .where(Certificado.igreja_id == igreja_id, Certificado.cancelado.is_(False))
            .order_by(Certificado.emitido_em.desc())
        )
        return list(r.scalars().all())

    async def listar_por_pessoa(self, pessoa_id):
        from app.modules.estudo.models import Certificado
        r = await self.db.execute(
            select(Certificado)
            .where(Certificado.pessoa_id == pessoa_id, Certificado.cancelado.is_(False))
            .order_by(Certificado.emitido_em.desc())
        )
        return list(r.scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


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


def adicionar_repositorios():
    p = BACKEND / "app" / "modules" / "estudo" / "repository.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class CertificadoRepository" in c:
        print("  [SKIP] repository.py ja tem CertificadoRepository")
        return
    c = c.rstrip() + repo_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] repository.py atualizado (+3 repositorios)")


# ============================================================
# MARCADOR — PARTE 2 CONTINUA AQUI
# ============================================================
# ============================================================
# 4. SERVICE
# ============================================================
service_extra = '''

class CertificadoService:
    def __init__(self, db):
        self.db = db
        self.repo = CertificadoRepository(db)

    def _gerar_codigo(self):
        import secrets
        return "CERT-" + secrets.token_hex(6).upper()

    async def emitir(self, matricula_id, autor, carga_horaria=None):
        from app.modules.estudo.repository import MatriculaRepository
        from app.modules.estudo.models import Curso
        from app.modules.igreja.repository import IgrejaRepository

        mat = await MatriculaRepository(self.db).buscar_por_id(matricula_id)
        if not mat:
            raise NotFoundError("Matricula", str(matricula_id))
        if mat.status != "aprovado":
            raise BusinessRuleError("Matricula ainda nao foi aprovada")

        existente = await self.repo.buscar_por_matricula(matricula_id)
        if existente and not existente.cancelado:
            return existente

        turma = getattr(mat, "turma", None)
        curso_id = getattr(turma, "curso_id", None) if turma else None
        curso = None
        if curso_id:
            r = await self.db.execute(select(Curso).where(Curso.id == curso_id))
            curso = r.scalar_one_or_none()

        igreja_id = getattr(autor, "igreja_id", None)
        if not igreja_id:
            igrejas = await IgrejaRepository(self.db).listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            igreja_id = igrejas[0].id

        dados = {
            "matricula_id": matricula_id,
            "pessoa_id": mat.pessoa_id,
            "curso_id": curso_id,
            "igreja_id": igreja_id,
            "codigo": self._gerar_codigo(),
            "carga_horaria": carga_horaria or (getattr(curso, "carga_horaria", None) if curso else None),
            "nota_final": getattr(mat, "nota_final", None),
        }

        if existente:
            return await self.repo.atualizar(existente, {**dados, "cancelado": False})

        cert = await self.repo.criar(dados)
        try:
            url = await self._gerar_pdf(cert)
            cert = await self.repo.atualizar(cert, {"url_pdf": url})
        except BusinessRuleError:
            pass  # reportlab nao instalado — nao bloqueia a emissao
        return cert

    async def _gerar_pdf(self, cert):
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
        except ImportError:
            raise BusinessRuleError("reportlab nao instalado. Rode: pip install reportlab")

        from app.modules.pessoas.models import Pessoa
        from app.modules.igreja.models import Igreja
        from app.modules.estudo.models import Curso

        pessoa = (await self.db.execute(select(Pessoa).where(Pessoa.id == cert.pessoa_id))).scalar_one_or_none()
        curso = None
        if cert.curso_id:
            curso = (await self.db.execute(select(Curso).where(Curso.id == cert.curso_id))).scalar_one_or_none()
        igreja = (await self.db.execute(select(Igreja).where(Igreja.id == cert.igreja_id))).scalar_one_or_none()

        pasta = BACKEND / "media" / "certificados"
        pasta.mkdir(parents=True, exist_ok=True)
        nome_arquivo = f"{cert.codigo}.pdf"
        caminho_pdf = pasta / nome_arquivo

        c = canvas.Canvas(str(caminho_pdf), pagesize=landscape(A4))
        w, h = landscape(A4)

        c.setLineWidth(3)
        c.rect(1*cm, 1*cm, w - 2*cm, h - 2*cm)
        c.setLineWidth(1)
        c.rect(1.3*cm, 1.3*cm, w - 2.6*cm, h - 2.6*cm)

        c.setFont("Helvetica-Bold", 32)
        c.drawCentredString(w/2, h - 4*cm, "CERTIFICADO")

        c.setFont("Helvetica", 14)
        c.drawCentredString(w/2, h - 5.5*cm, "Certificamos que")

        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(w/2, h - 7.5*cm, pessoa.nome if pessoa else "Aluno")

        c.setFont("Helvetica", 14)
        c.drawCentredString(w/2, h - 9.2*cm, "concluiu com exito o curso")

        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(w/2, h - 10.8*cm, getattr(curso, "nome", "Curso") if curso else "Curso")

        if cert.carga_horaria:
            c.setFont("Helvetica", 12)
            c.drawCentredString(w/2, h - 12*cm, f"Carga horaria: {cert.carga_horaria}h")

        if cert.nota_final is not None:
            c.setFont("Helvetica", 12)
            c.drawCentredString(w/2, h - 12.8*cm, f"Nota final: {cert.nota_final}")

        c.setFont("Helvetica", 11)
        c.drawCentredString(w/2, h - 15*cm, f"Codigo de validacao: {cert.codigo}")
        c.drawCentredString(w/2, h - 15.8*cm, f"Emitido em: {cert.emitido_em.strftime('%d/%m/%Y')}")

        c.line(w/2 - 8*cm, 4*cm, w/2 - 2*cm, 4*cm)
        c.drawCentredString(w/2 - 5*cm, 3.4*cm, "Diretor(a) de Ensino")

        c.line(w/2 + 2*cm, 4*cm, w/2 + 8*cm, 4*cm)
        c.drawCentredString(w/2 + 5*cm, 3.4*cm, getattr(igreja, "nome", "Igreja") if igreja else "Igreja")

        c.showPage()
        c.save()

        return f"/media/certificados/{nome_arquivo}"

    async def buscar(self, obj_id):
        c = await self.repo.buscar_por_id(obj_id)
        if not c:
            raise NotFoundError("Certificado", str(obj_id))
        return c

    async def listar(self, autor):
        igreja_id = getattr(autor, "igreja_id", None)
        if not igreja_id:
            return []
        return await self.repo.listar_por_igreja(igreja_id)

    async def listar_por_pessoa(self, pessoa_id):
        return await self.repo.listar_por_pessoa(pessoa_id)

    async def validar(self, codigo):
        from app.modules.pessoas.models import Pessoa
        from app.modules.igreja.models import Igreja
        from app.modules.estudo.models import Curso

        c = await self.repo.buscar_por_codigo(codigo)
        if not c or c.cancelado:
            return {"valido": False, "codigo": codigo, "mensagem": "Certificado nao encontrado"}

        pessoa = (await self.db.execute(select(Pessoa).where(Pessoa.id == c.pessoa_id))).scalar_one_or_none()
        curso = None
        if c.curso_id:
            curso = (await self.db.execute(select(Curso).where(Curso.id == c.curso_id))).scalar_one_or_none()
        igreja = (await self.db.execute(select(Igreja).where(Igreja.id == c.igreja_id))).scalar_one_or_none()

        return {
            "valido": True,
            "codigo": c.codigo,
            "nome_aluno": getattr(pessoa, "nome", None),
            "nome_curso": getattr(curso, "nome", None),
            "nome_igreja": getattr(igreja, "nome", None),
            "carga_horaria": c.carga_horaria,
            "nota_final": c.nota_final,
            "emitido_em": c.emitido_em,
            "mensagem": "Certificado autentico",
        }

    async def cancelar(self, obj_id, autor):
        c = await self.buscar(obj_id)
        return await self.repo.atualizar(c, {"cancelado": True})


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


def adicionar_services():
    p = BACKEND / "app" / "modules" / "estudo" / "service.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "class CertificadoService" in c:
        print("  [SKIP] service.py ja tem CertificadoService")
        return

    # Adiciona imports necessarios
    if "CertificadoRepository" not in c and "from app.modules.estudo.repository import" in c:
        c = c.replace(
            "from app.modules.estudo.repository import (\n    BadgeRepository,",
            "from app.modules.estudo.repository import (\n    AnotacaoRepository,\n    BadgeRepository,\n    CertificadoRepository,\n    FerramentaRepository,",
        )

    c = c.rstrip() + service_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] service.py atualizado (+3 services)")


# ============================================================
# 5. ROUTER
# ============================================================
router_extra = '''

# ============ CERTIFICADOS ============

@router.post("/matriculas/{matricula_id}/certificado", response_model=CertificadoResponse, status_code=status.HTTP_201_CREATED)
async def emitir_certificado(
    matricula_id: UUID,
    dados: CertificadoCreate | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    carga = dados.carga_horaria if dados else None
    return await CertificadoService(db).emitir(matricula_id, usuario, carga_horaria=carga)


@router.get("/certificados/", response_model=list[CertificadoResponse])
async def listar_certificados(
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await CertificadoService(db).listar(usuario)


@router.get("/pessoas/{pessoa_id}/certificados/", response_model=list[CertificadoResponse])
async def listar_certificados_pessoa(
    pessoa_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await CertificadoService(db).listar_por_pessoa(pessoa_id)


@router.get("/certificados/{certificado_id}", response_model=CertificadoResponse)
async def buscar_certificado(
    certificado_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await CertificadoService(db).buscar(certificado_id)


@router.delete("/certificados/{certificado_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancelar_certificado(
    certificado_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    await CertificadoService(db).cancelar(certificado_id, usuario)


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


def adicionar_router():
    p = BACKEND / "app" / "modules" / "estudo" / "router.py"
    if not p.exists():
        print(f"  [ERRO] {p.name} nao existe")
        return
    c = p.read_text(encoding="utf-8")
    if "/certificados/" in c:
        print("  [SKIP] router.py ja tem certificados")
        return

    # Adiciona imports de schemas
    if "CertificadoCreate" not in c:
        c = c.replace(
            "from app.modules.estudo.schemas import (\n    BadgeCreate,",
            "from app.modules.estudo.schemas import (\n    AnotacaoCreate,\n    AnotacaoResponse,\n    AnotacaoUpdate,\n    BadgeCreate,\n    CertificadoCreate,\n    CertificadoResponse,",
        )
    if "FerramentaCreate" not in c:
        c = c.replace(
            "    DashboardTurmas,",
            "    DashboardTurmas,\n    FerramentaCreate,\n    FerramentaResponse,",
        )

    # Adiciona imports de services
    if "CertificadoService" not in c:
        c = c.replace(
            "from app.modules.estudo.service import (\n    BadgeService,",
            "from app.modules.estudo.service import (\n    AnotacaoService,\n    BadgeService,\n    CertificadoService,\n    FerramentaService,",
        )

    c = c.rstrip() + router_extra
    if args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(c, encoding="utf-8")
    print(f"  [OK] router.py atualizado (+12 endpoints)")


# ============================================================
# 6. ROUTER PUBLICO (validacao)
# ============================================================
router_publico = '''"""Rotas publicas — validacao de certificado."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database.connection import get_db
from app.modules.estudo.schemas import CertificadoValidacao
from app.modules.estudo.service import CertificadoService

router = APIRouter(prefix="/publico", tags=["Publico"])


@router.get("/certificados/validar/{codigo}", response_model=CertificadoValidacao)
async def validar_certificado(codigo: str, db: AsyncSession = Depends(get_db)):
    resultado = await CertificadoService(db).validar(codigo)
    if not resultado.get("valido"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=resultado.get("mensagem", "Certificado nao encontrado"),
        )
    return resultado
'''


def criar_router_publico():
    p = BACKEND / "app" / "modules" / "estudo" / "router_publico.py"
    if p.exists() and not args.force:
        print(f"  [SKIP] {p.name} ja existe")
        return
    if p.exists() and args.force:
        backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
        shutil.copy2(p, backup)
        print(f"  [BACKUP] {backup.name}")
    p.write_text(router_publico, encoding="utf-8")
    print(f"  [OK] {p.name} criado")


# ============================================================
# 7. REGISTRAR ROUTER PUBLICO NO MAIN
# ============================================================
def registrar_no_main():
    p = BACKEND / "app" / "main.py"
    if not p.exists():
        print(f"  [AVISO] main.py nao encontrado")
        return
    c = p.read_text(encoding="utf-8")
    alterou = False

    # Import
    if "estudo_publico_router" not in c:
        if "from app.modules.estudo.router import router as estudo_router" in c:
            c = c.replace(
                "from app.modules.estudo.router import router as estudo_router",
                "from app.modules.estudo.router import router as estudo_router\n"
                "from app.modules.estudo.router_publico import router as estudo_publico_router",
            )
            alterou = True
        else:
            print("  [AVISO] nao achei 'from app.modules.estudo.router import router as estudo_router' no main.py")
            print("         adicione manualmente: from app.modules.estudo.router_publico import router as estudo_publico_router")

    # Include router
    if "estudo_publico_router" not in c:
        print("  [AVISO] nao consegui incluir o estudo_publico_router")
    elif "app.include_router(estudo_publico_router" not in c:
        if "app.include_router(estudo_router)" in c:
            c = c.replace(
                "app.include_router(estudo_router)",
                "app.include_router(estudo_router)\n"
                "    app.include_router(estudo_publico_router)",
            )
            alterou = True

    # StaticFiles para /media
    if "StaticFiles" not in c:
        if "from fastapi import FastAPI" in c:
            c = c.replace(
                "from fastapi import FastAPI",
                "from fastapi import FastAPI\nfrom fastapi.staticfiles import StaticFiles",
            )
            alterou = True
        # Mount
        if "app.mount('/media'" not in c and "app.mount(\"/media\"" not in c:
            # Procura onde colocar — depois dos include_router
            if "app.include_router(estudo_publico_router)" in c:
                c = c.replace(
                    "app.include_router(estudo_publico_router)",
                    "app.include_router(estudo_publico_router)\n\n"
                    "    # Static files (certificados PDF)\n"
                    "    from pathlib import Path as _Path\n"
                    "    _media_dir = _Path(__file__).parent.parent / 'media'\n"
                    "    _media_dir.mkdir(exist_ok=True)\n"
                    "    app.mount('/media', StaticFiles(directory=str(_media_dir)), name='media')",
                )
                alterou = True

    if alterou:
        if args.force:
            backup = p.with_suffix(p.suffix + f".bak.{STAMP}")
            shutil.copy2(p, backup)
            print(f"  [BACKUP] {backup.name}")
        p.write_text(c, encoding="utf-8")
        print(f"  [OK] main.py atualizado")
    else:
        print("  [SKIP] main.py sem alteracoes necessarias")


# ============================================================
# RUNNER
# ============================================================
print(f"Backend: {BACKEND}")
print()
print("Estudo Bloco 4 — Certificados + Anotacoes + Ferramentas")
print()

adicionar_models()
adicionar_schemas()
adicionar_repositorios()
adicionar_services()
adicionar_router()
criar_router_publico()
registrar_no_main()

print()
print("=" * 60)
print("PRONTO! Rode agora:")
print("  alembic revision --autogenerate -m 'estudo bloco 4'")
print("  alembic upgrade head")
print("=" * 60)