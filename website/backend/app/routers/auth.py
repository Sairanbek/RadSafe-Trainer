import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.logic import get_progress
from app.mailer import send_password_reset_email, send_verification_email
from app.models import EmailVerificationToken, Mistake, PasswordResetToken, User
from app.rate_limit import limiter
from app.schemas import (
    ChangePasswordIn,
    ForgotPasswordIn,
    LoginIn,
    MessageOut,
    MeOut,
    RegisterIn,
    ResetPasswordIn,
    TokenOut,
    UpdateProfileIn,
    UserOut,
    VerifyEmailIn,
)
from app.security import create_access_token, hash_password, verify_password
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

RESET_TOKEN_TTL_MINUTES = 30
VERIFY_TOKEN_TTL_HOURS = 24


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _send_verification_email(db: Session, background_tasks: BackgroundTasks, user: User) -> None:
    token = secrets.token_urlsafe(32)
    verification = EmailVerificationToken(
        user_id=user.id,
        token_hash=_hash_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=VERIFY_TOKEN_TTL_HOURS),
    )
    db.add(verification)
    db.commit()

    verify_link = f"{settings.frontend_url}/verify-email?token={token}"
    background_tasks.add_task(send_verification_email, user.email, verify_link)


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Этот email уже зарегистрирован")

    if not payload.consent_ai_transfer:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Необходимо согласие на трансграничную передачу данных ИИ-ассистенту",
        )

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        first_name=payload.first_name.strip(),
        consent_ai_transfer_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _send_verification_email(db, background_tasks, user)

    token = create_access_token(user.id)
    return TokenOut(access_token=token, user=UserOut(id=user.id, email=user.email, first_name=user.first_name))


@router.post("/login", response_model=TokenOut)
@limiter.limit("10/minute")
def login(request: Request, payload: LoginIn, db: Session = Depends(get_db)):
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
        is_admin=user.is_admin,
        email_verified=user.email_verified_at is not None,
        tests_count=tests_count,
        average_percent=average_percent,
        mistakes_count=mistakes_count,
    )


@router.patch("/me", response_model=UserOut)
def update_profile(payload: UpdateProfileIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    email = payload.email.lower()
    if email != user.email:
        existing = db.query(User).filter(User.email == email).first()
        if existing is not None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Этот email уже занят")
        user.email = email

    user.first_name = payload.first_name.strip()
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserOut(id=user.id, email=user.email, first_name=user.first_name)


@router.post("/change-password", response_model=MessageOut)
def change_password(payload: ChangePasswordIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Неверный текущий пароль")

    user.password_hash = hash_password(payload.new_password)
    db.add(user)
    db.commit()

    return MessageOut(message="Пароль изменён")


@router.post("/forgot-password", response_model=MessageOut)
@limiter.limit("3/minute")
def forgot_password(
    request: Request, payload: ForgotPasswordIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    generic = MessageOut(message="Если такой email зарегистрирован, письмо со ссылкой уже отправлено")

    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None:
        return generic

    token = secrets.token_urlsafe(32)
    reset = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
    )
    db.add(reset)
    db.commit()

    reset_link = f"{settings.frontend_url}/reset-password?token={token}"
    background_tasks.add_task(send_password_reset_email, user.email, reset_link)

    return generic


@router.post("/reset-password", response_model=MessageOut)
@limiter.limit("5/minute")
def reset_password(request: Request, payload: ResetPasswordIn, db: Session = Depends(get_db)):
    token_hash = _hash_token(payload.token)
    reset = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()

    now = datetime.now(timezone.utc)
    expires_at = reset.expires_at.replace(tzinfo=timezone.utc) if reset else None

    if reset is None or reset.used or expires_at is None or expires_at < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ссылка недействительна или истекла")

    user = db.get(User, reset.user_id)
    user.password_hash = hash_password(payload.new_password)
    reset.used = True
    db.add_all([user, reset])
    db.commit()

    return MessageOut(message="Пароль успешно изменён")


@router.post("/verify-email", response_model=MessageOut)
@limiter.limit("10/minute")
def verify_email(request: Request, payload: VerifyEmailIn, db: Session = Depends(get_db)):
    token_hash = _hash_token(payload.token)
    verification = db.query(EmailVerificationToken).filter(EmailVerificationToken.token_hash == token_hash).first()

    now = datetime.now(timezone.utc)
    expires_at = verification.expires_at.replace(tzinfo=timezone.utc) if verification else None

    if verification is None or verification.used or expires_at is None or expires_at < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ссылка недействительна или истекла")

    user = db.get(User, verification.user_id)
    user.email_verified_at = now
    verification.used = True
    db.add_all([user, verification])
    db.commit()

    return MessageOut(message="Email подтверждён")


@router.post("/resend-verification", response_model=MessageOut)
@limiter.limit("3/minute")
def resend_verification(
    request: Request, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    if user.email_verified_at is not None:
        return MessageOut(message="Email уже подтверждён")

    _send_verification_email(db, background_tasks, user)
    return MessageOut(message="Письмо с подтверждением отправлено")
