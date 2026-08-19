# Backend сайта: FastAPI + uvicorn.
FROM python:3.12-slim

# curl нужен scripts/scrape_adilet.py: adilet.zan.kz отдаёт неполную цепочку
# TLS-сертификатов, и httpx с ней не справляется, а curl — справляется.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts

# Не root: если кто-то пробьётся через приложение, у него не будет прав в контейнере.
RUN useradd --create-home --uid 10001 rst && chown -R rst:rst /app
USER rst

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
