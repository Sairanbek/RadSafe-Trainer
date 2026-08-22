# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## О проекте

RST (RadSafe Trainer) — тренажёр подготовки к аттестации по радиационной безопасности в
Казахстане. Три независимых клиента поверх одного банка вопросов: Telegram-бот, сайт
(FastAPI + React), мобильное приложение (Expo/React Native).

Весь UI, документация и комментарии в коде — на русском. Пишите новые комментарии,
тексты ошибок и сообщения пользователю тоже по-русски.

## Ключевая архитектурная особенность: два независимых стека

`telegram_bot/` и `website/backend/` — **не общий код**, а две отдельные реализации одной
предметной логики:

- **Бот**: сырой `sqlite3` + свои SQL-запросы (`telegram_bot/database/`), состояние теста
  в памяти процесса (`user_state` в `handlers/test.py`), пользователи — Telegram ID,
  база `telegram_bot/rst.db`.
- **Сайт**: SQLAlchemy 2.0 (`Mapped[...]`), состояние теста в таблице `test_sessions`
  (чтобы переживать перезапуск), пользователи — email + пароль, база
  `website/backend/rst_web.db`.

`website/backend/app/logic.py` — это порт логики из `telegram_bot/handlers/test.py`.
Меняя правила тестирования (длина сессии, порог 70%, перемешивание вариантов, учёт ошибок),
проверяйте, нужно ли синхронное изменение во втором стеке.

### Направления подготовки (module)

Банк вопросов больше не один. У `questions` есть колонка `module`, и по ней
фильтруется **всё**: пул вопросов, разделы, подразделы, длина тренировки,
аттестация, статистика, история, «мои ошибки». Направления сейчас:
`Радиационная безопасность` (436), `Радиология` (753), `Госслужба (Корпус Б)`
(1621). Значение по умолчанию — `DEFAULT_MODULE` в `app/models.py`.

Добавляя запрос к `questions`, не забывайте фильтр по `module` — без него
аттестация по радиационной безопасности начнёт подмешивать вопросы про УЗИ
щитовидной железы.

**Названия разделов обязаны быть уникальны по всей базе.** Таблица `stats`
хранит только `(user_id, section)` без направления, поэтому одинаковый раздел
в двух направлениях смешал бы статистику. `import_external_banks.py` проверяет
это и падает с понятной ошибкой при конфликте.

Вопросы внешних банков бывают с 4 вариантами вместо 5 — `wrong4` тогда пустой,
а `build_question` отбрасывает пустые дистракторы. Не рассчитывайте на ровно
пять вариантов.

### Поток данных банка вопросов

Два независимых пути, по одному на происхождение банка.

**Радиационная безопасность:**
`questions/radiation_safety/*.xlsx` → (`telegram_bot/migrate_to_sqlite.py`) →
**`telegram_bot/rst.db` — источник истины** (~436 вопросов) →
(`website/backend/scripts/import_questions.py`, идемпотентно, `INSERT OR REPLACE` по id) →
`website/backend/rst_web.db`.

**Остальные направления:**
`questions/<направление>/questions.json` (уже нормализованные, лежат в репозитории) →
(`website/backend/scripts/import_external_banks.py`, идемпотентно) → `rst_web.db`.
Id вычисляются от начала диапазона направления (радиология с 100 000, госслужба
с 200 000), чтобы не пересечься с банком бота.

Никогда не правьте вопросы напрямую в `rst_web.db` — при следующем импорте изменения
затрутся. Правки идут в `rst.db` (или через админ-панель сайта, понимая, что это односторонний
поток). Обе базы в `.gitignore`.

### Режимы тестирования

`training` | `exam` | `mistakes` | `learning`. `exam` — всегда все разделы, 50 вопросов,
75 минут, порог 70%. `learning` не пишет историю и статистику и единственный отдаёт
`correct_letter` клиенту сразу. Длина тренировки зависит от размера раздела
(`get_training_length` в `logic.py`).

### Аутентификация сайта/мобильного

Короткий access-токен (1 час, JWT HS256) + refresh-токен на 30 дней в базе, **одноразовый с
ротацией**: каждый `/api/auth/refresh` отзывает старый и выдаёт новый. Поэтому параллельные
401-запросы обязаны дожидаться одного и того же refresh — в `website/frontend/src/api/client.ts`
и `mobile/src/api/client.ts` это сделано через общий `refreshPromise`. Не ломайте эту
дедупликацию.

### Миграции

Alembic нет. `run_migrations()` в `website/backend/app/database.py` вызывается на старте и
добирает недостающие колонки из словаря `_NEW_COLUMNS` (`create_all` создаёт только
целиком отсутствующие таблицы). Словарь двухуровневый: таблица → колонка → (тип, чем
заполнить уже существующие строки). Добавляя колонку в существующую модель — дописывайте
её туда, иначе на рабочей базе будет ошибка `no such column`.

