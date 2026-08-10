from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Mode = Literal["training", "exam", "mistakes"]


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=255)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    first_name: str


class MeOut(UserOut):
    tests_count: int
    average_percent: int
    mistakes_count: int


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class SectionOut(BaseModel):
    name: str
    count: int


class StartTestIn(BaseModel):
    mode: Mode
    section: str | None = None
    subsection: str | None = None


class OptionOut(BaseModel):
    letter: str
    text: str


class QuestionOut(BaseModel):
    index: int
    total: int
    question: str
    options: list[OptionOut]
    timer_seconds_left: int | None = None


class SummaryOut(BaseModel):
    total: int
    asked: int
    correct: int
    wrong: int
    unanswered: int
    percent: int
    passed: bool
    threshold: int = 70


class StartTestOut(BaseModel):
    session_id: int | None = None
    mode: Mode
    section: str
    subsection: str | None = None
    question: QuestionOut | None = None
    summary: SummaryOut | None = None
    message: str | None = None


class AnswerIn(BaseModel):
    letter: str = Field(min_length=1, max_length=1)


class AnswerOut(BaseModel):
    correct: bool
    correct_letter: str
    correct_text: str
    session_id: int
    finished: bool
    question: QuestionOut | None = None
    summary: SummaryOut | None = None


class SessionStateOut(BaseModel):
    session_id: int
    mode: Mode
    section: str
    subsection: str | None = None
    finished: bool
    question: QuestionOut | None = None
    summary: SummaryOut | None = None


class StatRow(BaseModel):
    section: str
    asked: int
    correct: int
    percent: int


class StatsOut(BaseModel):
    sections: list[StatRow]
    tests_count: int
    average_percent: int


class HistoryRow(BaseModel):
    id: int
    date: str
    mode: Mode
    section: str
    total: int
    correct: int
    wrong: int
    percent: int


class SubsectionOut(BaseModel):
    name: str
    count: int
