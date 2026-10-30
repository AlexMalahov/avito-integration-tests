from __future__ import annotations

import pytest

from avito_integration.contacts import extract_contacts


def test_phone_extracted():
    result = extract_contacts(["Здравствуйте, мой телефон +7 (999) 123-45-67"])
    assert result["phone"] is not None
    assert "999" in result["phone"]


def test_email_extracted():
    result = extract_contacts(["Пишите на ivan.petrov@example.com"])
    assert result["email"] == "ivan.petrov@example.com"


def test_participants_budet_5():
    result = extract_contacts(["Нас будет 5 человек"])
    assert result["participants"] == 5


def test_participants_budet_10_00_not_matched():
    result = extract_contacts(["Встреча будет 10:00 у входа"])
    assert result["participants"] is None


def test_participants_5_chelovek():
    result = extract_contacts(["Нас 5 человек, двое детей"])
    assert result["participants"] == 5


def test_no_contacts():
    result = extract_contacts(["Просто вопрос по экскурсии"])
    assert result == {"phone": None, "email": None, "participants": None}


def test_contacts_from_multiple_messages():
    result = extract_contacts([
        "Меня зовут Иван",
        "Телефон: 8 999 111 22 33",
        "нас будет 4 человека",
    ])
    assert result["phone"] is not None
    assert result["participants"] == 4