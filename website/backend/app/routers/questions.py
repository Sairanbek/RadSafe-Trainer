from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import get_sections, get_subsections, section_has_useful_subsections
from app.models import User
from app.schemas import SectionOut, SubsectionOut

router = APIRouter(prefix="/api", tags=["questions"])


@router.get("/sections", response_model=list[SectionOut])
def sections(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return get_sections(db)


@router.get("/subsections", response_model=list[SubsectionOut])
def subsections(
    section: str = Query(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not section_has_useful_subsections(db, section):
        return []
    return get_subsections(db, section)
