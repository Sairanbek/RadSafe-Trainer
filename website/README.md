# RST — Сайт (Version 2.0)

Веб-версия тренажёра: FastAPI (backend) + React/TypeScript (frontend). Отдельные веб-аккаунты
(email + пароль), общий банк вопросов, синхронизируемый из базы Telegram-бота.

Помимо основного тренажёра (тренировка, аттестация, ошибки, статистика, история) сайт включает:
- **Режим обучения** — правильный ответ виден сразу, без баллов и записи в статистику;
- **Личный кабинет** — смена имени, email, пароля;
- **Восстановление пароля** — по ссылке на email (нужен SMTP, см. ниже);
- **Админ-панель вопросов** (`/admin/questions`) — доступна пользователям с `is_admin=true`.

## Backend

```bash
cd website/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# импорт вопросов из telegram_bot/rst.db (можно перезапускать)
python scripts/import_questions.py

uvicorn app.main:app --reload --port 8000
```

API доступно на `http://localhost:8000`, документация — `http://localhost:8000/docs`.

### Восстановление пароля (SMTP)

В `.env` укажите `SMTP_HOST/PORT/USER/PASSWORD/FROM` и `FRONTEND_URL`. Для Gmail нужен
[App Password](https://myaccount.google.com/apppasswords) (не обычный пароль от аккаунта),
включённая двухфакторная аутентификация. Без этих переменных `/api/auth/forgot-password`
вернёт ошибку при попытке реально отправить письмо.

### Администратор

```bash
python scripts/make_admin.py user@example.com
```

Пользователь должен быть уже зарегистрирован на сайте. После этого ему становится доступна
админ-панель `/admin/questions` (CRUD по банку вопросов).

## Frontend

```bash
cd website/frontend
npm install
cp .env.example .env.local
npm run dev
```

Сайт доступен на `http://localhost:5173`.
