from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# check_same_thread — специфика SQLite; для Postgres такой аргумент недопустим,
# поэтому передаём его только когда база действительно SQLite.
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Простая замена Alembic: на старте добираем колонки, которых не хватает в уже
# существующей базе (create_all создаёт только отсутствующие таблицы целиком).
# Добавляя колонку в модель, дописывайте её сюда — иначе на рабочей базе будет
# ошибка "no such column". Третий элемент — чем заполнить строки, которые уже
# лежат в базе (для NOT NULL-колонок это обязательно).
_NEW_COLUMNS: dict[str, dict[str, tuple[str, str | None]]] = {
    "users": {
        "email_verified_at": ("DATETIME", None),
        "consent_ai_transfer_at": ("DATETIME", None),
    },
    "questions": {
        # Банк был один, поэтому всё, что уже в базе, — радиационная безопасность.
        "module": ("VARCHAR(255)", "Радиационная безопасность"),
        "explanation": ("TEXT", None),
        "source": ("TEXT", None),
    },
    "history": {
        "module": ("VARCHAR(255)", "Радиационная безопасность"),
    },
    "test_sessions": {
        "module": ("VARCHAR(255)", "Радиационная безопасность"),
    },
}


def run_migrations() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table, columns in _NEW_COLUMNS.items():
            if table not in tables:
                continue
            existing = {col["name"] for col in inspector.get_columns(table)}
            for name, (coltype, backfill) in columns.items():
                if name in existing:
                    continue
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {coltype}"))
                if backfill is not None:
                    conn.execute(
                        text(f"UPDATE {table} SET {name} = :value WHERE {name} IS NULL"),
                        {"value": backfill},
                    )
