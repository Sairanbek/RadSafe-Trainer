from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import get_modules, get_sections, get_subsections, section_has_useful_subsections
from app.models import DEFAULT_MODULE, User
from app.schemas import ModuleOut, SectionOut, SubsectionOut

router = APIRouter(prefix="/api", tags=["questions"])


@router.get("/modules", response_model=list[ModuleOut])
def modules(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    """Направления подготовки: радиационная безопасность, радиология, госслужба."""
    return get_modules(db)


@router.get("/sections", response_model=list[SectionOut])
def sections(
    module: str = Query(DEFAULT_MODULE),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return get_sections(db, module)


@router.get("/subsections", response_model=list[SubsectionOut])
def subsections(
    section: str = Query(...),
    module: str = Query(DEFAULT_MODULE),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not section_has_useful_subsections(db, section, module):
        return []
    return [s for s in get_subsections(db, section, module) if s["name"]]
