# RST — как запустить всё

Три независимые части проекта: **сайт** (backend + frontend), **Telegram-бот**, **мобильное
приложение**. Каждую запускаете в своём отдельном окне терминала — они должны работать
одновременно, поэтому не закрывайте окно после запуска.

Это про запуск на своём Mac для разработки. Про боевой сервер в интернете — сайт на домене
с HTTPS, работающий круглосуточно — см. [DEPLOY.md](DEPLOY.md).

**Важно:** сначала всегда переходите в папку проекта. Все команды ниже начинаются с этого:

```bash
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST"
```

Если скопируете и вставите её первой строкой в новое окно терминала — дальше все команды
из этого файла будут работать. Не копируйте строки с `#` (это просто пояснения, не команды).

---

## Сначала проверьте — может, уже запущено

Если ошибка вида `Address already in use` — значит эта часть уже работает, второй раз
запускать не нужно. Проверить, что уже крутится:

```bash
ps aux | grep -E "uvicorn|expo start|vite" | grep -v grep
```

Если в списке есть строки про `uvicorn`, `expo start` или `vite` — соответствующая часть уже
запущена, просто откройте сайт/приложение. Ниже — как остановить, если нужно перезапустить:

```bash
pkill -f "uvicorn app.main"     # остановить backend сайта
pkill -f "expo start"           # остановить мобильное приложение
pkill -f "vite"                 # остановить сайт (frontend)
```

---

## 1. Сайт

Два процесса: backend (сервер) и frontend (то, что открывается в браузере). Нужны оба.

### Backend

```bash
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST/website/backend"
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Это окно терминала теперь занято сервером — не закрывайте его, откройте новое окно для
следующих шагов (⌘+T в Терминале — новая вкладка).

### Frontend

```bash
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST/website/frontend"
npm run dev
```

Сайт откроется на `http://localhost:5173`.

---

## 2. Telegram-бот

Отдельное окно терминала:

```bash
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST/telegram_bot"
source ../.venv/bin/activate
python bot.py
```

---

## 3. Мобильное приложение

Backend (пункт 1) должен уже работать. Отдельное окно терминала:

```bash
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST/mobile"
npx expo start --lan --web
```

В терминале появится QR-код. Дальше на телефоне (в той же Wi-Fi сети, что Mac):

- **Через приложение Expo Go** (бесплатно, App Store / Google Play) — отсканируйте QR-код.
- **Или прямо в браузере телефона** (если Expo Go пишет "incompatible") — откройте в Safari/
  Chrome на телефоне адрес, который покажет команда `ipconfig getifaddr en0`, с портом 8081,
  например `http://192.168.100.64:8081` (IP у вас может быть другой — посмотрите свежий).

Если IP Mac изменился с прошлого раза — обновите его в файле
`mobile/.env` (строка `EXPO_PUBLIC_API_URL=...`) и перезапустите `expo start`.

Это про разработку. Про настоящую сборку приложения для App Store и Google Play (через EAS,
в облаке Expo) — [mobile/README.md](mobile/README.md).

---

## Если что-то не заработало с первого раза (первая установка на новом Mac)

Эти шаги нужны **только один раз**, когда ставите проект впервые (venv/node_modules уже
созданы на этом Mac, так что обычно это уже не требуется):

```bash
# backend сайта
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST/website/backend"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/import_questions.py

# frontend сайта
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST/website/frontend"
npm install

# мобильное приложение
cd "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST/mobile"
npm install
```

---

## Частые проблемы

- **`Address already in use`** — эта часть уже запущена, см. раздел выше "проверьте, может
  уже запущено". Второй раз поднимать не нужно.
- **`no such file or directory`** — вы не в папке проекта. Сначала `cd
  "/Users/sairanbek/Desktop/ПРОЕКТЫ/RST"`, дальше по инструкции.
- **Мобильное приложение / сайт не подключается к серверу** — backend должен быть запущен
  именно с `--host 0.0.0.0` (как в инструкции), не просто `uvicorn app.main:app`.
- **Бот не отвечает** — проверьте, что окно с `python bot.py` не закрылось и не показывает
  ошибку.
- **Письма (сброс пароля) не приходят** — у Gmail лимит ~500 писем/день.
