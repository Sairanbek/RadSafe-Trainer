"""Импортирует банк вопросов из telegram_bot/rst.db в website/backend/rst_web.db.

Идемпотентно: перезаписывает вопросы по id (INSERT OR REPLACE), можно
перезапускать после обновления вопросов у бота.
"""

import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(BACKEND_DIR))

from app import models  # noqa: E402,F401
from app.config import settings  # noqa: E402
from app.database import Base, engine, run_migrations  # noqa: E402
from app.models import DEFAULT_MODULE  # noqa: E402

# Путь к банку вопросов берём из настроек (BOT_DB_PATH) — в контейнере база
# лежит не там, где в локальной раскладке проекта.
BOT_DB = settings.bot_db


def main():
    if not BOT_DB.exists():
        print(f"Не найдена база бота: {BOT_DB}")
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    run_migrations()

    src = sqlite3.connect(BOT_DB)
    src.row_factory = sqlite3.Row
    rows = src.execute(
        "SELECT id, section, subsection, question, answer, wrong1, wrong2, wrong3, wrong4 FROM questions ORDER BY id"
    ).fetchall()
    src.close()

    if not rows:
        print("В базе бота нет вопросов.")
        return

    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.executemany(
            """
            INSERT OR REPLACE INTO questions
                (id, module, section, subsection, question, answer, wrong1, wrong2, wrong3, wrong4)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    r["id"],
                    # Банк бота — только радиационная безопасность; остальные
                    # направления заливает import_external_banks.py.
                    DEFAULT_MODULE,
                    r["section"],
                    r["subsection"] or "Общие вопросы",
                    r["question"],
                    r["answer"],
                    r["wrong1"],
                    r["wrong2"],
                    r["wrong3"],
                    r["wrong4"],
                )
                for r in rows
            ],
        )
        raw.commit()
    finally:
        raw.close()

    print(f"Перенесено вопросов: {len(rows)}")


if __name__ == "__main__":
    main()
