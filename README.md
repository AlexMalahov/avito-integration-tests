# Avito ↔ Kalita — автотесты интеграции

Проект содержит минимальную референсную реализацию контрактов из задач
RAZRABOTKA-5704, 5898–5906 и полный набор тестов на `pytest`.

## Что покрыто

* `token_manager` — OAuth client_credentials, TTL, единственная строка `access_token`,
  обработка отказов 400/401/403 и 200 без `access_token` (RAZRABOTKA-5900).
* `client` — классификация ошибок: `AVITO_UNAUTHORIZED`,
  `AVITO_MESSENGER_ACCESS_DENIED`, `ChatAccessError` для 402/403 одного чата,
  повтор с новым токеном (5900).
* `message_parser` — все типы сообщений, camelCase `isRead` и snake_case `is_read`,
  system+flow_id, вложения, заглушка «Перейдите на подписку…» (5902).
* `notifications` — правило уведомления `message_received`, ключ дедупликации,
  задержка, notify_flag, first_seen_at (5901).
* `contacts` — телефон, email, число участников, исключение `будет 10:00`
  (5901, приложение Б).
* `items` — `is_available` = `active` && объявление было в последнем полном ответе
  (5904).
* `pagination` — стоп по неполной странице, по отсутствию несохранённых сообщений,
  по `offset > 1000` (5902).
* `webhook` — токен, лимит 64 КБ, тело без `id` → 200 без записи, дедупликация,
  фильтрация заголовков (5905).
* `adapter.connect` — поток подключения: token → self → chats limit=1 → items →
  проверка `external_account_id` (5900).

## Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                        # весь набор
pytest tests/unit             # только unit
pytest tests/integration      # только integration
pytest -k token_manager       # точечно

Add-Content -Path README.md -Value "`n## Отчёт`n`nПолный отчёт по задачам: [docs/report.html](docs/report.html)`n"