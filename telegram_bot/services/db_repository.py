from database.database import get_connection
from database.models import Question


def load_questions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, section, question, answer, wrong1, wrong2, wrong3, wrong4 FROM questions ORDER BY id")
    rows = cur.fetchall()
    conn.close()

    questions = [
        Question(
            id=row["id"],
            section=row["section"],
            question=row["question"],
            answer=row["answer"],
            wrong_answers=[row["wrong1"], row["wrong2"], row["wrong3"], row["wrong4"]]
        )
        for row in rows
    ]
    print(f"Загружено вопросов: {len(questions)}")
    return questions


def get_sections(questions):
    seen = []
    for q in questions:
        if q.section not in seen:
            seen.append(q.section)
    return seen