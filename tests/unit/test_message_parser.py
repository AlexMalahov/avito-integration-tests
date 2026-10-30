from __future__ import annotations

from datetime import datetime, timezone

from avito_integration.message_parser import parse_message

from tests.fixtures.samples import (
    message_image,
    message_stub,
    message_system,
    message_text,
)


def test_text_message_direction_in():
    msg = parse_message(message_text(direction="in"))
    assert msg.direction == "in"
    assert msg.message_text == "Привет"
    assert msg.author_type == "customer"
    assert msg.is_system is False


def test_text_message_direction_out():
    msg = parse_message(message_text(direction="out", author_id=123456789))
    assert msg.direction == "out"
    assert msg.author_type == "manager"


def test_isRead_camel_case_supported():
    raw = message_text()
    raw["isRead"] = True
    raw.pop("is_read", None)
    assert parse_message(raw).is_read is True


def test_is_read_snake_case_supported():
    raw = message_text()
    raw.pop("isRead", None)
    raw["is_read"] = True
    assert parse_message(raw).is_read is True


def test_system_with_flow_id():
    msg = parse_message(message_system())
    assert msg.is_system is True
    assert msg.author_type == "system"


def test_image_attachments_all_sizes():
    msg = parse_message(message_image())
    assert msg.attachments[0]["type"] == "image"
    assert len(msg.attachments[0]["sizes"]) == 2


def test_subscription_stub_marks_unavailable():
    msg = parse_message(message_stub())
    assert msg.message_text is None
    assert msg.payload.get("content_unavailable") is True


def test_call_missed_text():
    raw = {
        "id": "m-9",
        "chat_id": "c-1",
        "author_id": 42,
        "direction": "in",
        "type": "call",
        "content": {"call": {"status": "missed", "target_user_id": 42}},
        "created": 1_700_000_000,
        "isRead": False,
    }
    msg = parse_message(raw)
    assert msg.message_text == "Пропущенный звонок"
    assert msg.payload["call"]["status"] == "missed"


def test_deleted_message_has_no_text():
    raw = {
        "id": "m-10",
        "chat_id": "c-1",
        "author_id": 42,
        "direction": "in",
        "type": "deleted",
        "content": {},
        "created": 1_700_000_000,
        "isRead": False,
    }
    assert parse_message(raw).message_text is None


def test_created_unix_to_datetime():
    msg = parse_message(message_text())
    assert msg.message_created_at == datetime.fromtimestamp(1_700_000_000, tz=timezone.utc)