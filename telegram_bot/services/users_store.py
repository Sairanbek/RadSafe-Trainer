from datetime import datetime, timezone
from database.database import get_connection


def register_visit(user_id: int, first_name: str, username: str):
    now = datetime.now(timezone.utc).isoformat(timespec="minutes")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT visits FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO users (user_id, first_name, username, first_seen, last_seen, visits) VALUES (?, ?, ?, ?, ?, 1)",
            (user_id, first_name, username, now, now)
        )
    else:
        cur.execute(
            "UPDATE users SET first_name=?, username=?, last_seen=?, visits=visits+1 WHERE user_id=?",
            (first_name, username, now, user_id)
        )
    conn.commit()
    conn.close()


def get_admin_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_seen FROM users")
    rows = cur.fetchall()
    conn.close()

    total = len(rows)
    now = datetime.now(timezone.utc)
    active_today = 0
    active_7d = 0

    for row in rows:
        last_seen = datetime.fromisoformat(row["last_seen"])
        delta_days = (now - last_seen).days
        if delta_days == 0:
            active_today += 1
        if delta_days <= 7:
            active_7d += 1

    return {"total": total, "active_today": active_today, "active_7d": active_7d}