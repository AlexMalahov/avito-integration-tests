from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import httpx

from .errors import AvitoError, ErrorCode


@dataclass
class CredentialRow:
    account_uuid: str
    key_name: str
    encrypted_value: str
    expires_at: datetime | None
    is_active: bool = True
    credential_type: str = "access_token"


class TokenManager:
    """
    Одна строка access_token на (account_uuid, key_name).
    Хранит срок expires_at = now + expires_in - 60s.
    """

    TTL_MARGIN_SECONDS = 60

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http
        self._rows: dict[tuple[str, str], CredentialRow] = {}
        self._lock = asyncio.Lock()

    def _find(self, account_uuid: str, key_name: str) -> CredentialRow | None:
        return self._rows.get((account_uuid, key_name))

    def invalidate(self, account_uuid: str) -> None:
        row = self._rows.get((account_uuid, "access_token"))
        if row is not None:
            row.expires_at = None

    def rows_for(self, account_uuid: str) -> list[CredentialRow]:
        return [r for (a, _k), r in self._rows.items() if a == account_uuid]

    async def get_token(
        self,
        account_uuid: str,
        client_id: str,
        client_secret: str,
        base_url: str,
    ) -> str:
        async with self._lock:
            now = datetime.now(timezone.utc)
            row = self._find(account_uuid, "access_token")
            if row and row.is_active and row.expires_at and row.expires_at > now:
                return row.encrypted_value

            response = await self._http.post(
                f"{base_url.rstrip('/')}/token/",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )
            if response.status_code in (400, 401, 403):
                raise AvitoError(
                    ErrorCode.AVITO_UNAUTHORIZED.value,
                    "Token rejected",
                    response.status_code,
                )
            body = response.json()
            access_token = body.get("access_token")
            if not access_token:
                raise AvitoError(
                    ErrorCode.AVITO_UNAUTHORIZED.value,
                    "Response 200 without access_token",
                    200,
                )
            expires_in = int(body.get("expires_in", 86400))
            expires_at = now + timedelta(seconds=expires_in - self.TTL_MARGIN_SECONDS)

            if row is None:
                row = CredentialRow(
                    account_uuid=account_uuid,
                    key_name="access_token",
                    encrypted_value=access_token,
                    expires_at=expires_at,
                )
                self._rows[(account_uuid, "access_token")] = row
            else:
                row.encrypted_value = access_token
                row.expires_at = expires_at
                row.is_active = True
            return access_token