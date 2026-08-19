# Telegram-бот (aiogram, long polling — входящие порты не нужны).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram_bot/ ./

# Тот же uid, что у backend: оба контейнера пишут в общий каталог data
# (банк вопросов rst.db правит и бот, и скрипт перегенерации дистракторов),
# поэтому одного `chown -R 10001:10001 data` на хосте достаточно для обоих.
RUN useradd --create-home --uid 10001 rst && chown -R rst:rst /app
USER rst

CMD ["python", "bot.py"]
