"""Планировщик событий вебхуков для 5903/5906.

- BackoffPolicy: next_attempt_at с удвоением от 1 минуты до 1 часа.
- SchedulerStorage: in-memory заглушка integration_webhook_events.
- EventScheduler: pick_batch с FOR UPDATE SKIP LOCKED, mark_processed/mark_failed,
  close_without_action.

Один экземпляр EventScheduler = один цикл воркера (как run_notifications_loop в
workers/integration_orders_scheduler.py).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from typing import Callable


@dataclass
class SchedulerEvent:
    """Строка integration_webhook_events (только поля, которые нужны планировщику)."""

    external_event_id: str
    event_type: str  # "message" | другое (см. 5906)
    payload_created: datetime | None  # payload.value.created, unix -> datetime
    processed: bool = False
    attempts_count: int = 0
    next_attempt_at: datetime | None = None
    error_message: str | None = None


@dataclass
class BackoffPolicy:
    """1 мин -> 1 час: base * 2^(attempts-1), но не больше max."""

    base_seconds: int = 60
    max_seconds: int = 3600

    def delay_after(self, attempts_count: int) -> timedelta:
        if attempts_count <= 0:
            return timedelta(0)
        seconds = self.base_seconds * (2 ** (attempts_count - 1))
        if seconds > self.max_seconds:
            seconds = self.max_seconds
        return timedelta(seconds=seconds)

    def next_attempt_at(self, now: datetime, attempts_count: int) -> datetime:
        return now + self.delay_after(attempts_count)


class SchedulerStorage:
    """In-memory заглушка таблицы integration_webhook_events.

    FOR UPDATE SKIP LOCKED эмулируется набором _locked:
    выбранное событие не отдаётся другим pick_batch(), пока не будет
    выпущено через mark_processed / mark_failed / close_without_action.
    """

    def __init__(self) -> None:
        self._events: dict[str, SchedulerEvent] = {}
        self._locked: set[str] = set()

    def add(self, event: SchedulerEvent) -> None:
        self._events[event.external_event_id] = event

    def get(self, event_id: str) -> SchedulerEvent | None:
        return self._events.get(event_id)

    def snapshot(self) -> list[SchedulerEvent]:
        return list(self._events.values())

    def save(self, event: SchedulerEvent) -> None:
        self._events[event.external_event_id] = event

    def lock(self, event_id: str) -> None:
        self._locked.add(event_id)

    def release(self, event_id: str) -> None:
        self._locked.discard(event_id)

    def is_locked(self, event_id: str) -> bool:
        return event_id in self._locked


class EventScheduler:
    """Выборка событий по правилам 5906:

      - processed = false;
      - next_attempt_at IS NULL OR next_attempt_at <= now;
      - для event_type = "message" — не раньше payload_created + notify_delay;
      - событие, уже захваченное другим воркером, пропускается (SKIP LOCKED).
    """

    def __init__(
        self,
        storage: SchedulerStorage,
        backoff: BackoffPolicy | None = None,
        notify_delay_seconds: int = 300,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._storage = storage
        self._backoff = backoff or BackoffPolicy()
        self._notify_delay = timedelta(seconds=notify_delay_seconds)
        self._clock = clock or (lambda: datetime.now(tz=timezone.utc))

    def _ready(self, event: SchedulerEvent, now: datetime) -> bool:
        if event.processed:
            return False
        if event.next_attempt_at is not None and event.next_attempt_at > now:
            return False
        if (
            event.event_type == "message"
            and event.payload_created is not None
            and event.payload_created + self._notify_delay > now
        ):
            return False
        return True

    def pick_batch(self, limit: int = 10) -> list[SchedulerEvent]:
        now = self._clock()
        picked: list[SchedulerEvent] = []
        for event in self._storage.snapshot():
            if len(picked) >= limit:
                break
            if self._storage.is_locked(event.external_event_id):
                continue  # SKIP LOCKED
            if not self._ready(event, now):
                continue
            self._storage.lock(event.external_event_id)
            picked.append(replace(event))
        return picked

    def mark_processed(self, event_id: str) -> None:
        event = self._storage.get(event_id)
        if event is None:
            return
        self._storage.save(replace(event, processed=True, error_message=None))
        self._storage.release(event_id)

    def mark_failed(self, event_id: str, error: str) -> None:
        event = self._storage.get(event_id)
        if event is None:
            return
        attempts = event.attempts_count + 1
        next_at = self._backoff.next_attempt_at(self._clock(), attempts)
        self._storage.save(
            replace(
                event,
                attempts_count=attempts,
                next_attempt_at=next_at,
                error_message=error,
            )
        )
        self._storage.release(event_id)

    def close_without_action(self, event_id: str, reason: str) -> None:
        """Закрыть без обработки: пауза, чужой аккаунт, не тот type (5906)."""
        event = self._storage.get(event_id)
        if event is None:
            return
        self._storage.save(replace(event, processed=True, error_message=reason))
        self._storage.release(event_id)