"""Read-only проверки против dev-стенда. Ничего не создают и не меняют."""
from __future__ import annotations

import pytest


pytestmark = pytest.mark.live


def test_avito_present_in_catalog(providers):
    """5900: в /v1/integrations/providers Авито доступен, поля client_id/client_secret есть."""
    codes = [p.get("code") or p.get("provider_code") for p in providers]
    assert "avito" in codes, f"avito нет в каталоге. Известные: {codes}"

    avito = next(
        p for p in providers if (p.get("code") or p.get("provider_code")) == "avito"
    )
    availability = avito.get("availability")
    assert availability == "available", (
        f"availability = {availability!r}, ожидалось 'available'"
    )

    dumped = str(avito).lower()
    assert "client_id" in dumped, "в ответе нет поля client_id"
    assert "client_secret" in dumped, "в ответе нет поля client_secret"


def test_health_reports_webhooks_alive(api):
    """5906: /v1/integrations/health отдаёт webhooks.alive = true."""
    r = api.get("/v1/integrations/health")
    assert r.status_code == 200, (
        f"GET /v1/integrations/health → {r.status_code}: {r.text[:200]}"
    )
    body = r.json()
    webhooks = body.get("webhooks")
    if webhooks is None:
        pytest.skip(f"в /health нет поля webhooks. Поля ответа: {list(body.keys())}")
    alive = webhooks.get("alive") if isinstance(webhooks, dict) else None
    if alive is None:
        pytest.skip(f"в webhooks нет поля alive: {webhooks!r}")
    assert alive is True, f"webhooks.alive = {alive!r}, ожидалось True"


def test_webhook_public_endpoint_returns_404_for_invalid_token(anonymous):
    """5905: публичный вебхук с неизвестным подключением/токеном → 404, не 401."""
    r = anonymous.post(
        "/v1/public/integrations/avito/webhooks/"
        "00000000-0000-0000-0000-000000000000/bad-token",
        json={},
    )
    assert r.status_code == 404, (
        f"Ожидалось 404 (не 401) для неизвестного подключения/токена. "
        f"Получено {r.status_code}. Тело: {r.text[:200]}"
    )


def test_avito_connection_is_connected_and_credentials_configured(avito_connection):
    """5900: подключение Авито активно, ключи заданы, последняя синхронизация успешна.

    Проверка через публичные поля GET /v1/integrations/connections.
    external_account_id в ответе намеренно не выставляется — это внутренний
    идентификатор из БД (см. 5900, save_provider_connection).
    """
    assert avito_connection.get("connection_status") == "connected", (
        f"connection_status = {avito_connection.get('connection_status')!r}, "
        f"ожидалось 'connected'"
    )
    assert avito_connection.get("is_active") is True

    credentials = avito_connection.get("credentials") or []
    keys = {c.get("key"): c.get("configured") for c in credentials}
    assert keys.get("client_id") is True, f"client_id не сконфигурирован: {keys}"
    assert keys.get("client_secret") is True, f"client_secret не сконфигурирован: {keys}"

    last_sync = avito_connection.get("last_sync") or {}
    assert last_sync.get("status") in ("success", "partial"), (
        f"last_sync.status = {last_sync.get('status')!r}, ожидалось success/partial"
    )
    assert last_sync.get("last_success_at"), "нет last_sync.last_success_at"


def test_service_mappings_external_services_readable(api, avito_connection):
    """5904: GET .../service-mappings/external-services отвечает 200, is_available — bool."""
    uuid = (
        avito_connection.get("connection_uuid")
        or avito_connection.get("uuid")
        or avito_connection.get("account_uuid")
    )
    if not uuid:
        pytest.skip(f"нет UUID подключения. Поля: {list(avito_connection.keys())}")

    r = api.get(f"/v1/integrations/{uuid}/service-mappings/external-services")
    assert r.status_code == 200, (
        f"GET /v1/integrations/{uuid}/service-mappings/external-services → "
        f"{r.status_code}: {r.text[:200]}"
    )
    body = r.json()
    services = (
        body
        if isinstance(body, list)
        else body.get("items") or body.get("services") or []
    )
    for svc in services[:5]:
        assert isinstance(svc.get("is_available"), bool), (
            f"is_available не bool: {svc}"
        )