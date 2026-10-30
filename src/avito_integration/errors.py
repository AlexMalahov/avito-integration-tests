from __future__ import annotations

from enum import Enum


class ErrorCode(str, Enum):
    AVITO_UNAUTHORIZED = "AVITO_UNAUTHORIZED"
    AVITO_MESSENGER_ACCESS_DENIED = "AVITO_MESSENGER_ACCESS_DENIED"
    AVITO_NO_ITEMS = "AVITO_NO_ITEMS"
    AVITO_ACCOUNT_MISMATCH = "AVITO_ACCOUNT_MISMATCH"
    PROVIDER_TOKEN_REJECTED = "PROVIDER_TOKEN_REJECTED"


AUTH_ERROR_CODES = frozenset({ErrorCode.AVITO_UNAUTHORIZED.value})


class AvitoError(Exception):
    def __init__(self, error_code: str, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status = status


class ChatAccessError(AvitoError):
    """Ошибка уровня одного чата (402/403) — не валит запуск синхронизации."""