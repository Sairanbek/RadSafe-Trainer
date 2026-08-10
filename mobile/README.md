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

## Сборка для публикации

Сейчас проект в managed-режиме без нативных билдов — для реальной публикации в App Store /
Google Play понадобится `eas build` (аккаунт Expo, для iOS — членство в Apple Developer
Program). Пока не требуется: рабочий MVP тестируется через Expo Go.
