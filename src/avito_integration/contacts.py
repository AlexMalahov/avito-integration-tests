from __future__ import annotations

import re

PHONE_RE = re.compile(
    r"(?<!\d)(?:\+7|8)[\s\-()]*\d{3}[\s\-()]*\d{3}[\s\-()]*\d{2}[\s\-()]*\d{2}(?!\d)"
)
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

PARTICIPANTS_PATTERNS = [
    re.compile(r"(?:будет|на)\s+(\d{1,2})(?!\d)(?!\s*:\d{2})", re.IGNORECASE),
    re.compile(r"(\d{1,2})\s+(?:человек|гост|участник)", re.IGNORECASE),
]


def extract_contacts(texts: list[str]) -> dict:
    phone = None
    email = None
    participants = None
    for text in texts:
        if not text:
            continue
        if phone is None:
            m = PHONE_RE.search(text)
            if m:
                phone = m.group(0)
        if email is None:
            m = EMAIL_RE.search(text)
            if m:
                email = m.group(0)
        if participants is None:
            for pattern in PARTICIPANTS_PATTERNS:
                m = pattern.search(text)
                if m:
                    participants = int(m.group(1))
                    break
    return {"phone": phone, "email": email, "participants": participants}
