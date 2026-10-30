"""Тесты планировщика вебхуков (RAZRABOTKA-5903/5906)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from avito_integration.scheduler import (
    BackoffPolicy,
    EventScheduler,
    SchedulerEvent,
    SchedulerStorage,
)

NOW = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)


def make_event(event_id="evt-1", event_type="message", payload_created=None, **kwargs):
    return SchedulerEvent(
        external_event_id=event_id,
        event_type=event_type,
        payload_created=payload_created,
        **kwargs,
    )


@pytest.mark.parametrize(
    "attempts,expected_seconds",
    [
        (1, 60),
        (2, 120),
        (3, 240),
        (4, 480),
        (5, 960),
        (6, 1920),
        (7, 3600),   # 3840 -> обрезано до 1 часа
        (100, 3600), # выше потолка — тоже 1 час
    ],
)
def test_backoff_grows_exponentially_then_caps(attempts, expected_seconds):
    assert BackoffPolicy().delay_after(attempts).total_seconds() == expected_seconds


def test_pick_skips_processed_not_due_and_locked():
    storage = SchedulerStorage()
    storage.add(make_event("done", processed=True))
    storage.add(make_event("future", next_attempt_at=NOW + timedelta(minutes=1)))
    storage.add(make_event("ready"))
    sched = EventScheduler(storage, clock=lambda: NOW)

    picked = sched.pick_batch()
    assert [e.external_event_id for e in picked] == ["ready"]

    # ready уже locked → SKIP LOCKED; done/future всё ещё не подходят
    assert sched.pick_batch() == []


def test_message_not_picked_before_delay():
    storage = SchedulerStorage()
    storage.add(make_event("young", payload_created=NOW - timedelta(seconds=10)))
    storage.add(make_event("old", payload_created=NOW - timedelta(seconds=400)))
    sched = EventScheduler(storage, notify_delay_seconds=300, clock=lambda: NOW)

    assert [e.external_event_id for e in sched.pick_batch()] == ["old"]


def test_mark_failed_increments_and_schedules_retry():
    storage = SchedulerStorage()
    storage.add(make_event("evt-1"))
    sched = EventScheduler(storage, clock=lambda: NOW)

    sched.pick_batch()
    sched.mark_failed("evt-1", "boom")
    e = storage.get("evt-1")
    assert e.attempts_count == 1
    assert e.next_attempt_at == NOW + timedelta(seconds=60)
    assert e.error_message == "boom"
    assert e.processed is False

    # До наступления next_attempt_at событие не выдаётся
    assert sched.pick_batch() == []

    # Прошла минута + 1 секунда — снова выдаётся, теперь с задержкой 120s
    later = NOW + timedelta(seconds=61)
    sched2 = EventScheduler(storage, clock=lambda: later)
    assert [x.external_event_id for x in sched2.pick_batch()] == ["evt-1"]
    sched2.mark_failed("evt-1", "boom-2")
    e = storage.get("evt-1")
    assert e.attempts_count == 2
    assert e.next_attempt_at == later + timedelta(seconds=120)


def test_mark_processed_clears_error_and_releases_lock():
    storage = SchedulerStorage()
    storage.add(make_event("evt-1", error_message="previous"))
    sched = EventScheduler(storage, clock=lambda: NOW)

    assert [e.external_event_id for e in sched.pick_batch()] == ["evt-1"]
    assert storage.is_locked("evt-1") is True

    sched.mark_processed("evt-1")
    e = storage.get("evt-1")
    assert e.processed is True
    assert e.error_message is None
    assert storage.is_locked("evt-1") is False


def test_close_without_action_marks_processed_with_reason():
    storage = SchedulerStorage()
    storage.add(make_event("evt-1"))
    sched = EventScheduler(storage, clock=lambda: NOW)

    sched.pick_batch()
    sched.close_without_action("evt-1", "connection on pause")
    e = storage.get("evt-1")
    assert e.processed is True
    assert e.error_message == "connection on pause"
    assert storage.is_locked("evt-1") is False