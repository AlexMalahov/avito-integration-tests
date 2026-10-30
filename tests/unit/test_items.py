from __future__ import annotations

from avito_integration.items import item_to_external_service


def test_active_item_is_available():
    svc = item_to_external_service(
        {
            "item_id": 2001,
            "title": "Экскурсия",
            "price": 1500,
            "status": "active",
            "address": "Москва",
        }
    )
    assert svc.external_service_id == "2001"
    assert svc.name == "Экскурсия"
    assert svc.price == 1500
    assert svc.start_place == "Москва"
    assert svc.currency is None  # валюта не указана в ответе
    assert svc.status == "active"
    assert svc.is_available is True


def test_removed_item_not_available():
    svc = item_to_external_service(
        {"item_id": 2002, "title": "Старая", "price": None, "status": "removed"}
    )
    assert svc.is_available is False


def test_active_but_missing_in_last_response_not_available():
    svc = item_to_external_service(
        {"item_id": 2003, "title": "X", "price": 0, "status": "active"},
        was_in_last_full_response=False,
    )
    assert svc.is_available is False


def test_big_int_item_id_stringified():
    # на dev id объявлений больше 2^31
    svc = item_to_external_service(
        {"item_id": 2_500_000_001, "title": "big", "price": 1, "status": "active"}
    )
    assert svc.external_service_id == "2500000001"