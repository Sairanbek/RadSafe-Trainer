"""Снимок базы данных сайта (SQLite) в backend/backups/.

Использование (вручную или по расписанию — cron / launchd):
    python scripts/backup_db.py

Хранит последние 14 снимков, более старые удаляет автоматически.
"""

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings  # noqa: E402

BACKUPS_DIR = settings.backups
KEEP_LAST = 14


def _db_path() -> Path:
    parsed = urlparse(settings.database_url)
    if parsed.scheme != "sqlite":
        raise SystemExit(f"Бэкап поддерживается только для SQLite, а не {parsed.scheme}")
    return Path(parsed.path)


def main():
    src_path = _db_path()
    if not src_path.exists():
        raise SystemExit(f"База данных не найдена: {src_path}")

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_path = BACKUPS_DIR / f"{src_path.stem}_{stamp}.db"

    # Онлайн-бэкап через sqlite3 API — безопасен, даже если в этот момент
    # backend пишет в базу (обычная копия файла может захватить "разорванную"
    # запись посреди транзакции).
    src_conn = sqlite3.connect(src_path)
    dest_conn = sqlite3.connect(dest_path)
    with dest_conn:
        src_conn.backup(dest_conn)
    src_conn.close()
    dest_conn.close()

    print(f"Бэкап создан: {dest_path}")

    backups = sorted(BACKUPS_DIR.glob(f"{src_path.stem}_*.db"))
    for old in backups[:-KEEP_LAST]:
        old.unlink()
        print(f"Удалён старый бэкап: {old.name}")


if __name__ == "__main__":
    main()
