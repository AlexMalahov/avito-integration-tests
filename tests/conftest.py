# tests/conftest.py
from __future__ import annotations

import httpx
import pytest
import respx


BASE_URL = "https://api.avito.ru"


@pytest.fixture
def avito_base_url() -> str:
    return BASE_URL


@pytest.fixture
async def http_client():
    async with httpx.AsyncClient() as client:
        yield client


@pytest.fixture
def mock_api():
    with respx.mock(assert_all_called=False, base_url=BASE_URL) as router:
        yield router