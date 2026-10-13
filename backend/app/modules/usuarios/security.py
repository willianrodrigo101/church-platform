from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config.settings import settings
from app.core.exceptions.handlers import ChurchPlatformException


def hash_senha(senha: str) -> str:
    """Gera hash bcrypt da senha."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(senha.encode("utf-8"), salt).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha bate com o hash."""
    try:
        return bcrypt.checkpw(
            senha.encode("utf-8"),
            senha_hash.encode("utf-8"),
        )
    except Exception:
        return False


def criar_token(dados: dict[str, Any]) -> str:
    payload = dados.copy()
    expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["exp"] = expira
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decodificar_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ChurchPlatformException(
            "Token invalido ou expirado", "INVALID_TOKEN"
        ) from exc