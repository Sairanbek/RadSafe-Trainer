from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import get_progress
from app.models import Mistake, User
from app.schemas import LoginIn, MeOut, RegisterIn, TokenOut, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Этот email уже зарегистрирован")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        first_name=payload.first_name.strip(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut(id=user.id, email=user.email, first_name=user.first_name))


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")

    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut(id=user.id, email=user.email, first_name=user.first_name))


@router.get("/me", response_model=MeOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tests_count, average_percent = get_progress(db, user.id)
    mistakes_count = db.query(Mistake).filter(Mistake.user_id == user.id).count()

    return MeOut(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        tests_count=tests_count,
        average_percent=average_percent,
        mistakes_count=mistakes_count,
    )
