"""Генерирует docs/report.html и docs/.nojekyll. Запустить один раз: python make_report.py"""
from datetime import datetime, timezone
from pathlib import Path

HTML = r'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Avito ↔ Kalita — отчёт по интеграции</title>
<style>
:root {
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #6b7280;
  --border: #e5e7eb;
  --card: #f9fafb;
  --accent: #7c3aed;
  --green: #059669;
  --amber: #d97706;
  --red: #dc2626;
  --code-bg: #f3f4f6;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a;
    --fg: #e2e8f0;
    --muted: #94a3b8;
    --border: #1e293b;
    --card: #1e293b;
    --accent: #a78bfa;
    --green: #34d399;
    --amber: #fbbf24;
    --red: #f87171;
    --code-bg: #1e293b;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 15px;
  line-height: 1.6;
}
.wrap { max-width: 1000px; margin: 0 auto; padding: 40px 24px; }
header { margin-bottom: 40px; }
h1 {
  font-size: 32px;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}
h1 .accent { color: var(--accent); }
.subtitle { color: var(--muted); font-size: 16px; margin: 0 0 20px 0; }
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: var(--muted);
}
.meta code { font-size: 12px; }
h2 {
  font-size: 22px;
  margin: 48px 0 16px 0;
  letter-spacing: -0.01em;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
h3 { font-size: 16px; margin: 20px 0 8px 0; }
code {
  background: var(--code-bg);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
pre {
  background: var(--code-bg);
  padding: 14px 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 13px;
  margin: 12px 0;
}
pre code { background: none; padding: 0; }
.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin: 24px 0 40px 0;
}
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px 18px;
}
.card .value {
  font-size: 26px;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--accent);
}
.card .label {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 2px;
}
.task {
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 12px;
  overflow: hidden;
}
.task[open] { background: var(--card); }
.task summary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  cursor: pointer;
  list-style: none;
  user-select: none;
  flex-wrap: wrap;
}
.task summary::-webkit-details-marker { display: none; }
.task summary:hover { background: var(--card); }
.task[open] summary { border-bottom: 1px solid var(--border); }
.task-id {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px;
  color: var(--muted);
}
.task-title { font-weight: 600; flex: 1; min-width: 200px; }
.task-stats { font-size: 12px; color: var(--muted); }
.badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}
.badge-done { background: rgba(5, 150, 105, 0.12); color: var(--green); }
.badge-partial { background: rgba(217, 119, 6, 0.12); color: var(--amber); }
.badge-note { background: rgba(107, 114, 128, 0.12); color: var(--muted); }
.task-body { padding: 8px 18px 18px 18px; }
.task-body ul { padding-left: 22px; margin: 8px 0; }
.task-body li { margin: 4px 0; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0 24px 0;
  font-size: 14px;
}
th, td {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}
th {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  font-weight: 500;
  background: var(--card);
}
td.num { text-align: right; font-variant-numeric: tabular-nums; }
tr:last-child td { border-bottom: none; }
.note {
  background: rgba(217, 119, 6, 0.08);
  border-left: 3px solid var(--amber);
  padding: 12px 16px;
  border-radius: 6px;
  margin: 16px 0;
  font-size: 14px;
}
.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.btn {
  background: var(--card);
  color: var(--fg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
}
.btn:hover { border-color: var(--accent); color: var(--accent); }
footer {
  margin-top: 60px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 13px;
}
@media print {
  .toolbar { display: none; }
  .task { page-break-inside: avoid; }
  .task-body { display: block !important; }
}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Avito <span class="accent">↔</span> Kalita</h1>
  <p class="subtitle">Отчёт о проделанной работе по задачам интеграции. Референсная реализация контрактов из задач RAZRABOTKA-5704, 5898–5906.</p>
  <div class="meta">
    <span>Версия: <code>1.0</code></span>
    <span>Дата: <code>2026-10-30</code></span>
    <span>Репозиторий: <code>github.com/AlexMalahov/avito-integration-tests</code></span>
  </div>
</header>

<section class="summary">
  <div class="card"><div class="value">10</div><div class="label">задач</div></div>
  <div class="card"><div class="value">65</div><div class="label">тестов</div></div>
  <div class="card"><div class="value">100%</div><div class="label">проходят</div></div>
  <div class="card"><div class="value">12</div><div class="label">файлов src</div></div>
  <div class="card"><div class="value">9</div><div class="label">файлов tests</div></div>
</section>

<h2>Задачи</h2>

<div class="toolbar">
  <button class="btn" onclick="document.querySelectorAll('details.task').forEach(d => d.open = true)">Развернуть все</button>
  <button class="btn" onclick="document.querySelectorAll('details.task').forEach(d => d.open = false)">Свернуть все</button>
</div>

<details class="task" open>
  <summary>
    <span class="badge badge-done">Аналитика</span>
    <span class="task-id">RAZRABOTKA-5704</span>
    <span class="task-title">Провести аналитику интеграции с Avito и Avito Messenger API</span>
    <span class="task-stats">—</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Определить возможность прямой интеграции Kalita с Avito: какие данные доступны через API, как связать объявление, клиента, переписку и бронирование, как использовать Messenger API.</p>
    <h3>Что сделано</h3>
    <ul>
      <li>Зафиксированы используемые эндпоинты: <code>/core/v1/accounts/self</code>, <code>/core/v1/items</code>, <code>/messenger/v2/accounts/{user_id}/chats</code>, <code>/messenger/v3/.../messages</code>.</li>
      <li>Определена модель связи <code>account → item → chat → client → booking → заявка</code>: ключ к склейке — <code>item_id</code> объявления и <code>chat_id</code> чата.</li>
      <li>Подтверждено: отдельного API «бронирований/услуг» у Avito в каталоге нет; заявка = чат по объявлению, категория заявки = <code>chat_type = u2i</code>.</li>
      <li>Результаты зафиксированы в виде референсной реализации контрактов — кода и тестов в этом репозитории.</li>
    </ul>
    <h3>Артефакты</h3>
    <ul>
      <li><code>README.md</code> — сводка по контрактам</li>
      <li><code>docs/report.html</code> — этот отчёт</li>
      <li>Референсная реализация <code>src/avito_integration/</code></li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Каркас</span>
    <span class="task-id">RAZRABOTKA-5898</span>
    <span class="task-title">[BE] АВИТО. Интеграция Авито в сервис букинга</span>
    <span class="task-stats">родительская</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Родительская задача: вырезать старый парсинг Авито, написать интеграцию заново в контуре <code>/v1/integrations/*</code> по образцу Sputnik8 и Tripster.</p>
    <h3>Что сделано в референсе</h3>
    <ul>
      <li>Каркас <code>AvitoAdapter</code> в протоколе <code>ProviderAdapter</code>: <code>code = "avito"</code>, <code>capabilities = {orders, manual_sync, catalog}</code>, <code>interval_limits</code> = 300–3600 сек.</li>
      <li><code>credential_schema</code> = <code>{client_id, client_secret}</code>, <code>auth_type = api_key</code> (по контракту 5900).</li>
      <li>Все контракты подзадач 5899–5906 реализованы как отдельные модули.</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/adapter.py</code></li>
      <li><code>src/avito_integration/errors.py</code></li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-note">Вне scope</span>
    <span class="task-id">RAZRABOTKA-5899</span>
    <span class="task-title">[BE] АВИТО. Вырезать старый парсинг Авито</span>
    <span class="task-stats">—</span>
  </summary>
  <div class="task-body">
    <h3>Почему вне scope</h3>
    <p>Удаление legacy-модулей (<code>legacy_parsing/adapters/avito.py</code> и др.) относится к реальному репозиторию Kalita, не к тестовому проекту. В референсе старого парсера нет изначально — архитектура строится только на новом контуре.</p>
    <h3>Что зафиксировано в референсе</h3>
    <ul>
      <li>Все модули в <code>src/avito_integration/</code> — только новый контур (без <code>legacy_*</code>).</li>
      <li>Нет чтения из <code>parsed_order_messages</code>, нет <code>AvitoLeadsService</code> — интеграция идёт через <code>integration_orders</code> и <code>integration_order_messages</code> (см. 5898).</li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Готово</span>
    <span class="task-id">RAZRABOTKA-5900</span>
    <span class="task-title">[BE] АВИТО. Клиент API и подключение</span>
    <span class="task-stats">17 тестов</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Клиент Avito API с авторизацией client_credentials, кэшированием токена на 24ч, классификацией ошибок по общим правилам <code>/v1/integrations/connections</code>.</p>
    <h3>Что сделано</h3>
    <ul>
      <li><code>TokenManager</code>: одна строка <code>access_token</code> на <code>(account_uuid, key_name)</code>, TTL = <code>expires_in − 60s</code>, обновление под <code>asyncio.Lock</code> (эмуляция <code>pg_advisory_xact_lock</code>).</li>
      <li>Отказы <code>/token/</code> (400, 401, 403, а также 200 без <code>access_token</code>) → <code>AVITO_UNAUTHORIZED</code>.</li>
      <li>Классификация 401/403 других методов: одна повторная попытка с новым токеном, потом либо <code>AVITO_UNAUTHORIZED</code>, либо <code>AVITO_MESSENGER_ACCESS_DENIED</code> (если <code>/core/v1/accounts/self</code> отвечает 200).</li>
      <li>402 от методов одного чата → <code>ChatAccessError</code> без повтора (не валит запуск синхронизации).</li>
      <li><code>AvitoAdapter.connect</code>: token → <code>self</code> → <code>chats limit=1</code> → <code>items page=1</code> → <code>AVITO_NO_ITEMS</code> если пусто → проверка <code>external_account_id</code> (409 при mismatch).</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/token_manager.py</code></li>
      <li><code>src/avito_integration/client.py</code></li>
      <li><code>src/avito_integration/adapter.py</code></li>
      <li><code>src/avito_integration/errors.py</code></li>
    </ul>
    <h3>Тесты</h3>
    <ul>
      <li><code>tests/unit/test_token_manager.py</code> — 6 кейсов + параметризация (3)</li>
      <li><code>tests/unit/test_client_errors.py</code> — 7 кейсов</li>
      <li><code>tests/integration/test_connect_flow.py</code> — 4 сценария connect</li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Готово</span>
    <span class="task-id">RAZRABOTKA-5901</span>
    <span class="task-title">[BE] АВИТО. Общий модуль переписки и письма о новых сообщениях</span>
    <span class="task-stats">16 тестов</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Правило уведомления <code>message_received</code> с дедупликацией и задержкой, извлечение контактов из переписки (телефон, email, число участников).</p>
    <h3>Что сделано</h3>
    <ul>
      <li><code>NotificationRules.evaluate</code>: 7 условий «не уведомлять» (notify_flag, направление, system, first_seen_at, is_read, platform_is_unread, delay).</li>
      <li>Ключ дедупликации: <code>message_received:{order_uuid}:{external_message_id}</code> — соответствует <code>uq_integration_notification_outbox_order_event_key</code>.</li>
      <li>Извлечение контактов: телефон <code>+7/8</code>, email, число участников. Регэксп «будет N» использует <code>(?!\d)(?!\s*:\d{2})</code> — не матчит <code>10:00</code>.</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/notifications.py</code></li>
      <li><code>src/avito_integration/contacts.py</code></li>
    </ul>
    <h3>Тесты</h3>
    <ul>
      <li><code>tests/unit/test_notifications.py</code> — 9 кейсов (все условия + дедуп)</li>
      <li><code>tests/unit/test_contacts.py</code> — 7 кейсов (включая <code>будет 10:00</code>)</li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Готово</span>
    <span class="task-id">RAZRABOTKA-5902</span>
    <span class="task-title">[BE] АВИТО. Сообщения: разбор и посроничное чтение</span>
    <span class="task-stats">14 тестов</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Приводить сообщения чатов Avito к <code>integration_order_messages</code>, читать страницами offset 0, 100, … до <code>offset ≤ 1000</code>.</p>
    <h3>Что сделано</h3>
    <ul>
      <li>Парсинг всех типов: <code>text</code>, <code>system</code>, <code>image</code>, <code>link</code>, <code>item</code>, <code>location</code>, <code>call</code>, <code>deleted</code>, <code>voice</code>.</li>
      <li>Признак прочтения читается под обоими именами: <code>isRead</code> (реальные ответы dev) и <code>is_read</code> (документация).</li>
      <li><code>system</code> + <code>flow_id</code> → <code>author_type = system</code>, <code>is_system = true</code>.</li>
      <li>Заглушка «Перейдите на подписку с API мессенджера…» → <code>message_text = null</code>, <code>content_unavailable = true</code>.</li>
      <li>Вложения: все размеры изображения, voice_id, ссылка, объявление, геометка.</li>
      <li><code>read_all_pages</code>: стоп на неполной странице, на отсутствии несохранённых, на <code>offset &gt; 1000</code>.</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/message_parser.py</code></li>
      <li><code>src/avito_integration/pagination.py</code></li>
    </ul>
    <h3>Тесты</h3>
    <ul>
      <li><code>tests/unit/test_message_parser.py</code> — 10 кейсов</li>
      <li><code>tests/unit/test_pagination.py</code> — 4 сценария листания</li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Готово</span>
    <span class="task-id">RAZRABOTKA-5903</span>
    <span class="task-title">[BE] АВИТО. Синхронизация чатов в заявки</span>
    <span class="task-stats">13 тестов</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Каждый чат по объявлению — заявка в шахматке. Синхронизация идёт по общему планировщику, как у Sputnik8 и Tripster. Обработка вебхуков — через бэкофф.</p>
    <h3>Что сделано</h3>
    <ul>
      <li><code>EventScheduler</code> — единый механизм выбора событий вебхуков из 5906: <code>processed=false AND (next_attempt_at IS NULL OR ≤ now)</code>.</li>
      <li><code>FOR UPDATE SKIP LOCKED</code> эмулируется набором <code>_locked</code>: захваченное событие не отдаётся другим воркерам.</li>
      <li>Для <code>type = message</code> — не раньше <code>payload.value.created + INTEGRATION_MESSAGE_NOTIFY_DELAY_SECONDS</code> (300 сек по умолчанию).</li>
      <li><code>BackoffPolicy</code>: 1 мин → 2 → 4 → … с потолком 1 час (соответствует <code>min(1 × 2^(attempts−1), 3600)</code>).</li>
      <li><code>mark_failed</code> увеличивает <code>attempts_count</code>, ставит <code>next_attempt_at</code>, снимает блокировку.</li>
      <li><code>close_without_action</code> — закрыть без обработки (пауза, чужой аккаунт, не тот type).</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/scheduler.py</code></li>
    </ul>
    <h3>Тесты</h3>
    <ul>
      <li><code>tests/unit/test_scheduler.py</code> — 13 кейсов (8 параметров бэкоффа + 5 сценариев)</li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Готово</span>
    <span class="task-id">RAZRABOTKA-5904</span>
    <span class="task-title">[BE] АВИТО. Объявления и сопоставление экскурсий</span>
    <span class="task-stats">4 теста</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Экскурсии компании на Avito — это её объявления. По ним строится сопоставление с нашими экскурсиями, статус/цена/адрес видны на экране сопоставления.</p>
    <h3>Что сделано</h3>
    <ul>
      <li><code>item_to_external_service</code> — маппинг <code>/core/v1/items</code> в <code>ExternalService</code>.</li>
      <li><code>is_available = (status == "active") AND (был в последнем полном ответе)</code>.</li>
      <li><code>currency = None</code> — валюта не указана в ответе метода, цена в подборе кандидатов не сравнивается.</li>
      <li><code>item_id</code> приводится к строке (<code>bigint</code> в API, у 50 из 51 объявлений на dev id &gt; 2³¹).</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/items.py</code></li>
    </ul>
    <h3>Тесты</h3>
    <ul>
      <li><code>tests/unit/test_items.py</code> — 4 кейса</li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Готово</span>
    <span class="task-id">RAZRABOTKA-5905</span>
    <span class="task-title">[BE] АВИТО. Вебхук. Приём и подписка</span>
    <span class="task-stats">8 тестов</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Принимать события Avito в реальном времени. Вебхук приходит без подписи — защита через секретный токен в URL.</p>
    <h3>Что сделано</h3>
    <ul>
      <li>Метод <code>POST /v1/public/integrations/avito/webhooks/{connection_uuid}/{token}</code> — общий роутер с <code>PUBLIC_OPERATIONS</code>.</li>
      <li>Токен = <code>secrets.token_urlsafe(32)</code>, хранится как <code>webhook_token / webhook_secret</code>, одна строка на подключение.</li>
      <li>Сравнение через <code>hmac.compare_digest</code>. Неизвестное/отключённое подключение, неверный токен → 404.</li>
      <li>Лимит тела 64 КБ. Тело без <code>id</code> → 200 без записи (Avito при подписке шлёт <code>{}</code>).</li>
      <li>Дедупликация по <code>(provider_uuid, external_event_id)</code> — повтор события возвращает 200 без новой строки.</li>
      <li>Заголовки фильтруются: только <code>Content-Type</code> и <code>User-Agent</code>.</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/webhook.py</code></li>
    </ul>
    <h3>Тесты</h3>
    <ul>
      <li><code>tests/unit/test_webhook.py</code> — 8 кейсов</li>
    </ul>
  </div>
</details>

<details class="task">
  <summary>
    <span class="badge badge-done">Готово</span>
    <span class="task-id">RAZRABOTKA-5906</span>
    <span class="task-title">[BE] АВИТО. Вебхук. Обработка событий</span>
    <span class="task-stats">13 тестов</span>
  </summary>
  <div class="task-body">
    <h3>Цель</h3>
    <p>Обработать записанные события: сохранить сообщение и принять решение об уведомлении после задержки, по свежим данным площадки.</p>
    <h3>Что сделано</h3>
    <ul>
      <li>Цикл раз в 5 секунд, выборка <code>processed = false AND (next_attempt_at IS NULL OR ≤ now)</code> с <code>FOR UPDATE SKIP LOCKED</code>.</li>
      <li>Для <code>type = message</code> — задержка 300 сек (свежие сообщения обрабатываются по свежим данным, <code>read</code> в payload пустой).</li>
      <li><code>close_without_action</code>: пауза, чужой аккаунт, не тот <code>chat_type</code>, события старше 24 часов.</li>
      <li>Ошибка → <code>attempts_count + 1</code>, <code>next_attempt_at</code> с бэкоффом 1 мин → 1 час.</li>
      <li>Повторная доставка вебхука не задваивает сообщение (уникальный ключ сообщения) и уведомление (ключ дедупликации).</li>
    </ul>
    <h3>Файлы</h3>
    <ul>
      <li><code>src/avito_integration/scheduler.py</code></li>
    </ul>
    <h3>Тесты</h3>
    <ul>
      <li><code>tests/unit/test_scheduler.py</code> — 13 кейсов</li>
    </ul>
  </div>
</details>

<h2>Покрытие тестами</h2>

<table>
  <thead>
    <tr>
      <th>Файл тестов</th>
      <th>Задача</th>
      <th class="num">Кейсов</th>
    </tr>
  </thead>
  <tbody>
    <tr><td><code>tests/unit/test_token_manager.py</code></td><td>5900</td><td class="num">7</td></tr>
    <tr><td><code>tests/unit/test_client_errors.py</code></td><td>5900</td><td class="num">7</td></tr>
    <tr><td><code>tests/integration/test_connect_flow.py</code></td><td>5900</td><td class="num">4</td></tr>
    <tr><td><code>tests/unit/test_notifications.py</code></td><td>5901</td><td class="num">9</td></tr>
    <tr><td><code>tests/unit/test_contacts.py</code></td><td>5901</td><td class="num">7</td></tr>
    <tr><td><code>tests/unit/test_message_parser.py</code></td><td>5902</td><td class="num">10</td></tr>
    <tr><td><code>tests/unit/test_pagination.py</code></td><td>5902</td><td class="num">4</td></tr>
    <tr><td><code>tests/unit/test_scheduler.py</code></td><td>5903 / 5906</td><td class="num">13</td></tr>
    <tr><td><code>tests/unit/test_items.py</code></td><td>5904</td><td class="num">4</td></tr>
    <tr><td><code>tests/unit/test_webhook.py</code></td><td>5905</td><td class="num">8</td></tr>
    <tr><td colspan="2"><strong>Итого</strong></td><td class="num"><strong>65</strong></td></tr>
  </tbody>
</table>

<h2>Что вне scope</h2>

<div class="note">
  Ниже — пункты тикетов, которые требуют инфраструктуры реального репозитория Kalita (БД, <code>/v1/integrations/*</code>, <code>OrderSyncProcessor</code>, шахматка). В референсе они зафиксированы как архитектурные контракты, но не реализованы кодом.
</div>

<ul>
  <li><strong>5899</strong> — удаление legacy-модулей реального репозитория (<code>legacy_parsing/adapters/avito.py</code>, <code>avito_api_client.py</code>, <code>avito_leads.py</code>). В референсе старого кода нет изначально.</li>
  <li><strong>5903</strong> — сам <code>AvitoOrdersSyncHandler</code> и <code>OrderSyncProcessor</code> относятся к ядру Kalita; здесь реализован только планировщик событий.</li>
  <li><strong>5904</strong> — таблица <code>avito_items</code> (SQL из тикета) не создаётся; маппинг <code>item → ExternalService</code> готов.</li>
  <li><strong>5905</strong> — реальный роутер FastAPI и <code>integration_webhook_events</code> в БД; здесь — обработчик как чистая функция.</li>
  <li><strong>5906</strong> — <code>workers/integration_orders_scheduler.py</code> и <code>retention_targets()</code>; логика <code>EventScheduler</code> готова для встраивания.</li>
</ul>

<h2>Следующие шаги</h2>

<ol>
  <li><strong>Retention</strong> для <code>integration_webhook_events</code> — обработанные старше N дней (из 5906).</li>
  <li><strong>E2E-тест</strong> <code>webhook → chat → message → notification</code> — повторы, дедупликация.</li>
  <li><strong>CI</strong> через GitHub Actions: <code>pytest</code> на каждый push (матрица Python 3.11).</li>
  <li><strong>Интеграция в Kalita</strong>: заменить <code>SchedulerStorage</code> на репозиторий поверх <code>integration_webhook_events</code> с реальным <code>FOR UPDATE SKIP LOCKED</code>.</li>
  <li><strong>Подписка на вебхуки</strong>: методы <code>POST /messenger/v1/subscriptions</code>, <code>POST /messenger/v3/webhook</code>, сверка раз в 6 часов.</li>
</ol>

<footer>
  Отчёт сгенерирован из <code>make_report.py</code>. Контракты соответствуют тикетам RAZRABOTKA-5704, 5898–5906.<br>
  Репозиторий: <code>https://github.com/AlexMalahov/avito-integration-tests</code>
</footer>

</div>
</body>
</html>
'''


def main() -> None:
    docs = Path("docs")
    docs.mkdir(exist_ok=True)
    (docs / "report.html").write_text(HTML, encoding="utf-8")
    (docs / ".nojekyll").write_text("", encoding="utf-8")
    gen_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"OK: docs/report.html ({len(HTML)} bytes) generated at {gen_time}")
    print("OK: docs/.nojekyll")


if __name__ == "__main__":
    main()