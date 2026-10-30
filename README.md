# Avito ↔ Kalita — автотесты интеграции

Референсная реализация контрактов из задач RAZRABOTKA-5704, 5898–5906 и полный набор тестов на `pytest`.

📊 **[Отчёт по проделанной работе (HTML)](docs/report.html)** — сводка по 10 задачам, покрытие тестами, что реализовано и что вне scope.

## Что покрыто

| Задача | Модуль | Тесты |
|---|---|---|
| **5900** Клиент API и подключение | `token_manager.py`, `client.py`, `adapter.py`, `errors.py` | 18 |
| **5901** Правило уведомления и контакты | `notifications.py`, `contacts.py` | 16 |
| **5902** Парсинг сообщений и листание | `message_parser.py`, `pagination.py` | 14 |
| **5903 / 5906** Планировщик вебхуков | `scheduler.py` | 13 |
| **5904** Объявления и маппинг | `items.py` | 4 |
| **5905** Приём вебхука | `webhook.py` | 8 |
| **Итого** | 12 модулей | **65** |

### 5900 — Клиент API и подключение

- OAuth `client_credentials`, TTL = `expires_in − 60s`, одна строка `access_token` на `(account_uuid, key_name)`.
- Классификация ошибок: `AVITO_UNAUTHORIZED`, `AVITO_MESSENGER_ACCESS_DENIED`, `AVITO_NO_ITEMS`, `AVITO_ACCOUNT_MISMATCH`.
- `ChatAccessError` для 402/403 одного чата — не валит запуск синхронизации.
- Повтор с новым токеном при 401/403; проверка через `/core/v1/accounts/self`.
- `connect`: token → self → chats `limit=1` → items `page=1` → проверка `external_account_id`.

### 5901 — Правило уведомления и контакты

- `NotificationRules.evaluate`: 7 условий «не уведомлять» (notify_flag, направление, system, first_seen_at, is_read, platform_is_unread, delay 300s).
- Ключ дедупликации: `message_received:{order_uuid}:{external_message_id}`.
- Извлечение контактов: телефон, email, число участников. Регэксп «будет N» не матчит `10:00`.

### 5902 — Парсинг сообщений и листание

- Типы: `text`, `system`, `image`, `link`, `item`, `location`, `call`, `deleted`, `voice`.
- Признак прочтения: `isRead` (dev) и `is_read` (документация).
- `system` + `flow_id` → `author_type = system`.
- Заглушка «Перейдите на подписку…» → `content_unavailable = true`.
- `read_all_pages`: стоп на неполной странице, на отсутствии несохранённых, на `offset > 1000`.

### 5903 / 5906 — Планировщик вебхуков

- `EventScheduler`: `processed=false AND (next_attempt_at IS NULL OR ≤ now)`.
- `FOR UPDATE SKIP LOCKED` (эмуляция через `_locked`).
- Для `type = message` — не раньше `payload.value.created + 300s`.
- `BackoffPolicy`: 1 мин → 2 → 4 → … → 3600s.
- `mark_processed`, `mark_failed`, `close_without_action`.

### 5904 — Объявления и маппинг

- `item_to_external_service` → `ExternalService`.
- `is_available = (status == "active") AND (был в последнем полном ответе)`.
- `currency = None` — валюта не указана в ответе `/core/v1/items`.
- `item_id` приводится к строке (`bigint`, у 50 из 51 объявления на dev id > 2³¹).

### 5905 — Приём вебхука

- Токен `secrets.token_urlsafe(32)`, сравнение через `hmac.compare_digest`, ошибки → 404.
- Лимит тела 64 КБ. Тело без `id` → 200 без записи.
- Дедупликация по `(provider_uuid, external_event_id)`.
- Заголовки фильтруются: только `Content-Type` и `User-Agent`.

## Вне scope

Контракты зафиксированы в коде и тестах, но полноценная реализация требует инфраструктуры реального репозитория Kalita (БД, `/v1/integrations/*`, `OrderSyncProcessor`, шахматка):

- **5899** — удаление legacy-модулей (`legacy_parsing/adapters/avito.py` и др.).
- **5903** — сам `AvitoOrdersSyncHandler` и `OrderSyncProcessor`.
- **5904** — таблица `avito_items` (SQL из тикета).
- **5905** — реальный роутер FastAPI и таблица `integration_webhook_events` в БД.
- **5906** — `workers/integration_orders_scheduler.py` и `retention_targets()`.

## Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

pytest                            # весь набор (65 тестов)
pytest tests/unit                 # только юнит-тесты
pytest tests/integration          # сценарные тесты connect
pytest -k scheduler               # точечно по имени
pytest -v                         # подробный вывод