from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import get_progress, get_section_stats
from app.models import History, Mistake, User
from app.schemas import HistoryRow, StatsOut

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sections = get_section_stats(db, user.id)
    tests_count, average_percent = get_progress(db, user.id)
    return StatsOut(sections=sections, tests_count=tests_count, average_percent=average_percent)


@router.get("/history", response_model=list[HistoryRow])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(History)
        .filter(History.user_id == user.id)
        .order_by(History.id.desc())
        .all()
    )


@router.get("/mistakes/count")
def mistakes_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    count = db.query(Mistake).filter(Mistake.user_id == user.id).count()
    return {"count": count}
