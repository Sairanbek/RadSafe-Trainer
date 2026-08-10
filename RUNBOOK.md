# RST — как запустить всё

Три независимые части проекта: **сайт** (backend + frontend), **Telegram-бот**, **мобильное
приложение**. Каждую можно запускать отдельно, в своём терминале.

---

## 1. Сайт

### Backend (FastAPI)

```bash
cd website/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Первый раз перед запуском:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # заполните SECRET_KEY, при необходимости SMTP/GEMINI_API_KEY
python scripts/import_questions.py   # заливает банк вопросов из telegram_bot/rst.db
```

API: `http://localhost:8000`, документация: `http://localhost:8000/docs`.

### Frontend (React)

```bash
cd website/frontend
npm install        # только первый раз
npm run dev
```

Сайт: `http://localhost:5173`.

---

## 2. Telegram-бот

```bash
cd telegram_bot
source ../.venv/bin/activate      # общее окружение в корне проекта
python bot.py
```

Если venv в корне (`.venv`) не создан:
```bash
cd /path/to/RST
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`telegram_bot/.env` уже содержит `BOT_TOKEN`, `ADMIN_ID`, `DATABASE_NAME`, `GEMINI_API_KEY`.

---

## 3. Мобильное приложение (Android + iOS)

```bash
# backend должен быть поднят с --host 0.0.0.0 (см. пункт 1)

cd mobile
npm install         # только первый раз
npx expo start --lan --web
```

Узнать текущий IP Mac в локальной сети (меняется между сессиями Wi-Fi):
```bash
ipconfig getifaddr en0
```
Если изменился — обновите `EXPO_PUBLIC_API_URL` в `mobile/.env` на этот IP и перезапустите
`expo start` (backend трогать не надо — CORS уже разрешает любой адрес локальной сети).

**Способ 1 — приложение Expo Go** (App Store / Google Play, бесплатно):
- отсканируйте QR-код из терминала, или
- в Expo Go → "Enter URL manually" → `exp://<LAN-IP>:8081`.

**Способ 2 — прямо в браузере телефона**, если Expo Go несовместим по версии
("Project is incompatible with this version of Expo Go"):
- откройте `http://<LAN-IP>:8081` в Safari/Chrome на телефоне. Ничего ставить не нужно.

Телефон и Mac должны быть в одной Wi-Fi сети.

---

## Частые проблемы

- **Мобильное приложение / сайт не подключается к API** — проверьте, что backend поднят
  именно с `--host 0.0.0.0`, а не просто `uvicorn app.main:app` (тогда он слушает только
  127.0.0.1 и недоступен с телефона).
- **CORS-ошибка в браузере** (не в нативном Expo Go) — backend уже разрешает весь
  `192.168.x.x`/`10.x.x.x` диапазон (`app/main.py`, `allow_origin_regex`). Если всё равно
  ошибка — перезапустите backend, чтобы подхватить актуальный код/`.env`.
- **Бот не отвечает** — проверьте, что процесс `python bot.py` реально запущен и не упал с
  ошибкой в терминале (например, неверный `BOT_TOKEN`).
- **Письма (сброс пароля) не приходят** — Gmail SMTP лимитирован (~500 писем/день), плюс
  нужен App Password, а не обычный пароль от аккаунта (см. `website/README.md`).
