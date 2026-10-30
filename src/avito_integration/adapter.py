from __future__ import annotations

from typing import Callable

from .client import AvitoClient
from .errors import AvitoError, ErrorCode


ClientFactory = Callable[[str, str, str, str], AvitoClient]


class AvitoAdapter:
    """
    Поток connect из RAZRABOTKA-5900:
      1) token (получается лениво)
      2) /core/v1/accounts/self
      3) список чатов limit=1
      4) первая страница /core/v1/items
      5) проверка external_account_id
    """

    def __init__(self, client_factory: ClientFactory) -> None:
        self._factory = client_factory

    async def connect(
        self,
        account_uuid: str,
        client_id: str,
        client_secret: str,
        base_url: str,
        existing_external_account_id: str | None = None,
    ) -> dict:
        client = self._factory(account_uuid, client_id, client_secret, base_url)

        self_data = await client.account_self()
        external_account_id = str(self_data["id"])

        await client.list_chats(self_data["id"], limit=1)

        items_page = await client.list_items(per_page=1, page=1)
        if not items_page.get("resources"):
            raise AvitoError(
                ErrorCode.AVITO_NO_ITEMS.value,
                "Нужны ключи основного аккаунта компании",
                400,
            )

        if (
            existing_external_account_id is not None
            and existing_external_account_id != external_account_id
        ):
            raise AvitoError(
                ErrorCode.AVITO_ACCOUNT_MISMATCH.value,
                "К компании подключён другой аккаунт Avito",
                409,
            )

        return {"external_account_id": external_account_id}