from datetime import datetime, timezone
from database.database import get_connection

MAX_ENTRIES_PER_USER = 50


def add_session(user_id: int, mode: str, section: str, total: int, correct: int, wrong: int):
    percent = round(correct / total * 100) if total else 0
    now = datetime.now(timezone.utc).isoformat(timespec="minutes")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (user_id, date, mode, section, total, correct, wrong, percent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, now, mode, section, total, correct, wrong, percent)
    )
    cur.execute(
        """
        DELETE FROM history
        WHERE user_id = ? AND id NOT IN (
            SELECT id FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?
        )
        """,
        (user_id, user_id, MAX_ENTRIES_PER_USER)
    )
    conn.commit()
    conn.close()


def get_history(user_id: int, limit: int = 10):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT date, mode, section, total, correct, wrong, percent FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]