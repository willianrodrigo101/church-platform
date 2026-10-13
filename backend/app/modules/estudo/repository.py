from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.estudo.models import (
    ConteudoModulo,
    Curso,
    ModuloCurso,
    TrilhaFormacao,
)


class TrilhaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> TrilhaFormacao:
        obj = TrilhaFormacao(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id: UUID) -> TrilhaFormacao | None:
        stmt = (
            select(TrilhaFormacao)
            .options(selectinload(TrilhaFormacao.cursos))
            .where(TrilhaFormacao.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar(self, skip=0, limit=100, igreja_id=None, nivel=None, apenas_ativas=False):
        stmt = (
            select(TrilhaFormacao)
            .options(selectinload(TrilhaFormacao.cursos))
            .order_by(TrilhaFormacao.ordem.asc(), TrilhaFormacao.nome.asc())
        )
        if igreja_id: stmt = stmt.where(TrilhaFormacao.igreja_id == igreja_id)
        if nivel: stmt = stmt.where(TrilhaFormacao.nivel == nivel)
        if apenas_ativas: stmt = stmt.where(TrilhaFormacao.ativa.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class CursoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict, modulos: list[dict]) -> Curso:
        curso = Curso(**dados)
        self.db.add(curso)
        await self.db.flush()
        for m in modulos:
            conteudos = m.pop("conteudos", []) or []
            mod = ModuloCurso(curso_id=curso.id, **m)
            self.db.add(mod)
            await self.db.flush()
            for i, c in enumerate(conteudos, start=1):
                c["ordem"] = c.get("ordem") or i
                conteudo = ConteudoModulo(modulo_id=mod.id, **c)
                self.db.add(conteudo)
        await self.db.flush()
        await self.db.refresh(curso)
        return curso

    async def buscar_por_id(self, obj_id: UUID) -> Curso | None:
        stmt = (
            select(Curso)
            .options(
                selectinload(Curso.modulos).selectinload(ModuloCurso.conteudos),
            )
            .where(Curso.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar(
        self, skip=0, limit=100,
        igreja_id=None, trilha_id=None, tipo=None, nivel=None,
        apenas_ativos=False,
    ):
        stmt = (
            select(Curso)
            .options(selectinload(Curso.modulos))
            .order_by(Curso.ordem.asc(), Curso.nome.asc())
        )
        if igreja_id: stmt = stmt.where(Curso.igreja_id == igreja_id)
        if trilha_id: stmt = stmt.where(Curso.trilha_id == trilha_id)
        if tipo: stmt = stmt.where(Curso.tipo == tipo)
        if nivel: stmt = stmt.where(Curso.nivel == nivel)
        if apenas_ativos: stmt = stmt.where(Curso.ativo.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()

    async def contar_por_tipo(self, igreja_id=None) -> dict:
        stmt = select(Curso.tipo, func.count(Curso.id)).group_by(Curso.tipo)
        if igreja_id: stmt = stmt.where(Curso.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return {row[0]: row[1] for row in r.all()}

    async def contar_por_nivel(self, igreja_id=None) -> dict:
        stmt = select(Curso.nivel, func.count(Curso.id)).group_by(Curso.nivel)
        if igreja_id: stmt = stmt.where(Curso.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return {row[0]: row[1] for row in r.all()}


class ModuloRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict, conteudos: list[dict] | None = None) -> ModuloCurso:
        mod = ModuloCurso(**dados)
        self.db.add(mod)
        await self.db.flush()
        if conteudos:
            for i, c in enumerate(conteudos, start=1):
                c["ordem"] = c.get("ordem") or i
                self.db.add(ConteudoModulo(modulo_id=mod.id, **c))
        await self.db.flush()
        await self.db.refresh(mod)
        return mod

    async def buscar_por_id(self, obj_id: UUID) -> ModuloCurso | None:
        stmt = (
            select(ModuloCurso)
            .options(selectinload(ModuloCurso.conteudos))
            .where(ModuloCurso.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar_por_curso(self, curso_id: UUID):
        stmt = (
            select(ModuloCurso)
            .options(selectinload(ModuloCurso.conteudos))
            .where(ModuloCurso.curso_id == curso_id)
            .order_by(ModuloCurso.ordem.asc())
        )
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class ConteudoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def criar(self, dados: dict) -> ConteudoModulo:
        obj = ConteudoModulo(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def listar_por_modulo(self, modulo_id: UUID):
        stmt = select(ConteudoModulo).where(
            ConteudoModulo.modulo_id == modulo_id
        ).order_by(ConteudoModulo.ordem.asc())
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def buscar_por_id(self, obj_id: UUID) -> ConteudoModulo | None:
        r = await self.db.execute(select(ConteudoModulo).where(ConteudoModulo.id == obj_id))
        return r.scalar_one_or_none()

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()

class TurmaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Turma
        obj = Turma(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Turma
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Turma)
            .options(selectinload(Turma.matriculas))
            .where(Turma.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar(self, skip=0, limit=100, igreja_id=None, curso_id=None, status=None, apenas_ativas=False):
        from app.modules.estudo.models import Turma
        stmt = select(Turma).order_by(Turma.created_at.desc())
        if igreja_id: stmt = stmt.where(Turma.igreja_id == igreja_id)
        if curso_id: stmt = stmt.where(Turma.curso_id == curso_id)
        if status: stmt = stmt.where(Turma.status == status)
        if apenas_ativas: stmt = stmt.where(Turma.ativa.is_(True))
        stmt = stmt.offset(skip).limit(limit)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()

    async def contar_matriculas(self, turma_id):
        from app.modules.estudo.models import Matricula
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(Matricula.id)).where(Matricula.turma_id == turma_id)
        )
        return r.scalar_one()


class MatriculaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Matricula
        obj = Matricula(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Matricula
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Matricula)
            .options(selectinload(Matricula.progresso_modulos))
            .where(Matricula.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def buscar_por_turma_e_pessoa(self, turma_id, pessoa_id):
        from app.modules.estudo.models import Matricula
        r = await self.db.execute(
            select(Matricula).where(
                Matricula.turma_id == turma_id,
                Matricula.pessoa_id == pessoa_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar_por_turma(self, turma_id):
        from app.modules.estudo.models import Matricula
        r = await self.db.execute(
            select(Matricula).where(Matricula.turma_id == turma_id).order_by(Matricula.created_at.asc())
        )
        return list(r.scalars().all())

    async def listar_por_pessoa(self, pessoa_id, igreja_id=None):
        from app.modules.estudo.models import Matricula
        stmt = select(Matricula).where(Matricula.pessoa_id == pessoa_id).order_by(Matricula.created_at.desc())
        if igreja_id: stmt = stmt.where(Matricula.igreja_id == igreja_id)
        r = await self.db.execute(stmt)
        return list(r.scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            if v is not None:
                setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class ProgressoModuloRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import ProgressoModulo
        obj = ProgressoModulo(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar_por_matricula_e_modulo(self, matricula_id, modulo_id):
        from app.modules.estudo.models import ProgressoModulo
        r = await self.db.execute(
            select(ProgressoModulo).where(
                ProgressoModulo.matricula_id == matricula_id,
                ProgressoModulo.modulo_id == modulo_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar_por_matricula(self, matricula_id):
        from app.modules.estudo.models import ProgressoModulo
        r = await self.db.execute(
            select(ProgressoModulo).where(ProgressoModulo.matricula_id == matricula_id)
        )
        return list(r.scalars().all())

    async def atualizar(self, obj, dados):
        for k, v in dados.items():
            setattr(obj, k, v)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj


class PresencaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Presenca
        obj = Presenca(**dados)
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def buscar(self, matricula_id, modulo_id, data_aula):
        from app.modules.estudo.models import Presenca
        stmt = select(Presenca).where(
            Presenca.matricula_id == matricula_id,
            Presenca.data_aula == data_aula,
        )
        if modulo_id:
            stmt = stmt.where(Presenca.modulo_id == modulo_id)
        else:
            stmt = stmt.where(Presenca.modulo_id.is_(None))
        r = await self.db.execute(stmt)
        return r.scalar_one_or_none()

    async def listar_por_matricula(self, matricula_id):
        from app.modules.estudo.models import Presenca
        r = await self.db.execute(
            select(Presenca).where(Presenca.matricula_id == matricula_id).order_by(Presenca.data_aula.asc())
        )
        return list(r.scalars().all())

    async def contar_presentes(self, turma_id):
        from app.modules.estudo.models import Presenca, Matricula
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(Presenca.id))
            .join(Matricula, Matricula.id == Presenca.matricula_id)
            .where(Matricula.turma_id == turma_id, Presenca.presente.is_(True))
        )
        return r.scalar_one()

    async def contar_total(self, turma_id):
        from app.modules.estudo.models import Presenca, Matricula
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(Presenca.id))
            .join(Matricula, Matricula.id == Presenca.matricula_id)
            .where(Matricula.turma_id == turma_id)
        )
        return r.scalar_one()

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

    async def listar_por_igreja(self, igreja_id, apenas_ativos=True):
        from app.modules.estudo.models import Certificado
        stmt = select(Certificado).where(Certificado.igreja_id == igreja_id)
        if apenas_ativos:
            stmt = stmt.where(Certificado.cancelado.is_(False))
        stmt = stmt.order_by(Certificado.emitido_em.desc())
        r = await self.db.execute(stmt)
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

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()

class QuizRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados, perguntas):
        import json
        from app.modules.estudo.models import Quiz, PerguntaQuiz
        q = Quiz(**dados)
        self.db.add(q)
        await self.db.flush()
        for p in perguntas:
            opcoes = p.pop("opcoes", [])
            pergunta = PerguntaQuiz(quiz_id=q.id, opcoes=json.dumps(opcoes), **p)
            self.db.add(pergunta)
        await self.db.flush()
        await self.db.refresh(q)
        return q

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Quiz
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Quiz)
            .options(selectinload(Quiz.perguntas))
            .where(Quiz.id == obj_id)
        )
        r = await self.db.execute(stmt)
        return r.unique().scalar_one_or_none()

    async def listar_por_modulo(self, modulo_id):
        from app.modules.estudo.models import Quiz
        from sqlalchemy.orm import selectinload
        stmt = (
            select(Quiz)
            .options(selectinload(Quiz.perguntas))
            .where(Quiz.modulo_id == modulo_id)
        )
        r = await self.db.execute(stmt)
        return list(r.unique().scalars().all())

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class TentativaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import TentativaQuiz
        t = TentativaQuiz(**dados)
        self.db.add(t)
        await self.db.flush()
        await self.db.refresh(t)
        return t

    async def contar_por_quiz_e_matricula(self, quiz_id, matricula_id):
        from app.modules.estudo.models import TentativaQuiz
        from sqlalchemy import func
        r = await self.db.execute(
            select(func.count(TentativaQuiz.id)).where(
                TentativaQuiz.quiz_id == quiz_id,
                TentativaQuiz.matricula_id == matricula_id,
            )
        )
        return r.scalar_one()

    async def listar_por_quiz(self, quiz_id):
        from app.modules.estudo.models import TentativaQuiz
        r = await self.db.execute(
            select(TentativaQuiz).where(TentativaQuiz.quiz_id == quiz_id)
            .order_by(TentativaQuiz.nota.desc())
        )
        return list(r.scalars().all())


class ComentarioRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Comentario
        c = Comentario(**dados)
        self.db.add(c)
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def listar_por_modulo(self, modulo_id):
        from app.modules.estudo.models import Comentario
        r = await self.db.execute(
            select(Comentario).where(Comentario.modulo_id == modulo_id)
            .order_by(Comentario.fixado.desc(), Comentario.created_at.asc())
        )
        return list(r.scalars().all())

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class BadgeRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Badge
        b = Badge(**dados)
        self.db.add(b)
        await self.db.flush()
        await self.db.refresh(b)
        return b

    async def listar(self, igreja_id):
        from app.modules.estudo.models import Badge
        r = await self.db.execute(
            select(Badge).where(Badge.igreja_id == igreja_id).order_by(Badge.pontos.desc())
        )
        return list(r.scalars().all())

    async def buscar_por_id(self, obj_id):
        from app.modules.estudo.models import Badge
        r = await self.db.execute(select(Badge).where(Badge.id == obj_id))
        return r.scalar_one_or_none()

    async def buscar_por_codigo(self, igreja_id, codigo):
        from app.modules.estudo.models import Badge
        r = await self.db.execute(
            select(Badge).where(Badge.igreja_id == igreja_id, Badge.codigo == codigo)
        )
        return r.scalar_one_or_none()

    async def deletar(self, obj):
        await self.db.delete(obj)
        await self.db.flush()


class ConquistaRepository:
    def __init__(self, db):
        self.db = db

    async def criar(self, dados):
        from app.modules.estudo.models import Conquista
        c = Conquista(**dados)
        self.db.add(c)
        await self.db.flush()
        await self.db.refresh(c)
        return c

    async def buscar(self, badge_id, pessoa_id):
        from app.modules.estudo.models import Conquista
        r = await self.db.execute(
            select(Conquista).where(
                Conquista.badge_id == badge_id,
                Conquista.pessoa_id == pessoa_id,
            )
        )
        return r.scalar_one_or_none()

    async def listar_por_pessoa(self, pessoa_id):
        from app.modules.estudo.models import Conquista
        r = await self.db.execute(
            select(Conquista).where(Conquista.pessoa_id == pessoa_id)
            .order_by(Conquista.created_at.desc())
        )
        return list(r.scalars().all())

    async def ranking(self, igreja_id, limit=10):
        from app.modules.estudo.models import Conquista, Badge
        from app.modules.pessoas.models import Pessoa
        from sqlalchemy import func
        r = await self.db.execute(
            select(Pessoa.nome, func.sum(Badge.pontos).label("total"))
            .join(Conquista, Conquista.pessoa_id == Pessoa.id)
            .join(Badge, Badge.id == Conquista.badge_id)
            .where(Conquista.igreja_id == igreja_id)
            .group_by(Pessoa.nome)
            .order_by(func.sum(Badge.pontos).desc())
            .limit(limit)
        )
        return [{"nome": row[0], "pontos": int(row[1] or 0)} for row in r.all()]


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
