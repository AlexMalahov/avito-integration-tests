from __future__ import annotations

import httpx
import pytest

from avito_integration.client import AvitoClient
from avito_integration.errors import AvitoError, ChatAccessError, ErrorCode
from avito_integration.token_manager import TokenManager

from tests.fixtures.samples import CHATS_PAGE_SHORT, SELF_RESPONSE, TOKEN_RESPONSE


@pytest.fixture
def client(http_client, avito_base_url):
    tm = TokenManager(http_client)
    return AvitoClient(
        http=http_client,
        token_manager=tm,
        account_uuid="acc-1",
        base_url=avito_base_url,
        client_id="cid",
        client_secret="secret",
    )


def _mock_token(mock_api, base_url):
    return mock_api.post(f"{base_url}/token/").mock(
        return_value=httpx.Response(200, json=TOKEN_RESPONSE)
    )


async def test_account_self_401_after_retry_raises_unauthorized(mock_api, client, avito_base_url):
    _mock_token(mock_api, avito_base_url)
    mock_api.get(f"{avito_base_url}/core/v1/accounts/self").mock(
        return_value=httpx.Response(401)
    )
    with pytest.raises(AvitoError) as exc:
        await client.account_self()
    assert exc.value.error_code == ErrorCode.AVITO_UNAUTHORIZED.value


async def test_chats_401_with_self_ok_raises_messenger_denied(mock_api, client, avito_base_url):
    _mock_token(mock_api, avito_base_url)
    mock_api.get(f"{avito_base_url}/core/v1/accounts/self").mock(
        return_value=httpx.Response(200, json=SELF_RESPONSE)
    )
    mock_api.get(f"{avito_base_url}/messenger/v2/accounts/123456789/chats").mock(
        return_value=httpx.Response(403)
    )
    with pytest.raises(AvitoError) as exc:
        await client.list_chats(123456789, limit=1)
    assert exc.value.error_code == ErrorCode.AVITO_MESSENGER_ACCESS_DENIED.value


async def test_chats_401_with_self_401_raises_unauthorized(mock_api, client, avito_base_url):
    _mock_token(mock_api, avito_base_url)
    mock_api.get(f"{avito_base_url}/core/v1/accounts/self").mock(
        return_value=httpx.Response(401)
    )
    mock_api.get(f"{avito_base_url}/messenger/v2/accounts/123456789/chats").mock(
        return_value=httpx.Response(401)
    )
    with pytest.raises(AvitoError) as exc:
        await client.list_chats(123456789, limit=1)
    assert exc.value.error_code == ErrorCode.AVITO_UNAUTHORIZED.value


async def test_get_chat_402_raises_chat_access_without_retry(mock_api, client, avito_base_url):
    _mock_token(mock_api, avito_base_url)
    route = mock_api.get(
        f"{avito_base_url}/messenger/v2/accounts/123456789/chats/chat-x"
    ).mock(return_value=httpx.Response(402))
    with pytest.raises(ChatAccessError):
        await client.get_chat(123456789, "chat-x")
    # 402 не должен вызывать повторной попытки
    assert route.call_count == 1


async def test_get_chat_403_after_retry_with_self_ok_raises_chat_access(
    mock_api, client, avito_base_url
):
    _mock_token(mock_api, avito_base_url)
    mock_api.get(f"{avito_base_url}/core/v1/accounts/self").mock(
        return_value=httpx.Response(200, json=SELF_RESPONSE)
    )
    mock_api.get(
        f"{avito_base_url}/messenger/v2/accounts/123456789/chats/chat-x"
    ).mock(return_value=httpx.Response(403))
    with pytest.raises(ChatAccessError):
        await client.get_chat(123456789, "chat-x")


async def test_list_messages_402_raises_chat_access(mock_api, client, avito_base_url):
    _mock_token(mock_api, avito_base_url)
    mock_api.get(
        f"{avito_base_url}/messenger/v3/accounts/123456789/chats/chat-x/messages"
    ).mock(return_value=httpx.Response(402))
    with pytest.raises(ChatAccessError):
        await client.list_messages(123456789, "chat-x")


async def test_list_messages_success_returns_list(mock_api, client, avito_base_url):
    _mock_token(mock_api, avito_base_url)
    mock_api.get(
        f"{avito_base_url}/messenger/v3/accounts/123456789/chats/chat-x/messages"
    ).mock(return_value=httpx.Response(200, json=[{"id": "m-1"}]))
    data = await client.list_messages(123456789, "chat-x")
    assert data == [{"id": "m-1"}]