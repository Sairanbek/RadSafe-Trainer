# RST — Мобильное приложение (Android + iOS)

React Native + Expo SDK 57 (managed workflow), тот же backend API, что и у сайта
(`website/backend`). Админ-панель не портирована — она веб-only.

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
Google Play нет (например, из-за старой версии ОС). Два выхода:

1. **Браузер телефона** — запустите `npx expo start --lan --web` и откройте
   `http://<LAN-IP>:8081` в Safari/Chrome на телефоне. Работает идентично, без установки
   приложения. Backend уже разрешает CORS для любого адреса локальной сети
   (`allow_origin_regex` в `app/main.py`).
2. **Собственная сборка для разработки** (development build) — свой аналог Expo Go, собранный
   под этот проект и не зависящий от версии Expo Go в сторе:
   `npm run build:dev:android`. Ставится на телефон один раз, дальше работает с тем же
   `npx expo start`.

---

## Сборка через EAS

Сборка идёт в облаке Expo — Xcode и Android Studio на Mac не нужны. Профили описаны в
[eas.json](eas.json).

| Профиль | Что даёт | Куда ходит за API |
|---|---|---|
| `development` | dev-клиент вместо Expo Go, APK для установки на телефон | `.env` (LAN-адрес Mac) |
| `preview` | обычный APK / IPA для тестирования боевой версии | `EXPO_PUBLIC_API_URL` из `eas.json` |
| `production` | AAB для Google Play, сборка для App Store | `EXPO_PUBLIC_API_URL` из `eas.json` |

### Прежде чем собирать: два обязательных шага

**1. Указать реальный адрес backend.** В `eas.json` в профилях `preview` и `production` стоит
заглушка `https://rst.example.kz` — замените её на свой домен из [DEPLOY.md](../DEPLOY.md).
Нативная сборка **не может** ходить на `localhost` или LAN-адрес Mac: приложение работает на
телефоне вне вашей сети, и адрес должен быть публичным и на HTTPS (iOS блокирует HTTP).

Значение попадает в бинарник на этапе сборки, поэтому после смены домена приложение нужно
пересобрать. Секретов там быть не должно: всё с префиксом `EXPO_PUBLIC_` видно любому, кто
разберёт установленный APK.

**2. Привязать проект к аккаунту Expo:**

```bash
npm install --global eas-cli
eas login
eas init
```

`eas init` создаст проект в вашем аккаунте Expo и допишет `extra.eas.projectId` в `app.json` —
это нормально, изменение нужно закоммитить.

### Собрать

```bash
npm run build:preview:android     # APK — поставить на свой телефон и проверить
npm run build:prod:android        # AAB для Google Play
npm run build:prod:ios            # App Store
```

EAS сам создаст и сохранит подписи: keystore для Android и сертификаты для iOS. **Не теряйте
доступ к аккаунту Expo** — с другим keystore обновить уже опубликованное приложение в Google
Play нельзя.

Отправка в сторы после сборки — `eas submit --platform android` / `--platform ios`
(настройки в блоке `submit` в `eas.json`).

### Версии

- `version` в `app.json` (`1.0.0`) — версия, которую видит пользователь. Повышайте вручную для
  каждого релиза.
- `versionCode` (Android) и `buildNumber` (iOS) EAS ведёт сам: `appVersionSource: "remote"` +
  `autoIncrement` в профиле `production`.
- Идентификатор приложения — `rst.kz` (`android.package` и `ios.bundleIdentifier`). **После
  публикации в сторах его изменить нельзя.** Общепринятый формат — обратный домен (`kz.rst`);
  сейчас стоит прямой, поменять можно только до первой публикации.

### Что понадобится для публикации

- **Google Play** — аккаунт разработчика (разовая оплата), заполненная декларация Data Safety:
  приложение собирает email и имя, а при использовании ИИ-ассистента отправляет текст вопроса
  в Google Gemini (согласие пользователя запрашивается в профиле).
- **App Store** — членство в Apple Developer Program (ежегодная оплата).
- **Ссылка на политику конфиденциальности** — страница `/privacy` на сайте.

---

## Проверки перед сборкой

```bash
npm run typecheck   # tsc --noEmit
npm run doctor      # expo-doctor: версии пакетов и конфигурация
npx expo export --platform android   # локальная проверка, что JS-бандл собирается
```
