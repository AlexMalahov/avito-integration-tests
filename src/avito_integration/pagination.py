from __future__ import annotations

from typing import Awaitable, Callable


PAGE_LIMIT = 100
MAX_OFFSET = 1000


async def read_all_pages(
    fetch_page: Callable[..., Awaitable[list[dict]]],
    is_saved: Callable[[dict], bool] | None = None,
    limit: int = PAGE_LIMIT,
    max_offset: int = MAX_OFFSET,
) -> list[dict]:
    """
    Читает страницы offset=0,100,... пока:
      - страница короче limit,
      - на странице нет несохранённых сообщений (если передан is_saved),
      - offset > max_offset.
    """
    results: list[dict] = []
    offset = 0
    while offset <= max_offset:
        page = await fetch_page(offset=offset, limit=limit)
        results.extend(page)
        if len(page) < limit:
            break
        if is_saved is not None and not any(not is_saved(m) for m in page):
            break
        offset += limit
    return results