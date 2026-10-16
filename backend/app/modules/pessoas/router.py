from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.permissions import pode_escrever_em_pessoas
from app.core.database.connection import get_db
from app.core.exceptions.handlers import PermissionDeniedError
from app.modules.pessoas.schemas import (
    Aniversariante,
    AniversariantesResumo,
    PessoaCompleta,
    PessoaCreate,
    PessoaResponse,
    PessoaUpdate,
)
from app.modules.pessoas.service import PessoaService
from app.modules.usuarios.models import Usuario

router = APIRouter(prefix="/pessoas", tags=["Pessoas"])


def _exigir_escrita(usuario: Usuario):
    if not pode_escrever_em_pessoas(usuario):
        raise PermissionDeniedError("Seu perfil nao permite criar ou alterar pessoas.")


@router.post("/", response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
async def criar_pessoa(dados: PessoaCreate, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_escrita(usuario)
    return await PessoaService(db).criar(dados.model_dump())


@router.get("/", response_model=list[PessoaResponse])
async def listar_pessoas(
    skip: int = 0, limit: int = 100, igreja_id: UUID | None = None,
    apenas_ativos: bool = False, apenas_membros: bool | None = None,
    db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    return await PessoaService(db).listar(
        skip, limit, igreja_id, apenas_ativos, apenas_membros, usuario=usuario
    )


# ATENCAO: rotas especificas (como /aniversariantes/) DEVEM vir antes de /{pessoa_id}
@router.get("/aniversariantes/", response_model=AniversariantesResumo)
async def aniversariantes(
    igreja_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    """Retorna aniversariantes de hoje, proximos 7 dias e ultimos 7 dias."""
    from app.modules.pessoas.repository import PessoaRepository

    if usuario.igreja_id and not igreja_id:
        igreja_id = usuario.igreja_id

    repo = PessoaRepository(db)
    lista = await repo.aniversariantes(igreja_id=igreja_id, janela_dias=7)

    hoje = [a for a in lista if a["dias_ate"] == 0]
    proximos = [a for a in lista if 0 < a["dias_ate"] <= 7]
    passados = [a for a in lista if -7 <= a["dias_ate"] < 0]

    def to_item(a):
        return Aniversariante(
            id=a["id"], nome=a["nome"], data_nascimento=a["data_nascimento"],
            idade=a["idade"], dias_ate=a["dias_ate"],
            telefone=a["telefone"], email=a["email"], igreja_nome=a["igreja_nome"],
        )

    return AniversariantesResumo(
        hoje=[to_item(a) for a in hoje],
        proximos_7_dias=[to_item(a) for a in proximos],
        ultimos_7_dias=[to_item(a) for a in passados],
        total_hoje=len(hoje),
        total_semana=len(proximos),
    )


@router.get("/{pessoa_id}/perfil", response_model=PessoaCompleta)
async def perfil_pessoa(
    pessoa_id: UUID,
    db: AsyncSession = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return await PessoaService(db).perfil_completo(pessoa_id, usuario)


@router.get("/{pessoa_id}", response_model=PessoaResponse)
async def buscar_pessoa(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return await PessoaService(db).buscar(pessoa_id, usuario=usuario)


@router.put("/{pessoa_id}", response_model=PessoaResponse)
async def atualizar_pessoa(
    pessoa_id: UUID, dados: PessoaUpdate,
    db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user),
):
    _exigir_escrita(usuario)
    return await PessoaService(db).atualizar(pessoa_id, dados.model_dump(exclude_unset=True), usuario=usuario)


@router.patch("/{pessoa_id}/desativar", response_model=PessoaResponse)
async def desativar_pessoa(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_escrita(usuario)
    return await PessoaService(db).desativar(pessoa_id)


@router.patch("/{pessoa_id}/reativar", response_model=PessoaResponse)
async def reativar_pessoa(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_escrita(usuario)
    return await PessoaService(db).reativar(pessoa_id)


@router.delete("/{pessoa_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_pessoa(pessoa_id: UUID, db: AsyncSession = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    _exigir_escrita(usuario)
    await PessoaService(db).deletar_com_protecao(pessoa_id)