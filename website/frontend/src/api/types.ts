export type Mode = "training" | "exam" | "mistakes" | "learning";

export interface User {
  id: number;
  email: string;
  first_name: string;
}

export interface Me extends User {
  is_admin: boolean;
  email_verified: boolean;
  tests_count: number;
  average_percent: number;
  mistakes_count: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Module {
  name: string;
  count: number;
}

export interface Section {
  name: string;
  count: number;
}

export interface Subsection {
  name: string;
  count: number;
}

export interface Option {
  letter: string;
  text: string;
}

export interface QuestionPayload {
  id: number;
  index: number;
  total: number;
  question: string;
  options: Option[];
  timer_seconds_left: number | null;
  correct_letter: string | null;
  explanation: string | null;
  source: string | null;
}

export interface Summary {
  total: number;
  asked: number;
  correct: number;
  wrong: number;
  unanswered: number;
  percent: number;
  passed: boolean;
  threshold: number;
}

export interface StartTestResponse {
  session_id: number | null;
  mode: Mode;
  module: string | null;
  section: string;
  subsection: string | null;
  question: QuestionPayload | null;
  summary: Summary | null;
  message: string | null;
}

export interface SessionStateResponse {
  session_id: number;
  mode: Mode;
  section: string;
  subsection: string | null;
  finished: boolean;
  question: QuestionPayload | null;
  summary: Summary | null;
}

export interface AnswerResponse {
  correct: boolean;
  correct_letter: string;
  correct_text: string;
  explanation: string | null;
  source: string | null;
  session_id: number;
  finished: boolean;
  question: QuestionPayload | null;
  summary: Summary | null;
}

export interface StatRow {
  section: string;
  asked: number;
  correct: number;
  percent: number;
}

export interface StatsResponse {
  sections: StatRow[];
  tests_count: number;
  average_percent: number;
}

export interface HistoryRow {
  id: number;
  date: string;
  mode: Mode;
  section: string;
  total: number;
  correct: number;
  wrong: number;
  percent: number;
}

export interface LearningNextResponse {
  session_id: number;
  finished: boolean;
  question: QuestionPayload | null;
  message: string | null;
}

export interface MessageResponse {
  message: string;
}

export interface QuestionAdmin {
  id: number;
  section: string;
  subsection: string;
  question: string;
  answer: string;
  wrong1: string;
  wrong2: string;
  wrong3: string;
  wrong4: string;
}

export type QuestionSaveInput = Omit<QuestionAdmin, "id">;

export interface QuestionListResponse {
  items: QuestionAdmin[];
  total: number;
  page: number;
  page_size: number;
}

export type AiRole = "user" | "model";

export interface AiMessage {
  role: AiRole;
  text: string;
}

export interface AiTextResponse {
  text: string;
}
