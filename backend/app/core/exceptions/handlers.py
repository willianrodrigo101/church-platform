class ChurchPlatformException(Exception):
    """Excecao base da plataforma."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(ChurchPlatformException):
    def __init__(self, entity: str, id_: str | int):
        super().__init__(
            message=f"{entity} com id {id_} nao encontrado",
            code="NOT_FOUND",
        )


class PermissionDeniedError(ChurchPlatformException):
    def __init__(self, action: str):
        super().__init__(
            message=f"Permissao negada para: {action}",
            code="PERMISSION_DENIED",
        )


class BusinessRuleError(ChurchPlatformException):
    def __init__(self, message: str):
        super().__init__(message=message, code="BUSINESS_RULE")
