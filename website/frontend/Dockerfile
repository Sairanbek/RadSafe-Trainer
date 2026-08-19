# Frontend собирается в статику и отдаётся тем же Caddy, который терминирует
# HTTPS и проксирует /api на backend. Один origin => никакого CORS в проде.
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Пустая строка = запросы идут относительными путями на тот же origin.
# Не убирайте ARG: без него сборка возьмёт фоллбэк http://<host>:8000,
# который под HTTPS даёт mixed content и стучится в закрытый порт.
ARG VITE_API_URL=""
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

FROM caddy:2-alpine
COPY --from=build /app/dist /srv
# Caddyfile не копируем в образ, а монтируем через compose (deploy/Caddyfile) —
# правки конфига и смена домена не требуют пересборки фронтенда.
