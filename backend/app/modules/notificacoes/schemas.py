from datetime import date
from uuid import UUID

from pydantic import BaseModel


class NotificacaoItem(BaseModel):
    id: UUID
    tipo: str          # "acompanhamento_vencido" | "retorno_proximo" | "pedido_sem_resposta" | "pessoa_sem_interacao"
    titulo: str
    subtitulo: str | None = None
    data: date | None = None
    dias: int = 0      # dias vencido / dias sem interacao / dias aberto
    sigiloso: bool = False
    aba_destino: str   # "cuidado" | "oracao" | "pessoas"


class NotificacoesResumo(BaseModel):
    total: int
    por_tipo: dict[str, int]
    itens: list[NotificacaoItem]
