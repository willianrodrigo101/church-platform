from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.permissions import pode_gerenciar_estudo, pode_escrever_em_cuidado
from app.core.database.connection import get_db
from app.core.exceptions.handlers import PermissionDeniedError
from app.modules.estudo.schemas import (
    AnotacaoCreate,
    AnotacaoResponse,
    AnotacaoUpdate,
    CertificadoCreate,
    CertificadoResponse,
    CertificadoValidacao,
    BadgeCreate,
    BadgeResponse,
    ChamadaRequest,
    ComentarioCreate,
    ComentarioResponse,
    ConteudoCreate,
    ConteudoResponse,
    ConquistaResponse,
    CursoCreate,
    CursoResponse,
    CursoUpdate,
    DashboardEstudo,
    DashboardGamificacao,
    DashboardTurmas,
    FerramentaCreate,
    FerramentaResponse,
    MarcarModuloConcluido,
    MatriculaCreate,
    MatriculaResponse,
    ModuloCreate,
    ModuloResponse,
    ModuloUpdate,
    PresencaCreate,
    PresencaResponse,
    QuizCreate,
    QuizResponse,
    ResponderQuiz,
    TentativaResponse,
    TrilhaCreate,
    TrilhaResponse,
    TrilhaUpdate,
    TurmaCreate,
    TurmaResponse,
    TurmaUpdate,
)
from app.modules.estudo.service import (
    FerramentaService,
    AnotacaoService,
    CertificadoService,
    BadgeService,
    ComentarioService,
    ConteudoService,
    CursoService,
    MatriculaService,
    ModuloService,
    PresencaService,
    QuizService,
    TrilhaService,
    TurmaService,
)
from app.modules.usuarios.models import Usuario


router = APIRouter(prefix="/estudo", tags=["Estudo"])


def _exigir_gerenciar(usuario: Usuario):
    """Bloqueia quem nao pode gerenciar conteudo do estudo (admin + pastor)."""
    if not pode_gerenciar_estudo(usuario):
        raise PermissionDeniedError("Seu perfil nao permite gerenciar conteudo do estudo.")


def _exigir_operacional(usuario: Usuario):
    """Bloqueia quem nao pode operar turmas (admin + pastor + lider)."""
    if not pode_escrever_em_cuidado(usuario):
        raise PermissionDeniedError("Seu perfil nao permite gerenciar turmas e matriculas.")


# ============ DASHBOARD ============

