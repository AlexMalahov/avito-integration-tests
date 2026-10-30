from __future__ import annotations

import httpx
import pytest
import respx
from freezegun import freeze_time

from avito_integration.errors import AvitoError, ErrorCode
from avito_integration.token_manager import TokenManager

from tests.fixtures.samples import TOKEN_RESPONSE


@pytest.fixture
def manager(http_client):
    return TokenManager(http_client)


async def test_first_call_fetches_token(mock_api, manager, avito_base_url):
    route = mock_api.post(f"{avito_base_url}/token/").mock(
        return_value=httpx.Response(200, json=TOKEN_RESPONSE)
    )
    token = await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    assert token == "test-access-token"
    assert route.called
    rows = manager.rows_for("acc-1")
    assert len(rows) == 1
    assert rows[0].expires_at is not None


async def test_valid_token_not_refetched(mock_api, manager, avito_base_url):
    route = mock_api.post(f"{avito_base_url}/token/").mock(
        return_value=httpx.Response(200, json=TOKEN_RESPONSE)
    )
    await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    assert route.call_count == 1


async def test_expired_token_refreshed(mock_api, manager, avito_base_url):
    mock_api.post(f"{avito_base_url}/token/").mock(
        return_value=httpx.Response(
            200, json={**TOKEN_RESPONSE, "access_token": "token-A", "expires_in": 120}
        )
    )
    with freeze_time("2025-01-01 00:00:00"):
        await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    # TTL = 120 - 60 = 60s → через 61s токен просрочен
    with freeze_time("2025-01-01 00:01:01"):
        route2 = mock_api.post(f"{avito_base_url}/token/").mock(
            return_value=httpx.Response(
                200, json={**TOKEN_RESPONSE, "access_token": "token-B"}
            )
        )
        token = await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    assert token == "token-B"
    assert route2.called
    assert len(manager.rows_for("acc-1")) == 1  # вторая строка не вставляется


@pytest.mark.parametrize("status", [400, 401, 403])
async def test_rejected_credentials_raise_unauthorized(mock_api, manager, avito_base_url, status):
    mock_api.post(f"{avito_base_url}/token/").mock(return_value=httpx.Response(status))
    with pytest.raises(AvitoError) as exc:
        await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    assert exc.value.error_code == ErrorCode.AVITO_UNAUTHORIZED.value


async def test_200_without_access_token_raises_unauthorized(mock_api, manager, avito_base_url):
    mock_api.post(f"{avito_base_url}/token/").mock(
        return_value=httpx.Response(200, json={"expires_in": 86400})
    )
    with pytest.raises(AvitoError) as exc:
        await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    assert exc.value.error_code == ErrorCode.AVITO_UNAUTHORIZED.value


async def test_single_row_for_account_key(mock_api, manager, avito_base_url):
    mock_api.post(f"{avito_base_url}/token/").mock(
        return_value=httpx.Response(200, json=TOKEN_RESPONSE)
    )
    await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    manager.invalidate("acc-1")
    await manager.get_token("acc-1", "cid", "secret", avito_base_url)
    assert len(manager.rows_for("acc-1")) == 1