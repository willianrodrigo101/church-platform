from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ConteudoCreate(BaseModel):
    ordem: int = Field(1, ge=1)
    titulo: str = Field(..., min_length=2, max_length=200)
    tipo: str = Field("texto", pattern="^(video|pdf|audio|texto|link|imagem|slides)$")
    url: str | None = None
    texto: str | None = None
    duracao_minutos: int | None = None


class ConteudoResponse(ConteudoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ativo: bool
    created_at: datetime


class ModuloCreate(BaseModel):
    ordem: int = Field(1, ge=1)
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    duracao_minutos: int | None = None
    obrigatorio: bool = True
    conteudos: list[ConteudoCreate] = []


class ModuloUpdate(BaseModel):
    ordem: int | None = None
    titulo: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    duracao_minutos: int | None = None
    obrigatorio: bool | None = None


class ModuloResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    curso_id: UUID
    ordem: int
    titulo: str
    descricao: str | None = None
    duracao_minutos: int | None = None
    obrigatorio: bool
    ativo: bool
    created_at: datetime
    conteudos: list[ConteudoResponse] = []


class CursoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str = Field("teologia", pattern="^(teologia|biblico|sistematico|historico|pratico|linguas|artes|ministerial|outro)$")
    nivel: str = Field("iniciante", pattern="^(iniciante|basico|intermediario|avancado|bacharelado)$")
    carga_horaria: int | None = None
    imagem_capa: str | None = None
    obrigatorio: bool = False
    ordem: int = 1


class CursoCreate(CursoBase):
    trilha_id: UUID | None = None
    modulos: list[ModuloCreate] = []


class CursoUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=200)
    descricao: str | None = None
    tipo: str | None = None
    nivel: str | None = None
    carga_horaria: int | None = None
    imagem_capa: str | None = None
    obrigatorio: bool | None = None
    ordem: int | None = None
    trilha_id: UUID | None = None


class CursoResponse(CursoBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    trilha_id: UUID | None = None
    ativo: bool
    created_at: datetime
    updated_at: datetime
    modulos: list[ModuloResponse] = []


class TrilhaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    nivel: str = Field("iniciante", pattern="^(iniciante|basico|intermediario|avancado|bacharelado)$")
    icone: str | None = None
    cor: str | None = None
    ordem: int = 1


class TrilhaCreate(TrilhaBase):
    igreja_id: UUID | None = None


class TrilhaUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    nivel: str | None = None
    icone: str | None = None
    cor: str | None = None
    ordem: int | None = None


class TrilhaResponse(TrilhaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    igreja_id: UUID
    ativa: bool
    created_at: datetime
    updated_at: datetime
    cursos: list[CursoResponse] = []


class DashboardEstudo(BaseModel):
    total_trilhas: int
    total_cursos: int
    total_modulos: int
    total_conteudos: int
    cursos_por_tipo: dict[str, int]
    cursos_por_nivel: dict[str, int]

# ============ TURMAS ============

class TurmaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    horario: str | None = None
    local: str | None = None
    vagas: int | None = None
    modalidade: str = Field("presencial", pattern="^(presencial|online|hibrido)$")


class TurmaCreate(TurmaBase):
    curso_id: UUID
    professor_id: UUID | None = None
    igreja_id: UUID | None = None


class TurmaUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    horario: str | None = None
    local: str | None = None
    vagas: int | None = None
    modalidade: str | None = None
    professor_id: UUID | None = None
    status: str | None = None


class PessoaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class UsuarioResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class CursoResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    nivel: str


class TurmaResponse(TurmaBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    curso_id: UUID
    igreja_id: UUID
    professor_id: UUID | None = None
    status: str
    ativa: bool
    created_at: datetime
    updated_at: datetime
    curso: CursoResumo | None = None
    professor: UsuarioResumo | None = None
    total_matriculas: int = 0


# ============ MATRICULAS ============

class MatriculaCreate(BaseModel):
    pessoa_id: UUID
    observacoes: str | None = None


class MatriculaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    turma_id: UUID
    pessoa_id: UUID
    igreja_id: UUID
    status: str
    nota_final: float | None = None
    progresso_percentual: float
    data_matricula: date
    data_conclusao: date | None = None
    observacoes: str | None = None
    created_at: datetime
    pessoa: PessoaResumo | None = None


# ============ PROGRESSO ============

class ProgressoModuloResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    matricula_id: UUID
    modulo_id: UUID
    concluido: bool
    nota: float | None = None
    tentativas: int
    data_conclusao: date | None = None


class MarcarModuloConcluido(BaseModel):
    concluido: bool = True
    nota: float | None = None


# ============ PRESENCA ============

class PresencaCreate(BaseModel):
    data_aula: date
    modulo_id: UUID | None = None
    presente: bool = True
    observacao: str | None = None


class PresencaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    matricula_id: UUID
    modulo_id: UUID | None = None
    data_aula: date
    presente: bool
    observacao: str | None = None


class ChamadaItem(BaseModel):
    matricula_id: UUID
    pessoa_id: UUID
    nome: str
    presente: bool


class ChamadaRequest(BaseModel):
    data_aula: date
    modulo_id: UUID | None = None
    presencas: list[dict]


# ============ DASHBOARD ============

class DashboardTurmas(BaseModel):
    total_turmas: int
    turmas_ativas: int
    total_matriculas: int
    media_progresso: float
    taxa_presenca: float

# ============ QUIZ ============

class PerguntaCreate(BaseModel):
    ordem: int = Field(1, ge=1)
    enunciado: str = Field(..., min_length=2)
    opcoes: list[str] = Field(..., min_length=2)
    resposta_correta: int = Field(..., ge=0)
    pontuacao: float = 1.0


class PerguntaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    ordem: int
    enunciado: str
    opcoes: str
    resposta_correta: int
    pontuacao: float


class QuizCreate(BaseModel):
    modulo_id: UUID
    titulo: str = Field(..., min_length=2, max_length=200)
    descricao: str | None = None
    nota_minima: float = 7.0
    tentativas_max: int | None = None
    perguntas: list[PerguntaCreate] = []


class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    modulo_id: UUID
    titulo: str
    descricao: str | None = None
    nota_minima: float
    tentativas_max: int | None = None
    ativo: bool
    created_at: datetime
    perguntas: list[PerguntaResponse] = []


class ResponderQuiz(BaseModel):
    respostas: dict[str, int]  # pergunta_id -> indice escolhido


class TentativaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    quiz_id: UUID
    matricula_id: UUID
    nota: float
    acertos: int
    total: int
    aprovado: bool
    created_at: datetime


# ============ COMENTARIO ============

class ComentarioCreate(BaseModel):
    texto: str = Field(..., min_length=1)


class ComentarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    modulo_id: UUID
    pessoa_id: UUID
    parent_id: UUID | None = None
    texto: str
    fixado: bool
    created_at: datetime
    pessoa: PessoaResumo | None = None


# ============ BADGE ============

class BadgeCreate(BaseModel):
    codigo: str = Field(..., min_length=2, max_length=50)
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: str | None = None
    icone: str = "🏅"
    cor: str | None = None
    pontos: int = 10


class BadgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    codigo: str
    nome: str
    descricao: str | None = None
    icone: str
    cor: str | None = None
    pontos: int


class ConquistaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    badge_id: UUID
    pessoa_id: UUID
    badge: BadgeResponse | None = None
    created_at: datetime


class DashboardGamificacao(BaseModel):
    total_badges: int
    total_conquistas: int
    ranking: list[dict]

# ============ CERTIFICADO ============

class CertificadoCreate(BaseModel):
    matricula_id: UUID
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
