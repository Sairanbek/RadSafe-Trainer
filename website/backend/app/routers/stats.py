from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import get_progress
from app.models import History, Mistake, Stat, User
from app.schemas import HistoryRow, StatRow, StatsOut

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Stat).filter(Stat.user_id == user.id).order_by(Stat.section).all()
    sections = [
        StatRow(
            section=r.section,
            asked=r.asked,
            correct=r.correct,
            percent=round(r.correct / r.asked * 100) if r.asked else 0,
        )
        for r in rows
    ]
    tests_count, average_percent = get_progress(db, user.id)
    return StatsOut(sections=sections, tests_count=tests_count, average_percent=average_percent)


@router.get("/history", response_model=list[HistoryRow])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(History)
        .filter(History.user_id == user.id)
        .order_by(History.id.desc())
        .all()
    )
    return [
        HistoryRow(
            id=r.id,
            date=r.date,
            mode=r.mode,
            section=r.section,
            total=r.total,
            correct=r.correct,
            wrong=r.wrong,
            percent=r.percent,
        )
        for r in rows
    ]


@router.get("/mistakes/count")
def mistakes_count(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    count = db.query(Mistake).filter(Mistake.user_id == user.id).count()
    return {"count": count}
