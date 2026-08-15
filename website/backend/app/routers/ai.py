from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.gemini import GeminiError, chat_reply, explain_answer, study_plan
from app.logic import get_progress, get_section_stats
from app.models import Mistake, Question, User
from app.rate_limit import limiter
from app.schemas import AiTextOut, ChatRequestIn, ExplainRequestIn

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/explain", response_model=AiTextOut)
@limiter.limit("20/minute")
def explain(
    request: Request, payload: ExplainRequestIn, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    question = db.get(Question, payload.question_id)
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вопрос не найден")

    try:
        text = explain_answer(question, payload.chosen_text)
    except GeminiError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return AiTextOut(text=text)


@router.post("/chat", response_model=AiTextOut)
@limiter.limit("20/minute")
def chat(request: Request, payload: ChatRequestIn, _: User = Depends(get_current_user)):
    history = [{"role": m.role, "text": m.text} for m in payload.history]
    try:
        text = chat_reply(history, payload.message)
    except GeminiError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return AiTextOut(text=text)


@router.post("/study-plan", response_model=AiTextOut)
@limiter.limit("10/minute")
def get_study_plan(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sections = get_section_stats(db, user.id)
    tests_count, average_percent = get_progress(db, user.id)
    mistakes_count = db.query(Mistake).filter(Mistake.user_id == user.id).count()

    try:
        text = study_plan(sections, tests_count, average_percent, mistakes_count)
    except GeminiError as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(e)) from e

    return AiTextOut(text=text)
