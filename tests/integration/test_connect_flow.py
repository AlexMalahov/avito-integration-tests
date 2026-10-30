from __future__ import annotations

import httpx
import pytest

from avito_integration.adapter import AvitoAdapter
from avito_integration.client import AvitoClient
from avito_integration.errors import AvitoError, ErrorCode
from avito_integration.token_manager import TokenManager

from tests.fixtures.samples import (
    ITEMS_PAGE_EMPTY,
    ITEMS_PAGE_ONE,
    SELF_RESPONSE,
    TOKEN_RESPONSE,
)


def make_adapter(http_client):
    tm = TokenManager(http_client)

    def factory(account_uuid, cid, secret, base_url):
        return AvitoClient(
            http=http_client,
            token_manager=tm,
            account_uuid=account_uuid,
            base_url=base_url,
            client_id=cid,
            client_secret=secret,
        )

    return AvitoAdapter(factory)


def _mock_happy_path(mock_api, base_url):
    mock_api.post(f"{base_url}/token/").mock(
        return_value=httpx.Response(200, json=TOKEN_RESPONSE)
    )
    mock_api.get(f"{base_url}/core/v1/accounts/self").mock(
        return_value=httpx.Response(200, json=SELF_RESPONSE)
    )
    mock_api.get(f"{base_url}/messenger/v2/accounts/123456789/chats").mock(
        return_value=httpx.Response(200, json={"chats": []})
    )
    mock_api.get(f"{base_url}/core/v1/items").mock(
        return_value=httpx.Response(200, json=ITEMS_PAGE_ONE)
    )


async def test_connect_happy_path(mock_api, http_client, avito_base_url):
    _mock_happy_path(mock_api, avito_base_url)
    adapter = make_adapter(http_client)
    result = await adapter.connect("acc-1", "cid", "secret", avito_base_url)
    assert result["external_account_id"] == "123456789"


async def test_connect_no_items_raises(mock_api, http_client, avito_base_url):
    _mock_happy_path(mock_api, avito_base_url)
    mock_api.get(f"{avito_base_url}/core/v1/items").mock(
        return_value=httpx.Response(200, json=ITEMS_PAGE_EMPTY)
    )
    adapter = make_adapter(http_client)
    with pytest.raises(AvitoError) as exc:
        await adapter.connect("acc-1", "cid", "secret", avito_base_url)
    assert exc.value.error_code == ErrorCode.AVITO_NO_ITEMS.value


async def test_connect_account_mismatch_raises_409(mock_api, http_client, avito_base_url):
    _mock_happy_path(mock_api, avito_base_url)
    adapter = make_adapter(http_client)
    with pytest.raises(AvitoError) as exc:
        await adapter.connect(
            "acc-1",
            "cid",
            "secret",
            avito_base_url,
            existing_external_account_id="999999999",
        )
    assert exc.value.error_code == ErrorCode.AVITO_ACCOUNT_MISMATCH.value
    assert exc.value.status == 409


async def test_connect_employee_key_denied(mock_api, http_client, avito_base_url):
    """
    С ключом сотрудника /chats отвечает 200 но пусто, /items пуст.
    В нашем контракте это ловится AVITO_NO_ITEMS.
    """
    _mock_happy_path(mock_api, avito_base_url)
    mock_api.get(f"{avito_base_url}/core/v1/items").mock(
        return_value=httpx.Response(200, json={"meta": {}, "resources": []})
    )
    adapter = make_adapter(http_client)
    with pytest.raises(AvitoError) as exc:
        await adapter.connect("acc-1", "cid", "secret", avito_base_url)
    assert exc.value.error_code == ErrorCode.AVITO_NO_ITEMS.value