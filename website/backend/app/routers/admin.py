from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin
from app.models import Question, User
from app.schemas import QuestionAdminOut, QuestionListOut, QuestionSaveIn

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/questions", response_model=QuestionListOut)
def list_questions(
    section: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    query = db.query(Question)
    if section:
        query = query.filter(Question.section == section)
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Question.question.ilike(like), Question.answer.ilike(like)))

    total = query.count()
    items = query.order_by(Question.id).offset((page - 1) * page_size).limit(page_size).all()

    return QuestionListOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/questions/{question_id}", response_model=QuestionAdminOut)
def get_question(question_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вопрос не найден")
    return question


@router.post("/questions", response_model=QuestionAdminOut, status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionSaveIn, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    # Ретрай на случай гонки: два одновременных создания могут прочитать один
    # и тот же max_id до того, как первое из них закоммитится.
    for _attempt in range(3):
        max_id = db.query(func.max(Question.id)).scalar() or 0
        question = Question(id=max_id + 1, **payload.model_dump())
        db.add(question)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            continue
        db.refresh(question)
        return question

    raise HTTPException(status.HTTP_409_CONFLICT, "Не удалось создать вопрос, попробуйте ещё раз")


@router.put("/questions/{question_id}", response_model=QuestionAdminOut)
def update_question(
    question_id: int,
    payload: QuestionSaveIn,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вопрос не найден")

    for field, value in payload.model_dump().items():
        setattr(question, field, value)

    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    question = db.get(Question, question_id)
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Вопрос не найден")

    db.delete(question)
    db.commit()