@router.get("/dashboard", response_model=DashboardEstudo)
async def dashboard(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await CursoService(db).dashboard(usuario, igreja_id)


# ============ TRILHAS ============

@router.post("/trilhas/", response_model=TrilhaResponse, status_code=status.HTTP_201_CREATED)
async def criar_trilha(dados: TrilhaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TrilhaService(db).criar(dados.model_dump(), usuario)


@router.get("/trilhas/", response_model=list[TrilhaResponse])
async def listar_trilhas(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    nivel: str | None = None,
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TrilhaService(db).listar(usuario, skip, limit, igreja_id, nivel, apenas_ativas)


@router.get("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def buscar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TrilhaService(db).buscar(trilha_id)


@router.put("/trilhas/{trilha_id}", response_model=TrilhaResponse)
async def atualizar_trilha(trilha_id: UUID, dados: TrilhaUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TrilhaService(db).atualizar(trilha_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/trilhas/{trilha_id}/desativar", response_model=TrilhaResponse)
async def desativar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TrilhaService(db).desativar(trilha_id, usuario)


@router.patch("/trilhas/{trilha_id}/reativar", response_model=TrilhaResponse)
async def reativar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TrilhaService(db).reativar(trilha_id, usuario)


@router.delete("/trilhas/{trilha_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_trilha(trilha_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    await TrilhaService(db).deletar(trilha_id, usuario)


# ============ CURSOS ============

@router.post("/cursos/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def criar_curso(dados: CursoCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await CursoService(db).criar(dados.model_dump(), usuario)


@router.get("/cursos/", response_model=list[CursoResponse])
async def listar_cursos(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    trilha_id: UUID | None = None,
    tipo: str | None = None,
    nivel: str | None = None,
    apenas_ativos: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await CursoService(db).listar(usuario, skip, limit, igreja_id, trilha_id, tipo, nivel, apenas_ativos)


@router.get("/cursos/{curso_id}", response_model=CursoResponse)
async def buscar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await CursoService(db).buscar(curso_id)


@router.put("/cursos/{curso_id}", response_model=CursoResponse)
async def atualizar_curso(curso_id: UUID, dados: CursoUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await CursoService(db).atualizar(curso_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/cursos/{curso_id}/desativar", response_model=CursoResponse)
async def desativar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await CursoService(db).desativar(curso_id, usuario)


@router.patch("/cursos/{curso_id}/reativar", response_model=CursoResponse)
async def reativar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await CursoService(db).reativar(curso_id, usuario)


@router.delete("/cursos/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_curso(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    await CursoService(db).deletar(curso_id, usuario)


# ============ MODULOS ============

@router.post("/cursos/{curso_id}/modulos/", response_model=ModuloResponse, status_code=status.HTTP_201_CREATED)
async def criar_modulo(curso_id: UUID, dados: ModuloCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await ModuloService(db).criar(curso_id, dados.model_dump(), usuario)


@router.get("/cursos/{curso_id}/modulos/", response_model=list[ModuloResponse])
async def listar_modulos(curso_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ModuloService(db).listar_por_curso(curso_id)


@router.put("/modulos/{modulo_id}", response_model=ModuloResponse)
async def atualizar_modulo(modulo_id: UUID, dados: ModuloUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await ModuloService(db).atualizar(modulo_id, dados.model_dump(exclude_unset=True), usuario)


@router.delete("/modulos/{modulo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_modulo(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    await ModuloService(db).deletar(modulo_id, usuario)


# ============ CONTEUDOS ============

@router.post("/modulos/{modulo_id}/conteudos/", response_model=ConteudoResponse, status_code=status.HTTP_201_CREATED)
async def criar_conteudo(modulo_id: UUID, dados: ConteudoCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await ConteudoService(db).criar(modulo_id, dados.model_dump(), usuario)


@router.get("/modulos/{modulo_id}/conteudos/", response_model=list[ConteudoResponse])
async def listar_conteudos(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ConteudoService(db).listar_por_modulo(modulo_id)


@router.delete("/conteudos/{conteudo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_conteudo(conteudo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    await ConteudoService(db).deletar(conteudo_id, usuario)

# ============ TURMAS ============

@router.get("/turmas/dashboard", response_model=DashboardTurmas)
async def dashboard_turmas(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TurmaService(db).dashboard(usuario, igreja_id)


@router.post("/turmas/", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
async def criar_turma(dados: TurmaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TurmaService(db).criar(dados.model_dump(), usuario)


@router.get("/turmas/", response_model=list[TurmaResponse])
async def listar_turmas(
    skip: int = 0, limit: int = 100,
    igreja_id: UUID | None = None,
    curso_id: UUID | None = None,
    status_: str | None = None,
    apenas_ativas: bool = False,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await TurmaService(db).listar(usuario, skip, limit, igreja_id, curso_id, status_, apenas_ativas)


@router.get("/turmas/{turma_id}", response_model=TurmaResponse)
async def buscar_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await TurmaService(db).buscar(turma_id)


@router.put("/turmas/{turma_id}", response_model=TurmaResponse)
async def atualizar_turma(turma_id: UUID, dados: TurmaUpdate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TurmaService(db).atualizar(turma_id, dados.model_dump(exclude_unset=True), usuario)


@router.patch("/turmas/{turma_id}/iniciar", response_model=TurmaResponse)
async def iniciar_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TurmaService(db).iniciar(turma_id, usuario)


@router.patch("/turmas/{turma_id}/concluir", response_model=TurmaResponse)
async def concluir_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await TurmaService(db).concluir(turma_id, usuario)


@router.delete("/turmas/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    await TurmaService(db).deletar(turma_id, usuario)


# ============ MATRICULAS ============

@router.post("/turmas/{turma_id}/matriculas/", response_model=MatriculaResponse, status_code=status.HTTP_201_CREATED)
async def criar_matricula(turma_id: UUID, dados: MatriculaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_operacional(usuario)
    return await MatriculaService(db).criar(turma_id, dados.model_dump(), usuario)


@router.get("/turmas/{turma_id}/matriculas/", response_model=list[MatriculaResponse])
async def listar_matriculas_turma(turma_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).listar_por_turma(turma_id)


@router.get("/pessoas/{pessoa_id}/matriculas/", response_model=list[MatriculaResponse])
async def listar_matriculas_pessoa(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).listar_por_pessoa(pessoa_id, usuario)


@router.get("/matriculas/{matricula_id}", response_model=MatriculaResponse)
async def buscar_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await MatriculaService(db).buscar(matricula_id)


@router.patch("/matriculas/{matricula_id}/modulos/{modulo_id}", response_model=MatriculaResponse)
async def marcar_modulo_concluido(
    matricula_id: UUID,
    modulo_id: UUID,
    dados: MarcarModuloConcluido,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_operacional(usuario)
    return await MatriculaService(db).marcar_modulo(matricula_id, modulo_id, dados.concluido, dados.nota, usuario)


@router.patch("/matriculas/{matricula_id}/aprovar", response_model=MatriculaResponse)
async def aprovar_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_operacional(usuario)
    return await MatriculaService(db).aprovar(matricula_id, usuario)


@router.patch("/matriculas/{matricula_id}/desistir", response_model=MatriculaResponse)
async def desistir_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_operacional(usuario)
    return await MatriculaService(db).desistir(matricula_id, usuario)


@router.delete("/matriculas/{matricula_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_matricula(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_operacional(usuario)
    await MatriculaService(db).deletar(matricula_id, usuario)


# ============ PRESENCAS ============

@router.post("/matriculas/{matricula_id}/presencas/", response_model=PresencaResponse, status_code=status.HTTP_201_CREATED)
async def criar_presenca(matricula_id: UUID, dados: PresencaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_operacional(usuario)
    return await PresencaService(db).criar(matricula_id, dados.model_dump(), usuario)


@router.get("/matriculas/{matricula_id}/presencas/", response_model=list[PresencaResponse])
async def listar_presencas(matricula_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await PresencaService(db).listar_por_matricula(matricula_id)


@router.post("/turmas/{turma_id}/chamada")
async def fazer_chamada(turma_id: UUID, dados: ChamadaRequest, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_operacional(usuario)
    return await PresencaService(db).chamada(turma_id, dados.data_aula, dados.modulo_id, dados.presencas, usuario)


@router.delete("/presencas/{presenca_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_presenca(presenca_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_operacional(usuario)
    await PresencaService(db).deletar(presenca_id, usuario)

# ============ CERTIFICADOS ============

@router.post("/matriculas/{matricula_id}/certificado", response_model=CertificadoResponse, status_code=status.HTTP_201_CREATED)
async def emitir_certificado(
    matricula_id: UUID,
    dados: CertificadoCreate | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_operacional(usuario)
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
    _exigir_operacional(usuario)
    await CertificadoService(db).cancelar(certificado_id, usuario)

# ============ QUIZZES ============

@router.post("/quizzes/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def criar_quiz(dados: QuizCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await QuizService(db).criar(dados.model_dump(), usuario)


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def buscar_quiz(quiz_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await QuizService(db).buscar(quiz_id)


@router.get("/modulos/{modulo_id}/quizzes/", response_model=list[QuizResponse])
async def listar_quizzes_modulo(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await QuizService(db).listar_por_modulo(modulo_id)


@router.post("/quizzes/{quiz_id}/responder", response_model=TentativaResponse)
async def responder_quiz(
    quiz_id: UUID,
    dados: ResponderQuiz,
    matricula_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await QuizService(db).responder(quiz_id, matricula_id, dados.respostas, usuario)


@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_quiz(quiz_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    await QuizService(db).deletar(quiz_id, usuario)


# ============ COMENTARIOS ============

@router.post("/modulos/{modulo_id}/comentarios/", response_model=ComentarioResponse, status_code=status.HTTP_201_CREATED)
async def criar_comentario(
    modulo_id: UUID,
    dados: ComentarioCreate,
    pessoa_id: UUID,
    parent_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await ComentarioService(db).criar(modulo_id, dados.texto, pessoa_id, parent_id, usuario)


@router.get("/modulos/{modulo_id}/comentarios/", response_model=list[ComentarioResponse])
async def listar_comentarios(modulo_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await ComentarioService(db).listar_por_modulo(modulo_id)


@router.delete("/comentarios/{comentario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_comentario(comentario_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    await ComentarioService(db).deletar(comentario_id, usuario)


# ============ BADGES ============

@router.post("/badges/", response_model=BadgeResponse, status_code=status.HTTP_201_CREATED)
async def criar_badge(dados: BadgeCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_gerenciar(usuario)
    return await BadgeService(db).criar(dados.model_dump(), usuario)


@router.get("/badges/", response_model=list[BadgeResponse])
async def listar_badges(db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await BadgeService(db).listar(usuario)


@router.post("/badges/{badge_id}/conceder", response_model=ConquistaResponse, status_code=status.HTTP_201_CREATED)
async def conceder_badge(
    badge_id: UUID,
    pessoa_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    _exigir_gerenciar(usuario)
    return await BadgeService(db).conceder(badge_id, pessoa_id, usuario)


@router.get("/pessoas/{pessoa_id}/conquistas/", response_model=list[ConquistaResponse])
async def listar_conquistas(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await BadgeService(db).listar_conquistas_pessoa(pessoa_id)


@router.get("/gamificacao/dashboard", response_model=DashboardGamificacao)
async def dashboard_gamificacao(db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await BadgeService(db).dashboard(usuario)


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
    _exigir_gerenciar(usuario)
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
    _exigir_gerenciar(usuario)
    await FerramentaService(db).deletar(ferramenta_id, usuario)