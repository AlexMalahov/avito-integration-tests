from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from avito_integration.message_parser import parse_message
from avito_integration.notifications import NotificationRules

from tests.fixtures.samples import message_system, message_text


ORDER_UUID = "order-uuid-1"
FIRST_SEEN = datetime(2025, 1, 1, tzinfo=timezone.utc)


def make_message(direction="in", is_read=False, created=None, msg_type="text", text="hi"):
    raw = {
        "id": "m-42",
        "chat_id": "chat-1",
        "author_id": 42,
        "direction": direction,
        "type": msg_type,
        "content": {"text": text},
        "created": int((created or (FIRST_SEEN + timedelta(minutes=10))).timestamp()),
        "isRead": is_read,
    }
    return parse_message(raw)


def test_notify_flag_false_blocks():
    rules = NotificationRules(delay_seconds=300)
    ok, key = rules.evaluate(
        make_message(),
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=False,
        now=FIRST_SEEN + timedelta(minutes=20),
    )
    assert ok is False and key is None


def test_outgoing_blocks():
    rules = NotificationRules(delay_seconds=300)
    ok, _ = rules.evaluate(
        make_message(direction="out"),
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=True,
        now=FIRST_SEEN + timedelta(minutes=20),
    )
    assert ok is False


def test_older_than_first_seen_blocks():
    rules = NotificationRules(delay_seconds=300)
    ok, _ = rules.evaluate(
        make_message(created=FIRST_SEEN - timedelta(minutes=1)),
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=True,
        now=FIRST_SEEN + timedelta(minutes=20),
    )
    assert ok is False


def test_read_message_blocks():
    rules = NotificationRules(delay_seconds=300)
    ok, _ = rules.evaluate(
        make_message(is_read=True),
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=True,
        now=FIRST_SEEN + timedelta(minutes=20),
    )
    assert ok is False


def test_platform_read_blocks():
    rules = NotificationRules(delay_seconds=300)
    ok, _ = rules.evaluate(
        make_message(),
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=True,
        platform_is_unread=False,
        now=FIRST_SEEN + timedelta(minutes=20),
    )
    assert ok is False


def test_delay_blocks():
    rules = NotificationRules(delay_seconds=300)
    ok, _ = rules.evaluate(
        make_message(),
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=True,
        now=FIRST_SEEN + timedelta(minutes=10, seconds=30),  # 30s после сообщения
    )
    assert ok is False


def test_valid_notification_returns_dedup_key():
    rules = NotificationRules(delay_seconds=300)
    ok, key = rules.evaluate(
        make_message(),
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=True,
        now=FIRST_SEEN + timedelta(minutes=20),
    )
    assert ok is True
    assert key == f"message_received:{ORDER_UUID}:m-42"


def test_system_message_blocks():
    raw = message_system()
    raw["created"] = int((FIRST_SEEN + timedelta(minutes=10)).timestamp())
    raw["is_read"] = False
    msg = parse_message(raw)
    rules = NotificationRules(delay_seconds=300)
    ok, _ = rules.evaluate(
        msg,
        order_first_seen_at=FIRST_SEEN,
        order_uuid=ORDER_UUID,
        notify_flag=True,
        now=FIRST_SEEN + timedelta(minutes=20),
    )
    assert ok is False