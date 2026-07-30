from database.database import get_connection


def add_mistake(user_id: int, question_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO mistakes (user_id, question_id) VALUES (?, ?)", (user_id, question_id))
    conn.commit()
    conn.close()


def remove_mistake(user_id: int, question_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM mistakes WHERE user_id=? AND question_id=?", (user_id, question_id))
    conn.commit()
    conn.close()


def get_mistake_ids(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT question_id FROM mistakes WHERE user_id=?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {row["question_id"] for row in rows}