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
_NEW_USER_COLUMNS = {
    "email_verified_at": "DATETIME",
    "consent_ai_transfer_at": "DATETIME",
}


def run_migrations() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing = {col["name"] for col in inspector.get_columns("users")}
    with engine.begin() as conn:
        for name, coltype in _NEW_USER_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {coltype}"))
