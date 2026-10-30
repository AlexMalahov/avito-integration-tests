from __future__ import annotations

import hmac
import json
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone


MAX_BODY_BYTES = 64 * 1024
ALLOWED_HEADERS = {"content-type", "user-agent"}


@dataclass
class WebhookEvent:
    provider_uuid: str
    account_uuid: str
    company_uuid: str
    event_type: str | None
    external_event_id: str | None
    external_order_id: str | None
    payload: dict
    headers: dict
    received_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


class WebhookStorage:
    """Заглушка таблицы integration_webhook_events с UNIQUE(provider_uuid, external_event_id)."""

    def __init__(self) -> None:
        self.events: list[WebhookEvent] = []
        self._seen: set[tuple[str, str]] = set()

    def save(self, event: WebhookEvent) -> bool:
        if event.external_event_id is None:
            return False
        key = (event.provider_uuid, event.external_event_id)
        if key in self._seen:
            return False
        self._seen.add(key)
        self.events.append(event)
        return True


def generate_webhook_token() -> str:
    return secrets.token_urlsafe(32)


class WebhookHandler:
    """
    Обработчик POST /v1/public/integrations/avito/webhooks/{connection_uuid}/{token}.
    Никаких запросов к Avito — только запись события.
    """

    def __init__(self, storage: WebhookStorage) -> None:
        self._storage = storage

    def handle(
        self,
        connection_token: str,
        provided_token: str,
        body_bytes: bytes,
        connection_uuid: str,
        provider_uuid: str,
        company_uuid: str,
        headers: dict,
    ) -> tuple[int, str]:
        if not hmac.compare_digest(connection_token.encode(), provided_token.encode()):
            return 404, "not found"
        if len(body_bytes) > MAX_BODY_BYTES:
            return 413, "payload too large"
        try:
            payload = json.loads(body_bytes or b"{}")
        except json.JSONDecodeError:
            return 400, "invalid json"
        if not payload.get("id"):
            # Avito при подписке присылает POST с телом '{}' — просто 200
            return 200, "ok"

        value = payload.get("value") or {}
        chat_id = value.get("chat_id")
        event = WebhookEvent(
            provider_uuid=provider_uuid,
            account_uuid=connection_uuid,
            company_uuid=company_uuid,
            event_type=payload.get("type"),
            external_event_id=str(payload["id"]),
            external_order_id=str(chat_id) if chat_id is not None else None,
            payload=payload,
            headers={
                k: v for k, v in headers.items() if k.lower() in ALLOWED_HEADERS
            },
        )
        self._storage.save(event)
        return 200, "ok"