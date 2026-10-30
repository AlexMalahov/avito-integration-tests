from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExternalService:
    external_service_id: str
    name: str
    start_place: str | None
    price: int | None
    currency: str | None
    status: str
    is_available: bool


def item_to_external_service(item: dict, was_in_last_full_response: bool = True) -> ExternalService:
    status = item.get("status", "unknown")
    return ExternalService(
        external_service_id=str(item["item_id"]),
        name=item.get("title", ""),
        start_place=item.get("address"),
        price=item.get("price"),
        currency=None,  # валюта не указана в ответе /core/v1/items
        status=status,
        is_available=(status == "active" and was_in_last_full_response),
    )