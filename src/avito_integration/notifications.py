from __future__ import annotations

from datetime import datetime, timezone

from .models import Message


class NotificationRules:
    """
    Правило уведомления message_received из RAZRABOTKA-5901.
    """

    def __init__(self, delay_seconds: int = 300) -> None:
        self.delay_seconds = delay_seconds

    def evaluate(
        self,
        message: Message,
        order_first_seen_at: datetime,
        order_uuid: str,
        notify_flag: bool,
        platform_is_unread: bool | None = None,
        now: datetime | None = None,
    ) -> tuple[bool, str | None]:
        if not notify_flag:
            return False, None
        if message.direction != "in":
            return False, None
        if message.is_system:
            return False, None
        if message.message_created_at <= order_first_seen_at:
            return False, None
        if message.is_read:
            return False, None
        if platform_is_unread is False:
            return False, None

        now = now or datetime.now(tz=timezone.utc)
        age = (now - message.message_created_at).total_seconds()
        if age < self.delay_seconds:
            return False, None

        key = f"message_received:{order_uuid}:{message.external_message_id}"
        return True, key