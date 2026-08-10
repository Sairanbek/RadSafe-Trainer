import json
import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import (
    ALL_SECTIONS,
    EXAM_QUESTIONS,
    EXAM_TIME,
    add_history,
    add_mistake,
    build_question,
    get_training_length,
    is_exam_time_up,
    question_out,
    record_answer,
    remove_mistake,
    section_count,
    summary_out,
)
from app.models import Mistake, Question, TestSession, User
from app.schemas import AnswerIn, AnswerOut, LearningNextOut, SessionStateOut, StartTestIn, StartTestOut

router = APIRouter(prefix="/api/tests", tags=["tests"])


def _get_owned_session(db: Session, session_id: int, user: User) -> TestSession:
    session = db.get(TestSession, session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сессия теста не найдена")
    return session


def _finish(db: Session, session: TestSession) -> None:
    if session.finished:
        return
    if session.mode != "learning":
        add_history(
            db, session.user_id, session.mode, session.section, session.asked, session.correct, session.wrong
        )
    session.finished = True
    db.add(session)
    db.commit()


@router.post("/start", response_model=StartTestOut)
def start_test(payload: StartTestIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    mode = payload.mode

    if mode == "exam":
        section = ALL_SECTIONS
        subsection = None
        total = EXAM_QUESTIONS
        time_limit = EXAM_TIME
    elif mode == "mistakes":
        mistake_count = db.query(Mistake).filter(Mistake.user_id == user.id).count()
        if mistake_count == 0:
            return StartTestOut(mode=mode, section="Ошибки", message="🎉 Ошибок нет!")
        section = "Ошибки"
        subsection = None
        total = mistake_count
        time_limit = None
    elif mode == "learning":
        section = payload.section or ALL_SECTIONS
        subsection = payload.subsection
        if subsection:
            total = db.query(Question).filter(
                Question.section == section, Question.subsection == subsection
            ).count()
        else:
            total = section_count(db, section)
        time_limit = None
    else:  # training
        section = payload.section or ALL_SECTIONS
        subsection = payload.subsection
        if subsection:
            pool_size = section_count(db, section) if section == ALL_SECTIONS else (
                db.query(Question)
                .filter(Question.section == section, Question.subsection == subsection)
                .count()
            )
            total = min(pool_size, 50)
        else:
            total = get_training_length(db, section)
        time_limit = None

    session = TestSession(
        user_id=user.id,
        mode=mode,
        section=section,
        subsection=subsection,
        total=total,
        used_ids="[]",
        start_time=time.time(),
        time_limit=time_limit,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    q = build_question(db, session)
    if q is None:
        return StartTestOut(
            session_id=session.id,
            mode=mode,
            section=section,
            subsection=subsection,
            message="Вопросы не найдены",
        )

    return StartTestOut(
        session_id=session.id,
        mode=mode,
        section=section,
        subsection=subsection,
        question=question_out(db, session, q),
    )


@router.get("/{session_id}", response_model=SessionStateOut)
def get_test(session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    session = _get_owned_session(db, session_id, user)

    if not session.finished and is_exam_time_up(session):
        _finish(db, session)

    if session.finished:
        return SessionStateOut(
            session_id=session.id,
            mode=session.mode,
            section=session.section,
            subsection=session.subsection,
            finished=True,
            summary=summary_out(session),
        )

    return SessionStateOut(
        session_id=session.id,
        mode=session.mode,
        section=session.section,
        subsection=session.subsection,
        finished=False,
        question=question_out(db, session),
    )


@router.post("/{session_id}/answer", response_model=AnswerOut)
def answer_test(
    session_id: int,
    payload: AnswerIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = _get_owned_session(db, session_id, user)

    if session.finished:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Тест уже завершён")

    if is_exam_time_up(session):
        letter_map = json.loads(session.options_json) if session.options_json else {}
        correct_letter = session.correct_letter or ""
        _finish(db, session)
        return AnswerOut(
            correct=False,
            correct_letter=correct_letter,
            correct_text=letter_map.get(correct_letter, ""),
            session_id=session.id,
            finished=True,
            summary=summary_out(session),
        )

    chosen = payload.letter.upper()
    correct_letter = session.correct_letter
    if correct_letter is None or session.current_qid is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нет активного вопроса")

    letter_map = json.loads(session.options_json)
    question = db.get(Question, session.current_qid)
    is_correct = chosen == correct_letter

    if is_correct:
        session.correct += 1
        record_answer(db, user.id, question.section, True)
        if session.mode == "mistakes":
            remove_mistake(db, user.id, question.id)
    else:
        session.wrong += 1
        record_answer(db, user.id, question.section, False)
        add_mistake(db, user.id, question.id)

    session.asked += 1
    db.add(session)
    db.commit()
    db.refresh(session)

    result_common = dict(
        correct=is_correct,
        correct_letter=correct_letter,
        correct_text=letter_map[correct_letter],
        session_id=session.id,
    )

    if session.asked >= session.total:
        _finish(db, session)
        return AnswerOut(**result_common, finished=True, summary=summary_out(session))

    next_q = build_question(db, session)
    if next_q is None:
        _finish(db, session)
        return AnswerOut(**result_common, finished=True, summary=summary_out(session))

    return AnswerOut(
        **result_common,
        finished=False,
        question=question_out(db, session, next_q),
    )


@router.post("/{session_id}/next", response_model=LearningNextOut)
def next_learning_question(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = _get_owned_session(db, session_id, user)

    if session.mode != "learning":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Доступно только в режиме обучения")

    if session.finished:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Просмотр уже завершён")

    session.asked += 1
    db.add(session)
    db.commit()
    db.refresh(session)

    if session.asked >= session.total:
        _finish(db, session)
        return LearningNextOut(session_id=session.id, finished=True, message=f"Просмотрено вопросов: {session.total}")

    next_q = build_question(db, session)
    if next_q is None:
        _finish(db, session)
        return LearningNextOut(session_id=session.id, finished=True, message=f"Просмотрено вопросов: {session.asked}")

    return LearningNextOut(session_id=session.id, finished=False, question=question_out(db, session, next_q))
