from datetime import datetime

from database.database import get_connection


def get_user(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE user_id = ?
        """,
        (user_id,)
    )

    user = cur.fetchone()

    conn.close()

    return user


def create_user(user_id, first_name, username):

    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        """
        INSERT INTO users
        (
            user_id,
            first_name,
            username,
            first_seen,
            last_seen,
            visits
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            first_name,
            username,
            now,
            now,
            1
        )
    )

    conn.commit()
    conn.close()


def update_visit(user_id):

    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        """
        UPDATE users
        SET last_seen = ?,
            visits = visits + 1
        WHERE user_id = ?
        """,
        (
            now,
            user_id
        )
    )

    conn.commit()
    conn.close()


def get_progress(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            COUNT(*) as tests,
            AVG(percent) as average
        FROM history
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cur.fetchone()

    conn.close()

    tests = result["tests"] or 0
    average = round(result["average"]) if result["average"] else 0

    return tests, average