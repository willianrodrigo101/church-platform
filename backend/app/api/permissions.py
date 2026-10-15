# -*- coding: utf-8 -*-
"""
Permissoes centrais do Church Platform.

Este arquivo e a UNICA fonte de verdade sobre quem pode ver o que.
Todos os modulos devem importar daqui.

Regras (matriz de visibilidade):
    🔴 admin   -> ve tudo (todas as igrejas)
    🟣 pastor  -> ve a propria igreja
    🔵 lider   -> ve o proprio ministerio (aplicado quando ministerios existirem)
    🟢 membro  -> ve apenas os proprios dados

IMPORTANTE:
    - Este arquivo NAO acessa o banco. Ele apenas monta filtros SQLAlchemy.
    - Os filtros devem ser encadeados na query:
          query = select(Pessoa)
          query = filtrar_por_igreja(query, Pessoa, user)
          query = filtrar_pessoas_por_role(query, Pessoa, user)
    - Se o filtro nao se aplica, ele retorna a query inalterada.
"""
from typing import Any, Optional

from sqlalchemy import or_, select
from sqlalchemy.sql import Select

from app.modules.usuarios.models import Usuario


# ------------------------------------------------------------------
# Helpers de identificacao de role
# ------------------------------------------------------------------

def is_admin(user: Usuario) -> bool:
    """Retorna True se o usuario for admin global."""
    return getattr(user, "role", None) == "admin"


def is_pastor(user: Usuario) -> bool:
    """Retorna True se o usuario for pastor."""
    return getattr(user, "role", None) == "pastor"


def is_lider(user: Usuario) -> bool:
    """Retorna True se o usuario for lider."""
    return getattr(user, "role", None) == "lider"


def is_membro(user: Usuario) -> bool:
    """Retorna True se o usuario for membro comum."""
    return getattr(user, "role", None) == "membro"


# ------------------------------------------------------------------
# Capacidades (o que o role pode fazer)
# ------------------------------------------------------------------

def pode_ver_tudo(user: Usuario) -> bool:
    """admin e pastor veem a igreja inteira (admin ve tudo)."""
    return is_admin(user) or is_pastor(user)


def pode_ver_igreja(user: Usuario) -> bool:
    """admin, pastor e lider veem a igreja (lider so quando houver ministerio)."""
    return is_admin(user) or is_pastor(user) or is_lider(user)


def pode_gerenciar_usuarios(user: Usuario) -> bool:
    """Somente admin gerencia usuarios do sistema."""
    return is_admin(user)


def pode_gerenciar_igrejas(user: Usuario) -> bool:
    """Somente admin cria/edita igrejas."""
    return is_admin(user)


def respeita_sigilo(user: Usuario) -> bool:
    """
    Se True, o sigilo pastoral DEVE ser aplicado nas consultas
    (usuario nao ve conteudo sigiloso que nao seja dele).

    Admin: NAO respeita sigilo (ve tudo, inclusive sigiloso).
    Pastor/Lider/Membro: respeitam sigilo.
    """
    return not is_admin(user)


# ------------------------------------------------------------------
# Filtros reutilizaveis (SQLAlchemy)
# ------------------------------------------------------------------

def filtrar_por_igreja(query: Select, model: Any, user: Usuario) -> Select:
    """
    Aplica filtro de igreja na query.

    - admin: sem filtro (ve todas as igrejas)
    - outros: filtra por user.igreja_id
    - se o model nao tem igreja_id ou o user nao tem igreja, retorna sem mexer
    """
    if is_admin(user):
        return query

    if not hasattr(model, "igreja_id"):
        return query

    igreja_id = getattr(user, "igreja_id", None)
    if igreja_id is None:
        return query

    return query.where(model.igreja_id == igreja_id)


def filtrar_pessoas_por_role(query: Select, model: Any, user: Usuario) -> Select:
    """
    Aplica filtro de visibilidade de pessoas.

    - admin/pastor: veem todas as pessoas da igreja
    - lider: por enquanto veem todas (ministerio vem na Etapa 4)
    - membro: ve APENAS a si proprio

    Requer que o model Pessoa tenha id e o Usuario tenha pessoa_id.
    """
    if pode_ver_igreja(user):
        return query

    if is_membro(user):
        pessoa_id = getattr(user, "pessoa_id", None)
        if pessoa_id is None:
            # Membro sem pessoa vinculada: nao ve ninguem
            return query.where(model.id == None)  # noqa: E711
        return query.where(model.id == pessoa_id)

    return query


def filtrar_por_sigilo(
    query: Select,
    model: Any,
    user: Usuario,
    campo_sigiloso: str = "sigiloso",
    campo_responsavel: str = "responsavel_id",
) -> Select:
    """
    Aplica filtro de sigilo pastoral.

    Regra:
      - Se respeita_sigilo(user) e False (admin): sem filtro
      - Se o model nao tem os campos, sem filtro
      - Caso contrario: mostra registros onde sigiloso=False OU responsavel=user.id
        (ou seja: ve os nao-sigilosos + os sigilosos dos quais e responsavel)

    Funciona tanto pro usuario.id quanto pro pessoa_id, se voce passar
    o nome do campo_responsavel correto.
    """
    if not respeita_sigilo(user):
        return query

    if not hasattr(model, campo_sigiloso) or not hasattr(model, campo_responsavel):
        return query

    user_id = getattr(user, "id", None)
    if user_id is None:
        return query

    return query.where(
        or_(
            getattr(model, campo_sigiloso).is_(False),
            getattr(model, campo_sigiloso).is_(None),
            getattr(model, campo_responsavel) == user_id,
        )
    )


def filtrar_por_igreja_e_sigilo(
    query: Select,
    model: Any,
    user: Usuario,
    campo_sigiloso: str = "sigiloso",
    campo_responsavel: str = "responsavel_id",
) -> Select:
    """Atalho: aplica filtro de igreja + filtro de sigilo em sequencia."""
    query = filtrar_por_igreja(query, model, user)
    query = filtrar_por_sigilo(
        query, model, user, campo_sigiloso, campo_responsavel
    )
    return query


__all__ = [
    # identificacao
    "is_admin",
    "is_pastor",
    "is_lider",
    "is_membro",
    # capacidades
    "pode_ver_tudo",
    "pode_ver_igreja",
    "pode_gerenciar_usuarios",
    "pode_gerenciar_igrejas",
    "respeita_sigilo",
    # filtros
    "filtrar_por_igreja",
    "filtrar_pessoas_por_role",
    "filtrar_por_sigilo",
    "filtrar_por_igreja_e_sigilo",
]
