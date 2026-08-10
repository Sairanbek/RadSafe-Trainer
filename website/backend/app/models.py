from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    section: Mapped[str] = mapped_column(String(255), index=True)
    subsection: Mapped[str] = mapped_column(String(255))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    wrong1: Mapped[str] = mapped_column(Text)
    wrong2: Mapped[str] = mapped_column(Text)
    wrong3: Mapped[str] = mapped_column(Text)
    wrong4: Mapped[str] = mapped_column(Text)


class Stat(Base):
    __tablename__ = "stats"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    section: Mapped[str] = mapped_column(String(255), primary_key=True)
    asked: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)


class Mistake(Base):
    __tablename__ = "mistakes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, primary_key=True)


class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[str] = mapped_column(String(32))
    mode: Mapped[str] = mapped_column(String(32))
    section: Mapped[str] = mapped_column(String(255))
    total: Mapped[int] = mapped_column(Integer)
    correct: Mapped[int] = mapped_column(Integer)
    wrong: Mapped[int] = mapped_column(Integer)
    percent: Mapped[int] = mapped_column(Integer)


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    mode: Mapped[str] = mapped_column(String(32))
    section: Mapped[str] = mapped_column(String(255))
    subsection: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total: Mapped[int] = mapped_column(Integer)
    asked: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    wrong: Mapped[int] = mapped_column(Integer, default=0)
    used_ids: Mapped[str] = mapped_column(Text, default="[]")  # JSON list[int]
    current_qid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    correct_letter: Mapped[str | None] = mapped_column(String(1), nullable=True)
    options_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON {letter: text}
    start_time: Mapped[float] = mapped_column(Float)
    time_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
