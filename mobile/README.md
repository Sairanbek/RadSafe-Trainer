# RST — Мобильное приложение (Android + iOS)

React Native + Expo (managed workflow), тот же backend API, что и у сайта (`website/backend`).
Админ-панель не портирована — она веб-only.

## Запуск (разработка)

```bash
# backend должен слушать на всех интерфейсах, не только localhost
cd website/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# в отдельном терминале
cd mobile
npm install
cp .env.example .env   # укажите LAN-адрес Mac, см. `ipconfig getifaddr en0`
npx expo start --lan
```

Телефон и компьютер должны быть в одной Wi-Fi сети. Установите бесплатное приложение
**Expo Go** (App Store / Google Play), затем:
- отсканируйте QR-код из терминала, или
- в Expo Go выберите "Enter URL manually" и введите `exp://<LAN-IP>:8081`.

### Если Expo Go несовместим ("Project is incompatible with this version of Expo Go")

Такое бывает, если на телефоне установлена старая версия Expo Go, а обновления в App Store/
Google Play нет (например, из-за старой версии ОС). В этом случае не нужен Expo Go вообще —
запустите `npx expo start --lan --web` и откройте `http://<LAN-IP>:8081` прямо в браузере на
телефоне (Safari/Chrome). Работает идентично, без установки приложения. Не забудьте добавить
этот адрес (`http://<LAN-IP>:8081`) в `CORS_ORIGINS` в `website/backend/.env` — в отличие от
нативного Expo Go, браузер шлёт заголовок Origin, и без этого backend отклонит запросы.

## Сборка для публикации

Сейчас проект в managed-режиме без нативных билдов — для реальной публикации в App Store /
Google Play понадобится `eas build` (аккаунт Expo, для iOS — членство в Apple Developer
Program). Пока не требуется: рабочий MVP тестируется через Expo Go.
