from sqlalchemy import select
from uuid import UUID
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
    PermissionDeniedError,
)
from app.modules.estudo.repository import (
    BadgeRepository,
    AnotacaoRepository,
    CertificadoRepository,
    FerramentaRepository,
    ComentarioRepository,
    ConquistaRepository,
    ConteudoRepository,
    CursoRepository,
    MatriculaRepository,
    ModuloRepository,
    PresencaRepository,
    ProgressoModuloRepository,
    QuizRepository,
    TentativaRepository,
    TrilhaRepository,
    TurmaRepository,
)
from app.modules.igreja.repository import IgrejaRepository
from app.modules.pessoas.repository import PessoaRepository
from app.modules.usuarios.models import Usuario

# Raiz do backend (para salvar PDFs de certificado)
BACKEND = Path(__file__).resolve().parents[3]


class TrilhaService:
    def __init__(self, db: AsyncSession):
        self.repo = TrilhaRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    async def _resolver_igreja(self, autor: Usuario, igreja_id: UUID | None) -> UUID:
        if autor.role == "admin":
            if igreja_id:
                return igreja_id
            if autor.igreja_id:
                return autor.igreja_id
            igrejas = await self.igreja_repo.listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            return igrejas[0].id
        if not autor.igreja_id:
            raise BusinessRuleError("Usuario sem igreja vinculada.")
        return autor.igreja_id

    async def criar(self, dados: dict, autor: Usuario):
        dados["igreja_id"] = await self._resolver_igreja(autor, dados.pop("igreja_id", None))
        return await self.repo.criar(dados)

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Trilha de formacao", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, nivel=None, apenas_ativas=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(skip, limit, igreja_id, nivel, apenas_ativas)

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.buscar(obj_id)
        return await self.repo.atualizar(obj, dados)

    async def desativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if not obj.ativa:
            raise BusinessRuleError("Trilha ja esta desativada")
        return await self.repo.atualizar(obj, {"ativa": False})

    async def reativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.ativa:
            raise BusinessRuleError("Trilha ja esta ativa")
        return await self.repo.atualizar(obj, {"ativa": True})

    async def deletar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.cursos:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {len(obj.cursos)} curso(s) vinculado(s). "
                "Desative a trilha em vez de exclui-la."
            )
        await self.repo.deletar(obj)


