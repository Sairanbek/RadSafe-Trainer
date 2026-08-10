from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.gemini import GeminiError, chat_reply, explain_answer, study_plan
from app.logic import get_progress
from app.models import Mistake, Question, Stat, User
from app.schemas import AiTextOut, ChatRequestIn, ExplainRequestIn

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/explain", response_model=AiTextOut)
def explain(payload: ExplainRequestIn, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    question = db.get(Question, payload.question_id)
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вопрос не найден")

    try:
        text = explain_answer(question, payload.chosen_text)
    except GeminiError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return AiTextOut(text=text)


@router.post("/chat", response_model=AiTextOut)
def chat(payload: ChatRequestIn, _: User = Depends(get_current_user)):
    history = [{"role": m.role, "text": m.text} for m in payload.history]
    try:
        text = chat_reply(history, payload.message)
    except GeminiError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return AiTextOut(text=text)


@router.post("/study-plan", response_model=AiTextOut)
def get_study_plan(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Stat).filter(Stat.user_id == user.id).order_by(Stat.section).all()
    sections = [
        {
            "section": r.section,
            "asked": r.asked,
            "correct": r.correct,
            "percent": round(r.correct / r.asked * 100) if r.asked else 0,
        }
        for r in rows
    ]
    tests_count, average_percent = get_progress(db, user.id)
    mistakes_count = db.query(Mistake).filter(Mistake.user_id == user.id).count()

    try:
        text = study_plan(sections, tests_count, average_percent, mistakes_count)
    except GeminiError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return AiTextOut(text=text)
