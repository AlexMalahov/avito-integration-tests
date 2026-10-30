from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    external_message_id: str
    chat_id: str
    author_id: int | None
    direction: str  # "in" | "out"
    message_type: str
    message_text: str | None
    message_created_at: datetime
    is_read: bool
    is_system: bool = False
    author_type: str = "customer"
    attachments: list[dict] = field(default_factory=list)
    payload: dict = field(default_factory=dict)


@dataclass
class Chat:
    chat_id: str
    item_id: int
    user_id: int | None
    updated: int
    last_message: dict | None = None


@dataclass
class Item:
    item_id: int
    title: str
    price: int | None
    status: str
    url: str | None = None
    address: str | None = None
    category_id: int | None = None
    category_name: str | None = None