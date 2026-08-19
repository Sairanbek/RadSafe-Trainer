from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    secret_key: str = "change-me-in-production"
    database_url: str = f"sqlite:///{BACKEND_DIR / 'rst_web.db'}"
    access_token_expire_minutes: int = 60  # короткий, реальная "сессия" держится refresh-токеном
    refresh_token_expire_days: int = 30
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    frontend_url: str = "http://localhost:5173"

    gemini_api_key: str = ""

    # Пути, которые в контейнере отличаются от локальной раскладки на Mac.
    # Пусто = локальные значения по умолчанию (см. свойства ниже).
    bot_db_path: str = ""   # банк вопросов, источник истины (telegram_bot/rst.db)
    backups_dir: str = ""   # куда scripts/backup_db.py кладёт снимки базы

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def bot_db(self) -> Path:
        if self.bot_db_path:
            return Path(self.bot_db_path)
        return BACKEND_DIR.parent.parent / "telegram_bot" / "rst.db"

    @property
    def backups(self) -> Path:
        if self.backups_dir:
            return Path(self.backups_dir)
        return BACKEND_DIR / "backups"


settings = Settings()
