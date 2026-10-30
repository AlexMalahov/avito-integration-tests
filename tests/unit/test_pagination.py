from __future__ import annotations

from avito_integration.pagination import read_all_pages


async def test_short_page_stops():
    async def fetch(offset, limit):
        return [{"id": "m-1"}]

    result = await read_all_pages(fetch, limit=100)
    assert len(result) == 1


async def test_full_page_with_all_saved_stops():
    async def fetch(offset, limit):
        if offset == 0:
            return [{"id": f"m-{i}"} for i in range(100)]
        return [{"id": f"m-{offset + i}"} for i in range(100)]

    result = await read_all_pages(fetch, is_saved=lambda m: True, limit=100)
    assert len(result) == 100


async def test_full_page_with_new_continues():
    """На странице есть несохранённые — продолжаем листать до короткой страницы (5902)."""
    pages = {
        0: [{"id": f"m-{i}"} for i in range(100)],
        100: [{"id": f"m-{100 + i}"} for i in range(50)],
    }
    # m-0..m-49 уже сохранены, m-50..m-149 — новые
    saved_ids = {f"m-{i}" for i in range(50)}

    async def fetch(offset, limit):
        return pages.get(offset, [])

    result = await read_all_pages(
        fetch,
        is_saved=lambda m: m["id"] in saved_ids,
        limit=100,
    )
    # страница 0: 50 новых -> продолжаем
    # страница 100: 50 < limit -> стоп
    assert len(result) == 150
    assert any(m["id"] == "m-50" for m in result)
    assert any(m["id"] == "m-149" for m in result)


async def test_offset_limit_stops():
    async def fetch(offset, limit):
        return [{"id": f"m-{offset + i}"} for i in range(limit)]

    result = await read_all_pages(fetch, is_saved=lambda m: False, limit=100, max_offset=200)
    assert len(result) == 300
