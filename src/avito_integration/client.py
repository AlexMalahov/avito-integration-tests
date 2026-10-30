from __future__ import annotations

from typing import Any

import httpx

from .errors import AvitoError, ChatAccessError, ErrorCode
from .token_manager import TokenManager


class AvitoClient:
    """
    Тонкий клиент Avito с правилами классификации ошибок из 5900.
    """

    def __init__(
        self,
        http: httpx.AsyncClient,
        token_manager: TokenManager,
        account_uuid: str,
        base_url: str,
        client_id: str,
        client_secret: str,
    ) -> None:
        self._http = http
        self._tm = token_manager
        self._account_uuid = account_uuid
        self._base = base_url.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret

    async def _token(self) -> str:
        return await self._tm.get_token(
            self._account_uuid, self._client_id, self._client_secret, self._base
        )

    async def _send(self, method: str, path: str, token: str, **kwargs: Any) -> httpx.Response:
        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = f"Bearer {token}"
        return await self._http.request(method, f"{self._base}{path}", headers=headers, **kwargs)

    async def _request_with_retry(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        token = await self._token()
        response = await self._send(method, path, token, **kwargs)
        if response.status_code in (401, 403):
            self._tm.invalidate(self._account_uuid)
            token = await self._token()
            response = await self._send(method, path, token, **kwargs)
        return response

    async def account_self(self) -> dict:
        response = await self._request_with_retry("GET", "/core/v1/accounts/self")
        if response.status_code in (401, 403):
            raise AvitoError(ErrorCode.AVITO_UNAUTHORIZED.value, "Unauthorized", response.status_code)
        response.raise_for_status()
        return response.json()

    async def list_chats(self, user_id: int, limit: int = 100, offset: int = 0) -> dict:
        response = await self._request_with_retry(
            "GET",
            f"/messenger/v2/accounts/{user_id}/chats",
            params={"chat_types": "u2i", "limit": limit, "offset": offset},
        )
        if response.status_code in (401, 402, 403):
            self_resp = await self._send("GET", "/core/v1/accounts/self", await self._token())
            if self_resp.status_code == 200:
                raise AvitoError(
                    ErrorCode.AVITO_MESSENGER_ACCESS_DENIED.value,
                    "Messenger API access denied",
                    response.status_code,
                )
            raise AvitoError(ErrorCode.AVITO_UNAUTHORIZED.value, "Unauthorized", response.status_code)
        response.raise_for_status()
        return response.json()

    async def get_chat(self, user_id: int, chat_id: str) -> dict:
        response = await self._request_with_retry(
            "GET", f"/messenger/v2/accounts/{user_id}/chats/{chat_id}"
        )
        if response.status_code == 402:
            raise ChatAccessError("CHAT_ACCESS_DENIED", "Chat access denied (402)", 402)
        if response.status_code == 403:
            self_resp = await self._send("GET", "/core/v1/accounts/self", await self._token())
            if self_resp.status_code == 200:
                raise ChatAccessError("CHAT_ACCESS_DENIED", "Chat access denied (403)", 403)
            raise AvitoError(ErrorCode.AVITO_UNAUTHORIZED.value, "Unauthorized", 403)
        if response.status_code == 401:
            raise AvitoError(ErrorCode.AVITO_UNAUTHORIZED.value, "Unauthorized", 401)
        response.raise_for_status()
        return response.json()

    async def list_messages(
        self, user_id: int, chat_id: str, limit: int = 100, offset: int = 0
    ) -> list[dict]:
        response = await self._request_with_retry(
            "GET",
            f"/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages",
            params={"limit": limit, "offset": offset},
        )
        if response.status_code == 402:
            raise ChatAccessError("CHAT_ACCESS_DENIED", "Chat access denied (402)", 402)
        if response.status_code == 403:
            self_resp = await self._send("GET", "/core/v1/accounts/self", await self._token())
            if self_resp.status_code == 200:
                raise ChatAccessError("CHAT_ACCESS_DENIED", "Chat access denied (403)", 403)
            raise AvitoError(ErrorCode.AVITO_UNAUTHORIZED.value, "Unauthorized", 403)
        if response.status_code == 401:
            raise AvitoError(ErrorCode.AVITO_UNAUTHORIZED.value, "Unauthorized", 401)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else data.get("messages", [])

    async def list_items(self, per_page: int = 99, page: int = 1) -> dict:
        response = await self._request_with_retry(
            "GET",
            "/core/v1/items",
            params={
                "per_page": per_page,
                "page": page,
                "status": "active,removed,old,blocked,rejected",
            },
        )
        response.raise_for_status()
        return response.json()