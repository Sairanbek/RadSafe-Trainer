from database.database import get_connection


def record_answer(user_id: int, section: str, is_correct: bool):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT asked, correct FROM stats WHERE user_id=? AND section=?", (user_id, section))
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO stats (user_id, section, asked, correct) VALUES (?, ?, 1, ?)",
            (user_id, section, 1 if is_correct else 0)
        )
    else:
        new_asked = row["asked"] + 1
        new_correct = row["correct"] + (1 if is_correct else 0)
        cur.execute(
            "UPDATE stats SET asked=?, correct=? WHERE user_id=? AND section=?",
            (new_asked, new_correct, user_id, section)
        )
    conn.commit()
    conn.close()


def get_stats(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT section, asked, correct FROM stats WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {row["section"]: {"asked": row["asked"], "correct": row["correct"]} for row in rows}