from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Mode = Literal["training", "exam", "mistakes", "learning"]


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=255)
    consent_ai_transfer: bool


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    first_name: str


class MeOut(UserOut):
    is_admin: bool
    email_verified: bool
    tests_count: int
    average_percent: int
    mistakes_count: int


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class VerifyEmailIn(BaseModel):
    token: str


class UpdateProfileIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=255)
    email: EmailStr


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class MessageOut(BaseModel):
    message: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class RefreshIn(BaseModel):
    refresh_token: str


class RefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


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
    id: int
    index: int
    total: int
    question: str
    options: list[OptionOut]
    timer_seconds_left: int | None = None
    correct_letter: str | None = None


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
    model_config = ConfigDict(from_attributes=True)

    section: str
    asked: int
    correct: int
    percent: int


class StatsOut(BaseModel):
    sections: list[StatRow]
    tests_count: int
    average_percent: int


class HistoryRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class LearningNextOut(BaseModel):
    session_id: int
    finished: bool
    question: QuestionOut | None = None
    message: str | None = None


class QuestionAdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    section: str
    subsection: str
    question: str
    answer: str
    wrong1: str
    wrong2: str
    wrong3: str
    wrong4: str


class QuestionSaveIn(BaseModel):
    section: str = Field(min_length=1, max_length=255)
    subsection: str = Field(min_length=1, max_length=255)
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    wrong1: str = Field(min_length=1)
    wrong2: str = Field(min_length=1)
    wrong3: str = Field(min_length=1)
    wrong4: str = Field(min_length=1)


class QuestionListOut(BaseModel):
    items: list[QuestionAdminOut]
    total: int
    page: int
    page_size: int


class ExplainRequestIn(BaseModel):
    question_id: int
    chosen_text: str | None = None


class AiMessage(BaseModel):
    role: Literal["user", "model"]
    text: str = Field(min_length=1, max_length=4000)


class ChatRequestIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[AiMessage] = []


class AiTextOut(BaseModel):
    text: str
