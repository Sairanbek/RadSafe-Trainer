"""Портирование логики тестирования из telegram_bot/handlers/test.py.

Состояние теста (аналог user_state в боте) хранится в таблице test_sessions,
а не в памяти процесса, чтобы переживать перезапуски и работать с несколькими
воркерами.
"""

import json
import random
import time
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import History, Mistake, Question, Stat, TestSession

LETTERS = ["A", "B", "C", "D", "E"]
EXAM_QUESTIONS = 50
EXAM_TIME = 75 * 60
PASS_THRESHOLD = 70
ALL_SECTIONS = "ALL"


def get_sections(db: Session) -> list[dict]:
    rows = (
        db.query(Question.section, func.min(Question.id).label("first_id"), func.count(Question.id))
        .group_by(Question.section)
        .order_by("first_id")
        .all()
    )
    return [{"name": r[0], "count": r[2]} for r in rows]


def get_subsections(db: Session, section: str) -> list[dict]:
    rows = (
        db.query(Question.subsection, func.min(Question.id).label("first_id"), func.count(Question.id))
        .filter(Question.section == section)
        .group_by(Question.subsection)
        .order_by("first_id")
        .all()
    )
    return [{"name": r[0], "count": r[2]} for r in rows]


def section_has_useful_subsections(db: Session, section: str) -> bool:
    subs = get_subsections(db, section)
    if len(subs) < 2:
        return False
    return sum(1 for s in subs if s["count"] >= 3) >= 2


def section_count(db: Session, section: str) -> int:
    if section == ALL_SECTIONS:
        return db.query(func.count(Question.id)).scalar() or 0
    return db.query(func.count(Question.id)).filter(Question.section == section).scalar() or 0


def get_training_length(db: Session, section: str) -> int:
    if section == ALL_SECTIONS:
        return 50

    count = section_count(db, section)
    if count <= 30:
        return count
    if count <= 100:
        return 30
    if count <= 200:
        return 40
    return 50


def _candidate_pool(db: Session, session: TestSession) -> list[Question]:
    used_ids = set(json.loads(session.used_ids))

    if session.mode == "mistakes":
        mistake_ids = [
            row[0]
            for row in db.query(Mistake.question_id).filter(Mistake.user_id == session.user_id).all()
        ]
        pool_ids = [qid for qid in mistake_ids if qid not in used_ids]
        if not pool_ids:
            return []
        return db.query(Question).filter(Question.id.in_(pool_ids)).all()

    query = db.query(Question)
    if session.section != ALL_SECTIONS:
        query = query.filter(Question.section == session.section)
    if session.subsection:
        query = query.filter(Question.subsection == session.subsection)
    return [q for q in query.all() if q.id not in used_ids]


def build_question(db: Session, session: TestSession) -> Question | None:
    pool = _candidate_pool(db, session)
    if not pool:
        return None

    q = random.choice(pool)

    used_ids = json.loads(session.used_ids)
    used_ids.append(q.id)
    session.used_ids = json.dumps(used_ids)
    session.current_qid = q.id

    options = [q.answer] + [q.wrong1, q.wrong2, q.wrong3, q.wrong4]
    random.shuffle(options)
    correct_letter = LETTERS[options.index(q.answer)]

    letter_map = {LETTERS[i]: opt for i, opt in enumerate(options)}
    session.correct_letter = correct_letter
    session.options_json = json.dumps(letter_map)

    db.add(session)
    db.commit()
    db.refresh(session)

    return q


def timer_seconds_left(session: TestSession) -> int | None:
    if session.mode != "exam" or session.time_limit is None:
        return None
    passed = time.time() - session.start_time
    left = session.time_limit - passed
    return max(0, int(left))


def is_exam_time_up(session: TestSession) -> bool:
    if session.mode != "exam" or session.time_limit is None:
        return False
    return time.time() - session.start_time >= session.time_limit


def question_out(db: Session, session: TestSession, q: Question | None = None) -> dict | None:
    if session.current_qid is None or session.options_json is None:
        return None
    if q is None:
        q = db.get(Question, session.current_qid)
        if q is None:
            return None

    letter_map: dict[str, str] = json.loads(session.options_json)
    options = [{"letter": letter, "text": text} for letter, text in letter_map.items()]

    return {
        "index": session.asked + 1,
        "total": session.total,
        "question": q.question,
        "options": options,
        "timer_seconds_left": timer_seconds_left(session),
        "correct_letter": session.correct_letter if session.mode == "learning" else None,
    }


def summary_out(session: TestSession) -> dict:
    total = session.total
    asked = session.asked
    correct = session.correct
    wrong = session.wrong
    unanswered = total - asked
    percent = round(correct / total * 100) if total else 0

    return {
        "total": total,
        "asked": asked,
        "correct": correct,
        "wrong": wrong,
        "unanswered": unanswered,
        "percent": percent,
        "passed": percent >= PASS_THRESHOLD,
        "threshold": PASS_THRESHOLD,
    }


def record_answer(db: Session, user_id: int, section: str, correct: bool) -> None:
    stat = db.get(Stat, {"user_id": user_id, "section": section})
    if stat is None:
        stat = Stat(user_id=user_id, section=section, asked=0, correct=0)
        db.add(stat)

    stat.asked += 1
    if correct:
        stat.correct += 1

    db.commit()


def add_mistake(db: Session, user_id: int, question_id: int) -> None:
    existing = db.get(Mistake, {"user_id": user_id, "question_id": question_id})
    if existing is None:
        db.add(Mistake(user_id=user_id, question_id=question_id))
        db.commit()


def remove_mistake(db: Session, user_id: int, question_id: int) -> None:
    existing = db.get(Mistake, {"user_id": user_id, "question_id": question_id})
    if existing is not None:
        db.delete(existing)
        db.commit()


def add_history(db: Session, user_id: int, mode: str, section: str, total: int, correct: int, wrong: int) -> None:
    percent = round(correct / total * 100) if total else 0
    entry = History(
        user_id=user_id,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        mode=mode,
        section=section,
        total=total,
        correct=correct,
        wrong=wrong,
        percent=percent,
    )
    db.add(entry)
    db.commit()


def get_progress(db: Session, user_id: int) -> tuple[int, int]:
    tests = db.query(func.count(History.id)).filter(History.user_id == user_id).scalar() or 0
    avg = db.query(func.avg(History.percent)).filter(History.user_id == user_id).scalar()
    average = round(avg) if avg else 0
    return tests, average
