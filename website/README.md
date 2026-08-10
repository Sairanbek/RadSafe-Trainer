# RST — Сайт (Version 2.0)

Веб-версия тренажёра: FastAPI (backend) + React/TypeScript (frontend). Отдельные веб-аккаунты
(email + пароль), общий банк вопросов, синхронизируемый из базы Telegram-бота.

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

## Frontend

```bash
cd website/frontend
npm install
cp .env.example .env.local
npm run dev
```

Сайт доступен на `http://localhost:5173`.