### Gemini

`website/backend/app/gemini.py` (сайт) и `telegram_bot/handlers/ai_assistant.py` (бот) —
модель `gemini-flash-latest`, бесплатная квота ~20 запросов в день **на весь проект**, общая
у живого ассистента и офлайн-скриптов генерации дистракторов. Поэтому
`regenerate_distractors.py` по умолчанию работает маленькими порциями. Учитывайте эту квоту,
добавляя новые вызовы. Все AI-эндпоинты требуют согласия пользователя на передачу данных
(`users.consent_ai_transfer_at`) и покрыты rate-limit (`app/rate_limit.py`, slowapi).

## Команды

Три части запускаются в отдельных окнах терминала и работают одновременно. Подробная
инструкция для владельца проекта — в [RUNBOOK.md](RUNBOOK.md).

```bash
# backend сайта (--host 0.0.0.0 обязателен, иначе не подключится мобильное приложение)
cd website/backend && source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000     # http://localhost:8000/docs

# frontend сайта
cd website/frontend && npm run dev                            # http://localhost:5173
npm run build                                                 # tsc -b + vite build = проверка типов
npm run lint                                                  # oxlint (не eslint)

# Telegram-бот (venv в корне проекта, отдельный от backend)
cd telegram_bot && source ../.venv/bin/activate && python bot.py

# мобильное приложение (backend должен быть уже запущен)
cd mobile && npx expo start --lan --web
```

Проверить, что уже запущено, вместо повторного запуска:
`ps aux | grep -E "uvicorn|expo start|vite" | grep -v grep`.

### Скрипты (из `website/backend`, с активированным `.venv`)

```bash
python scripts/import_questions.py                  # rst.db -> rst_web.db, безопасно перезапускать
python scripts/make_admin.py user@example.com       # выдать is_admin (пользователь должен быть зарегистрирован)
python scripts/backup_db.py                         # снимок rst_web.db в backend/backups/, хранит 14 последних
python scripts/regenerate_distractors.py --limit 20 # перегенерация неверных вариантов через Gemini
python scripts/scrape_adilet.py                     # сверка вопросов с первоисточниками на adilet.zan.kz
```

`daily_distractor_job.py` — обёртка для launchd: порция дистракторов + сразу импорт на сайт.

## Тесты

Автотестов в проекте нет — ни pytest, ни vitest, ни CI. `telegram_bot/test_loader.py` —
устаревший скрипт (импортирует удалённый `services.excel_loader`), не тест, запускать его
не нужно. Проверка изменений: `npm run build` во frontend (типы), ручной прогон через UI,
`http://localhost:8000/docs` для API.

## Окружения Python

Три venv в корне (`.venv`, `.venv-1`, `.venv-2`) — все с aiogram; бот использует `.venv`
(Python 3.12), остальные — остатки экспериментов. У backend сайта свой venv
`website/backend/.venv` (fastapi, без aiogram). Зависимости бота — корневой
`requirements.txt`, зависимости сайта — `website/backend/requirements.txt`.

## Мобильное приложение

`mobile/AGENTS.md` требует: **перед написанием кода читать версионированную документацию
Expo для v57** — https://docs.expo.dev/versions/v57.0.0/. API Expo меняется между
мажорными версиями, память о прошлых версиях ненадёжна.

Экраны в `mobile/src/screens/` повторяют страницы сайта из `website/frontend/src/pages/`,
кроме админ-панели — она веб-only. Адрес backend задаётся `EXPO_PUBLIC_API_URL` в `mobile/.env`
и требует обновления при смене LAN-IP Mac (`ipconfig getifaddr en0`). Токены —
`expo-secure-store`, с фоллбэком на `localStorage` в web-режиме (`Platform.OS === "web"`).

## Локальная сеть и CORS

`app/main.py` помимо `CORS_ORIGINS` разрешает регуляркой любой адрес локальной сети
(`localhost`/`127.0.0.1`/`192.168.*`/`10.*` с любым портом) — чтобы CORS не ломался при
каждом новом DHCP-адресе Mac. Frontend без `VITE_API_URL` берёт хост, с которого открыт сайт,
подменяя `localhost` на `127.0.0.1` (localhost может резолвиться в IPv6 и уводить запросы
не туда).

## Секреты и данные

`.env` файлы, обе базы, `website/backend/law_snapshots/` — в `.gitignore`. Порядок действий
при утечке персональных данных (сроки уведомления по правилам РК) — в
[SECURITY_INCIDENT.md](SECURITY_INCIDENT.md).

`scrape_adilet.py` качает страницы через `curl`, а не httpx: adilet.zan.kz отдаёт неполную
цепочку TLS-сертификатов, и Python-библиотеки с этим не справляются. Скрипт никогда не
переписывает вопросы автоматически — только пишет отчёт для проверки человеком, юридическая
точность формулировок требует ручного контроля.
