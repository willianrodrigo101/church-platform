from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class ResumoIgrejas(BaseModel):
    total: int
    ativas: int


class ResumoPessoas(BaseModel):
    total: int
    ativas: int
    membros: int
    visitantes: int
    sem_interacao_30d: int


class ResumoCuidado(BaseModel):
    total: int
    pendentes: int
    vencidos: int
    concluidos: int
    retornos_7d: int


class ResumoOracao(BaseModel):
    total: int
    abertos: int
    em_oracao: int
    atendidos: int
    sem_resposta_30d: int


class AtividadeRecente(BaseModel):
    id: UUID
    tipo: str  # "acompanhamento" | "oracao"
    titulo: str
    subtitulo: str | None = None
    data: date
    status: str
    sigiloso: bool = False


class DashboardGeral(BaseModel):
    igrejas: ResumoIgrejas
    pessoas: ResumoPessoas
    cuidado: ResumoCuidado
    oracao: ResumoOracao
    atividades_recentes: list[AtividadeRecente]
