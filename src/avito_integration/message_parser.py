from __future__ import annotations

from datetime import datetime, timezone

from .models import Message

SUBSCRIPTION_STUB_MARKER = "Перейдите на подписку с API мессенджера"


def parse_message(raw: dict, users: list[dict] | None = None) -> Message:
    users_by_id = {u.get("id"): u for u in (users or [])}
    msg_type = raw.get("type", "text")
    content = raw.get("content") or {}

    author_id = raw.get("author_id")
    direction = "in" if raw.get("direction") == "in" else "out"

    if "isRead" in raw:
        is_read = bool(raw["isRead"])
    else:
        is_read = bool(raw.get("is_read", False))

    is_system = msg_type == "system"
    if is_system and content.get("flow_id"):
        author_type = "system"
    elif direction == "out":
        author_type = "manager"
    else:
        author_type = "customer"

    text: str | None
    payload: dict = {}

    if msg_type in ("text", "system"):
        text = content.get("text")
    elif msg_type == "call":
        call = content.get("call") or {}
        text = "Пропущенный звонок" if call.get("status") == "missed" else "Звонок"
        payload["call"] = call
    elif msg_type == "link":
        text = content.get("text") or content.get("url")
    elif msg_type == "item":
        text = (content.get("item") or {}).get("title")
    elif msg_type == "location":
        text = (content.get("location") or {}).get("title")
    else:
        text = content.get("text")

    if text and SUBSCRIPTION_STUB_MARKER in text:
        text = None
        payload["content_unavailable"] = True

    attachments: list[dict] = []
    if msg_type == "image":
        attachments = [{"type": "image", "sizes": (content.get("image") or {}).get("sizes") or []}]
    elif msg_type == "voice":
        attachments = [{"type": "voice", "voice_id": content.get("voice_id")}]
    elif msg_type == "link":
        attachments = [{"type": "link", "url": content.get("url"), "preview": content.get("preview")}]
    elif msg_type == "item":
        item = content.get("item") or {}
        attachments = [{
            "type": "item",
            "title": item.get("title"),
            "item_url": item.get("url"),
            "image_url": item.get("image_url"),
            "price_string": item.get("price_string"),
        }]
    elif msg_type == "location":
        loc = content.get("location") or {}
        attachments = [{
            "type": "location",
            "lat": loc.get("lat"),
            "lon": loc.get("lon"),
            "title": loc.get("title"),
        }]

    created = raw.get("created")
    message_created_at = (
        datetime.fromtimestamp(int(created), tz=timezone.utc)
        if created is not None
        else datetime.now(tz=timezone.utc)
    )

    payload.update({
        "read": raw.get("read"),
        "quote": raw.get("quote"),
        "flow_id": content.get("flow_id"),
    })

    return Message(
        external_message_id=str(raw.get("id")),
        chat_id=str(raw.get("chat_id")),
        author_id=author_id,
        direction=direction,
        message_type=msg_type,
        message_text=text,
        message_created_at=message_created_at,
        is_read=is_read,
        is_system=is_system,
        author_type=author_type,
        attachments=attachments,
        payload=payload,
    )