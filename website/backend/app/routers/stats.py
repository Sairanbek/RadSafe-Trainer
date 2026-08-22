from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import get_progress, get_section_stats
from app.models import DEFAULT_MODULE, History, Mistake, Question, User
from app.schemas import HistoryRow, StatsOut

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def stats(
    module: str = Query(DEFAULT_MODULE),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    sections = get_section_stats(db, user.id, module)
    tests_count, average_percent = get_progress(db, user.id, module)
    return StatsOut(sections=sections, tests_count=tests_count, average_percent=average_percent)


@router.get("/history", response_model=list[HistoryRow])
def history(
    module: str = Query(DEFAULT_MODULE),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(History)
        .filter(History.user_id == user.id, History.module == module)
        .order_by(History.id.desc())
        .all()
    )


@router.get("/mistakes/count")
def mistakes_count(
    module: str = Query(DEFAULT_MODULE),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    # Считаем ошибки только текущего направления — «Мои ошибки» повторяет его же.
    count = (
        db.query(Mistake)
        .join(Question, Question.id == Mistake.question_id)
        .filter(Mistake.user_id == user.id, Question.module == module)
        .count()
    )
    return {"count": count}
