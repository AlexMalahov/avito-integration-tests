from __future__ import annotations


TOKEN_RESPONSE = {
    "access_token": "test-access-token",
    "expires_in": 86400,
    "token_type": "Bearer",
}

SELF_RESPONSE = {"id": 123456789, "name": "Kalita Test Account"}

CHATS_PAGE_FULL = {
    "chats": [
        {
            "id": f"chat-{i}",
            "updated": 1_700_000_000 + i,
            "item_id": 1000 + i,
            "users": [{"id": 123456789, "name": "Менеджер"}],
            "last_message": {"id": f"m-{i}", "type": "text", "content": {"text": "hi"}},
        }
        for i in range(100)
    ]
}

CHATS_PAGE_SHORT = {
    "chats": [
        {
            "id": "chat-only",
            "updated": 1_700_000_001,
            "item_id": 1001,
            "users": [{"id": 123456789}],
            "last_message": {"id": "m-1", "type": "text", "content": {"text": "hello"}},
        }
    ]
}

ITEMS_PAGE_ONE = {
    "meta": {"page": 1, "per_page": 1},
    "resources": [
        {
            "item_id": 2001,
            "title": "Экскурсия по Москве",
            "price": 1500,
            "status": "active",
            "url": "https://avito.ru/item/2001",
            "address": "Москва, Красная площадь",
        }
    ],
}

ITEMS_PAGE_EMPTY = {"meta": {"page": 1, "per_page": 1}, "resources": []}


def message_text(msg_id="m-1", chat_id="chat-1", author_id=42, direction="in", text="Привет"):
    return {
        "id": msg_id,
        "chat_id": chat_id,
        "author_id": author_id,
        "direction": direction,
        "type": "text",
        "content": {"text": text},
        "created": 1_700_000_000,
        "isRead": False,
    }


def message_system(msg_id="m-2", chat_id="chat-1"):
    return {
        "id": msg_id,
        "chat_id": chat_id,
        "author_id": 999,
        "direction": "in",
        "type": "system",
        "content": {"text": "Здравствуйте!", "flow_id": "auto-reply-1"},
        "created": 1_700_000_001,
        "is_read": False,
    }


def message_image(msg_id="m-3", chat_id="chat-1"):
    return {
        "id": msg_id,
        "chat_id": chat_id,
        "author_id": 42,
        "direction": "in",
        "type": "image",
        "content": {
            "image": {
                "sizes": [
                    {"url": "https://avito.ru/img/small.jpg", "width": 100, "height": 100},
                    {"url": "https://avito.ru/img/large.jpg", "width": 800, "height": 800},
                ]
            }
        },
        "created": 1_700_000_002,
        "isRead": False,
    }


def message_stub(msg_id="m-4", chat_id="chat-1"):
    return {
        "id": msg_id,
        "chat_id": chat_id,
        "author_id": 42,
        "direction": "in",
        "type": "text",
        "content": {"text": "Перейдите на подписку с API мессенджера, чтобы получить доступ к чатам"},
        "created": 1_700_000_003,
        "isRead": False,
    }