class CursoService:
    def __init__(self, db: AsyncSession):
        self.repo = CursoRepository(db)
        self.mod_repo = ModuloRepository(db)
        self.trilha_repo = TrilhaRepository(db)
        self.igreja_repo = IgrejaRepository(db)
        self.db = db

    async def _resolver_igreja(self, autor: Usuario, igreja_id: UUID | None) -> UUID:
        if autor.role == "admin":
            if igreja_id:
                return igreja_id
            if autor.igreja_id:
                return autor.igreja_id
            igrejas = await self.igreja_repo.listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            return igrejas[0].id
        if not autor.igreja_id:
            raise BusinessRuleError("Usuario sem igreja vinculada.")
        return autor.igreja_id

    async def criar(self, dados: dict, autor: Usuario):
        modulos = dados.pop("modulos", []) or []
        trilha_id = dados.pop("trilha_id", None)

        if trilha_id:
            trilha = await self.trilha_repo.buscar_por_id(trilha_id)
            if not trilha:
                raise BusinessRuleError("Trilha informada nao existe")

        igreja_id = await self._resolver_igreja(autor, None)
        dados["igreja_id"] = igreja_id
        dados["trilha_id"] = trilha_id

        for i, m in enumerate(modulos, start=1):
            m["ordem"] = m.get("ordem") or i

        curso = await self.repo.criar(dados, modulos)
        recarregado = await self.repo.buscar_por_id(curso.id)
        return recarregado or curso

    async def buscar(self, obj_id: UUID):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Curso", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, trilha_id=None, tipo=None, nivel=None, apenas_ativos=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        return await self.repo.listar(skip, limit, igreja_id, trilha_id, tipo, nivel, apenas_ativos)

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.buscar(obj_id)
        return await self.repo.atualizar(obj, dados)

    async def desativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if not obj.ativo:
            raise BusinessRuleError("Curso ja esta desativado")
        return await self.repo.atualizar(obj, {"ativo": False})

    async def reativar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.ativo:
            raise BusinessRuleError("Curso ja esta ativo")
        return await self.repo.atualizar(obj, {"ativo": True})

    async def deletar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        await self.repo.deletar(obj)

    async def dashboard(self, usuario, igreja_id=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id

        trilhas = await self.trilha_repo.listar(igreja_id=igreja_id, limit=1000)
        cursos = await self.repo.listar(igreja_id=igreja_id, limit=10000)

        total_modulos = sum(len(c.modulos) for c in cursos)
        total_conteudos = sum(len(m.conteudos) for c in cursos for m in c.modulos)

        return {
            "total_trilhas": len(trilhas),
            "total_cursos": len(cursos),
            "total_modulos": total_modulos,
            "total_conteudos": total_conteudos,
            "cursos_por_tipo": await self.repo.contar_por_tipo(igreja_id),
            "cursos_por_nivel": await self.repo.contar_por_nivel(igreja_id),
        }


class ModuloService:
    def __init__(self, db: AsyncSession):
        self.repo = ModuloRepository(db)
        self.curso_repo = CursoRepository(db)
        self.db = db

    async def criar(self, curso_id: UUID, dados: dict, autor: Usuario):
        curso = await self.curso_repo.buscar_por_id(curso_id)
        if not curso:
            raise NotFoundError("Curso", str(curso_id))
        conteudos = dados.pop("conteudos", []) or []
        dados["curso_id"] = curso_id
        mod = await self.repo.criar(dados, conteudos)
        recarregado = await self.repo.buscar_por_id(mod.id)
        return recarregado or mod

    async def listar_por_curso(self, curso_id: UUID):
        return await self.repo.listar_por_curso(curso_id)

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Modulo", str(obj_id))
        return await self.repo.atualizar(obj, dados)

    async def deletar(self, obj_id, usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Modulo", str(obj_id))
        await self.repo.deletar(obj)


class ConteudoService:
    def __init__(self, db: AsyncSession):
        self.repo = ConteudoRepository(db)
        self.mod_repo = ModuloRepository(db)
        self.db = db

    async def criar(self, modulo_id: UUID, dados: dict, autor: Usuario):
        mod = await self.mod_repo.buscar_por_id(modulo_id)
        if not mod:
            raise NotFoundError("Modulo", str(modulo_id))
        dados["modulo_id"] = modulo_id
        return await self.repo.criar(dados)

    async def listar_por_modulo(self, modulo_id: UUID):
        return await self.repo.listar_por_modulo(modulo_id)

    async def deletar(self, obj_id, usuario):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Conteudo", str(obj_id))
        await self.repo.deletar(obj)


class TurmaService:
    def __init__(self, db):
        self.db = db
        self.repo = TurmaRepository(db)
        self.curso_repo = CursoRepository(db)
        self.igreja_repo = IgrejaRepository(db)

    async def _resolver_igreja(self, autor, igreja_id=None):
        if autor.role == "admin":
            if igreja_id: return igreja_id
            if autor.igreja_id: return autor.igreja_id
            igrejas = await self.igreja_repo.listar(apenas_ativas=True)
            if not igrejas:
                raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
            return igrejas[0].id
        if not autor.igreja_id:
            raise BusinessRuleError("Usuario sem igreja vinculada.")
        return autor.igreja_id

    async def criar(self, dados, autor):
        curso_id = dados.get("curso_id")
        curso = await self.curso_repo.buscar_por_id(curso_id)
        if not curso:
            raise BusinessRuleError("Curso informado nao existe")
        dados["igreja_id"] = await self._resolver_igreja(autor, dados.pop("igreja_id", None))
        return await self.repo.criar(dados)

    async def buscar(self, obj_id):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Turma", str(obj_id))
        return obj

    async def listar(self, usuario, skip=0, limit=100, igreja_id=None, curso_id=None, status=None, apenas_ativas=False):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        turmas = await self.repo.listar(skip, limit, igreja_id, curso_id, status, apenas_ativas)
        for t in turmas:
            t.total_matriculas = await self.repo.contar_matriculas(t.id)
        return turmas

    async def atualizar(self, obj_id, dados, usuario):
        obj = await self.buscar(obj_id)
        return await self.repo.atualizar(obj, dados)

    async def iniciar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.status == "em_andamento":
            raise BusinessRuleError("Turma ja esta em andamento")
        return await self.repo.atualizar(obj, {"status": "em_andamento"})

    async def concluir(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.status == "concluida":
            raise BusinessRuleError("Turma ja esta concluida")
        return await self.repo.atualizar(obj, {"status": "concluida"})

    async def deletar(self, obj_id, usuario):
        obj = await self.buscar(obj_id)
        if obj.matriculas:
            raise BusinessRuleError(
                f"Nao e possivel excluir: {len(obj.matriculas)} matricula(s) vinculada(s)."
            )
        await self.repo.deletar(obj)

    async def dashboard(self, usuario, igreja_id=None):
        if usuario.igreja_id and not igreja_id:
            igreja_id = usuario.igreja_id
        turmas = await self.repo.listar(igreja_id=igreja_id, limit=10000)
        ativas = [t for t in turmas if t.ativa]
        total_matriculas = sum(await self.repo.contar_matriculas(t.id) for t in turmas)

        return {
            "total_turmas": len(turmas),
            "turmas_ativas": len(ativas),
            "total_matriculas": total_matriculas,
            "media_progresso": 0.0,
            "taxa_presenca": 0.0,
        }


class MatriculaService:
    def __init__(self, db):
        self.db = db
        self.repo = MatriculaRepository(db)
        self.turma_repo = TurmaRepository(db)
        self.pessoa_repo = PessoaRepository(db)
        self.prog_repo = ProgressoModuloRepository(db)
        self.mod_repo = ModuloRepository(db)
        self.curso_repo = CursoRepository(db)

    async def criar(self, turma_id, dados, autor):
        turma = await self.turma_repo.buscar_por_id(turma_id)
        if not turma:
            raise NotFoundError("Turma", str(turma_id))
        if turma.status == "concluida":
            raise BusinessRuleError("Turma ja concluida. Nao aceita novas matriculas.")

        pessoa = await self.pessoa_repo.buscar_por_id(dados["pessoa_id"])
        if not pessoa:
            raise BusinessRuleError("Pessoa nao existe")
        if not pessoa.ativo:
            raise BusinessRuleError("Pessoa inativa")

        if turma.vagas is not None:
            total = await self.turma_repo.contar_matriculas(turma_id)
            if total >= turma.vagas:
                raise BusinessRuleError("Turma lotada")

        existente = await self.repo.buscar_por_turma_e_pessoa(turma_id, dados["pessoa_id"])
        if existente:
            raise BusinessRuleError("Pessoa ja esta matriculada nesta turma")

        from datetime import date as date_cls
        dados_mat = {
            "turma_id": turma_id,
            "pessoa_id": dados["pessoa_id"],
            "igreja_id": turma.igreja_id,
            "data_matricula": date_cls.today(),
            "observacoes": dados.get("observacoes"),
            "status": "matriculado",
        }
        mat = await self.repo.criar(dados_mat)

        curso = await self.curso_repo.buscar_por_id(turma.curso_id)
        if curso:
            modulos = await self.mod_repo.listar_por_curso(curso.id)
            for m in modulos:
                await self.prog_repo.criar({
                    "matricula_id": mat.id,
                    "modulo_id": m.id,
                    "concluido": False,
                    "tentativas": 0,
                })
        return await self.buscar(mat.id)

    async def buscar(self, obj_id):
        obj = await self.repo.buscar_por_id(obj_id)
        if not obj:
            raise NotFoundError("Matricula", str(obj_id))
        return obj

    async def listar_por_turma(self, turma_id):
        return await self.repo.listar_por_turma(turma_id)

    async def listar_por_pessoa(self, pessoa_id, usuario):
        igreja_id = usuario.igreja_id
        return await self.repo.listar_por_pessoa(pessoa_id, igreja_id)

    async def marcar_modulo(self, matricula_id, modulo_id, concluido, nota, usuario):
        mat = await self.buscar(matricula_id)
        if mat.status not in ("matriculado", "em_andamento"):
            raise BusinessRuleError("Matricula nao esta ativa")

        prog = await self.prog_repo.buscar_por_matricula_e_modulo(matricula_id, modulo_id)
        if not prog:
            raise NotFoundError("Progresso do modulo", str(modulo_id))

        from datetime import date as date_cls
        dados = {
            "concluido": concluido,
            "data_conclusao": date_cls.today() if concluido else None,
        }
        if nota is not None:
            dados["nota"] = nota
        dados["tentativas"] = (prog.tentativas or 0) + 1

        await self.prog_repo.atualizar(prog, dados)

        todos = await self.prog_repo.listar_por_matricula(matricula_id)
        if todos:
            concluidos = sum(1 for p in todos if p.concluido)
            pct = round((concluidos / len(todos)) * 100, 1)
            await self.repo.atualizar(mat, {"progresso_percentual": pct})

        return await self.buscar(matricula_id)

    async def aprovar(self, matricula_id, usuario):
        mat = await self.buscar(matricula_id)
        from datetime import date as date_cls
        return await self.repo.atualizar(mat, {
            "status": "aprovado",
            "data_conclusao": date_cls.today(),
        })

    async def desistir(self, matricula_id, usuario):
        mat = await self.buscar(matricula_id)
        return await self.repo.atualizar(mat, {"status": "desistente"})

    async def deletar(self, matricula_id, usuario):
        mat = await self.buscar(matricula_id)
        await self.repo.deletar(mat)


class PresencaService:
    def __init__(self, db):
        self.db = db
        self.repo = PresencaRepository(db)
        self.mat_repo = MatriculaRepository(db)
        self.turma_repo = TurmaRepository(db)

    async def buscar(self, obj_id):
        from app.modules.estudo.models import Presenca
        r = await self.db.execute(select(Presenca).where(Presenca.id == obj_id))
        return r.scalar_one_or_none()

    async def criar(self, matricula_id, dados, usuario):
        mat = await self.mat_repo.buscar_por_id(matricula_id)
        if not mat:
            raise NotFoundError("Matricula", str(matricula_id))

        existente = await self.repo.buscar(matricula_id, dados.get("modulo_id"), dados["data_aula"])
        if existente:
            for k, v in dados.items():
                setattr(existente, k, v)
            await self.db.flush()
            await self.db.refresh(existente)
            return existente

        dados["matricula_id"] = matricula_id
        return await self.repo.criar(dados)

    async def chamada(self, turma_id, data_aula, modulo_id, presencas, usuario):
        turma = await self.turma_repo.buscar_por_id(turma_id)
        if not turma:
            raise NotFoundError("Turma", str(turma_id))

        resultados = []
        for item in presencas:
            mat_id = item.get("matricula_id")
            presente = item.get("presente", False)
            if not mat_id:
                continue
            r = await self.criar(mat_id, {
                "data_aula": data_aula,
                "modulo_id": modulo_id,
                "presente": presente,
            }, usuario)
            resultados.append(r)
        return resultados

    async def listar_por_matricula(self, matricula_id):
        return await self.repo.listar_por_matricula(matricula_id)

    async def deletar(self, obj_id, usuario):
        from app.modules.estudo.models import Presenca
        r = await self.db.execute(select(Presenca).where(Presenca.id == obj_id))
        obj = r.scalar_one_or_none()
        if not obj:
            raise NotFoundError("Presenca", str(obj_id))
        await self.db.delete(obj)
        await self.db.flush()


class CertificadoService:
    def __init__(self, db):
        self.db = db
        self.repo = CertificadoRepository(db)

    def _gerar_codigo(self):
        import secrets
        return "CERT-" + secrets.token_hex(6).upper()

    async def _carregar_matricula(self, matricula_id):
        repo = MatriculaRepository(self.db)
        m = await repo.buscar_por_id(matricula_id)
        if not m:
            raise NotFoundError("Matricula", str(matricula_id))
        return m

    async def emitir(self, matricula_id, autor, carga_horaria=None):
        from app.modules.estudo.models import Curso
        mat = await self._carregar_matricula(matricula_id)
        if getattr(mat, "status", None) != "aprovado":
            raise BusinessRuleError("Matricula ainda nao foi aprovada")

        existente = await self.repo.buscar_por_matricula(matricula_id)
        if existente and not existente.cancelado:
            return existente

        turma = getattr(mat, "turma", None)
        curso = None
        curso_id = None
        if turma:
            curso_id = getattr(turma, "curso_id", None)
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
        url = await self._gerar_pdf(cert)
        cert = await self.repo.atualizar(cert, {"url_pdf": url})
        return cert

    async def _gerar_pdf(self, cert):
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
        except ImportError:
            raise BusinessRuleError("reportlab nao instalado. Rode: pip install reportlab")

        from app.modules.estudo.models import Pessoa, Curso
        from app.modules.igreja.models import Igreja
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
        emitido = getattr(cert, "emitido_em", None) or getattr(cert, "created_at", None)
        if emitido:
            c.drawCentredString(w/2, h - 15.8*cm, f"Emitido em: {emitido.strftime('%d/%m/%Y')}")

        c.setFont("Helvetica", 11)
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
        from app.modules.estudo.models import Pessoa, Curso
        from app.modules.igreja.models import Igreja
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
            "emitido_em": getattr(c, "emitido_em", None) or getattr(c, "created_at", None),
            "mensagem": "Certificado autentico",
        }

    async def cancelar(self, obj_id, autor):
        c = await self.buscar(obj_id)
        await self.repo.atualizar(c, {"cancelado": True})


class QuizService:
    def __init__(self, db):
        self.db = db
        self.repo = QuizRepository(db)
        self.tent_repo = TentativaRepository(db)
        self.mod_repo = ModuloRepository(db)

    async def criar(self, dados, autor):
        modulo_id = dados.get("modulo_id")
        mod = await self.mod_repo.buscar_por_id(modulo_id)
        if not mod:
            raise NotFoundError("Modulo", str(modulo_id))
        perguntas = dados.pop("perguntas", []) or []
        for i, p in enumerate(perguntas):
            if p.get("resposta_correta", 0) >= len(p.get("opcoes", [])):
                raise BusinessRuleError(f"Pergunta {i+1}: indice da resposta invalido")
        q = await self.repo.criar(dados, perguntas)
        return await self.repo.buscar_por_id(q.id)

    async def buscar(self, obj_id):
        q = await self.repo.buscar_por_id(obj_id)
        if not q:
            raise NotFoundError("Quiz", str(obj_id))
        return q

    async def listar_por_modulo(self, modulo_id):
        return await self.repo.listar_por_modulo(modulo_id)

    async def responder(self, quiz_id, matricula_id, respostas, usuario):
        import json
        quiz = await self.buscar(quiz_id)
        if not quiz.ativo:
            raise BusinessRuleError("Quiz desativado")

        tentativas = await self.tent_repo.contar_por_quiz_e_matricula(quiz_id, matricula_id)
        if quiz.tentativas_max is not None and tentativas >= quiz.tentativas_max:
            raise BusinessRuleError(f"Limite de {quiz.tentativas_max} tentativas atingido")

        acertos = 0
        total = len(quiz.perguntas)
        for p in quiz.perguntas:
            resp = respostas.get(str(p.id))
            if resp is not None and int(resp) == p.resposta_correta:
                acertos += 1

        nota = round((acertos / total) * 10, 1) if total > 0 else 0.0
        aprovado = nota >= quiz.nota_minima

        t = await self.tent_repo.criar({
            "quiz_id": quiz_id,
            "matricula_id": matricula_id,
            "nota": nota,
            "acertos": acertos,
            "total": total,
            "aprovado": aprovado,
            "respostas": json.dumps(respostas),
        })

        prog_repo = ProgressoModuloRepository(self.db)
        prog = await prog_repo.buscar_por_matricula_e_modulo(matricula_id, quiz.modulo_id)
        if prog:
            await prog_repo.atualizar(prog, {
                "concluido": aprovado,
                "nota": nota,
                "tentativas": (prog.tentativas or 0) + 1,
            })

        return t

    async def deletar(self, obj_id, usuario):
        q = await self.buscar(obj_id)
        await self.repo.deletar(q)


class ComentarioService:
    def __init__(self, db):
        self.db = db
        self.repo = ComentarioRepository(db)

    async def criar(self, modulo_id, texto, pessoa_id, parent_id=None, autor=None):
        return await self.repo.criar({
            "modulo_id": modulo_id,
            "pessoa_id": pessoa_id,
            "texto": texto,
            "parent_id": parent_id,
        })

    async def listar_por_modulo(self, modulo_id):
        return await self.repo.listar_por_modulo(modulo_id)

    async def deletar(self, obj_id, usuario):
        from app.modules.estudo.models import Comentario
        r = await self.db.execute(select(Comentario).where(Comentario.id == obj_id))
        c = r.scalar_one_or_none()
        if not c:
            raise NotFoundError("Comentario", str(obj_id))
        await self.repo.deletar(c)


class BadgeService:
    def __init__(self, db):
        self.db = db
        self.repo = BadgeRepository(db)
        self.conq_repo = ConquistaRepository(db)
        self.igreja_repo = IgrejaRepository(db)

    async def _resolver_igreja(self, autor):
        if autor.igreja_id:
            return autor.igreja_id
        igrejas = await self.igreja_repo.listar(apenas_ativas=True)
        if not igrejas:
            raise BusinessRuleError("Nenhuma igreja ativa cadastrada.")
        return igrejas[0].id

    async def criar(self, dados, autor):
        igreja_id = await self._resolver_igreja(autor)
        existente = await self.repo.buscar_por_codigo(igreja_id, dados["codigo"])
        if existente:
            raise BusinessRuleError(f"Ja existe badge com codigo '{dados['codigo']}'")
        dados["igreja_id"] = igreja_id
        return await self.repo.criar(dados)

    async def listar(self, autor):
        igreja_id = await self._resolver_igreja(autor)
        return await self.repo.listar(igreja_id)

    async def conceder(self, badge_id, pessoa_id, autor):
        badge = await self.repo.buscar_por_id(badge_id)
        if not badge:
            raise NotFoundError("Badge", str(badge_id))
        existente = await self.conq_repo.buscar(badge_id, pessoa_id)
        if existente:
            raise BusinessRuleError("Pessoa ja possui este badge")
        return await self.conq_repo.criar({
            "badge_id": badge_id,
            "pessoa_id": pessoa_id,
            "igreja_id": badge.igreja_id,
        })

    async def listar_conquistas_pessoa(self, pessoa_id):
        return await self.conq_repo.listar_por_pessoa(pessoa_id)

    async def ranking(self, autor, limit=10):
        igreja_id = await self._resolver_igreja(autor)
        return await self.conq_repo.ranking(igreja_id, limit)

    async def dashboard(self, autor):
        igreja_id = await self._resolver_igreja(autor)
        badges = await self.repo.listar(igreja_id)
        ranking = await self.conq_repo.ranking(igreja_id)
        return {
            "total_badges": len(badges),
            "total_conquistas": sum(1 for _ in ranking),
            "ranking": ranking,
        }


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
