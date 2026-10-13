"""Excecoes de dominio da aplicacao."""
from app.core.exceptions.handlers import (
    BusinessRuleError,
    NotFoundError,
)

__all__ = [
    "BusinessRuleError",
    "NotFoundError",
]
