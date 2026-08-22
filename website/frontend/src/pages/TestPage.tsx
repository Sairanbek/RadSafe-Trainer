import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Layout } from "../components/Layout";
import { Timer } from "../components/Timer";
import { api, ApiError } from "../api/client";
import { renderBold } from "../utils/markdown";
import type {
  AiTextResponse,
  AnswerResponse,
  LearningNextResponse,
  Mode,
  QuestionPayload,
  SessionStateResponse,
  StartTestResponse,
  Summary,
} from "../api/types";

const MODE_LABELS: Record<Mode, string> = {
  training: "Тренировка",
  exam: "Аттестация",
  mistakes: "Мои ошибки",
  learning: "Обучение",
};

interface Feedback {
  chosen: string;
  correct: boolean;
  correctLetter: string;
  correctText: string;
}

export function TestPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const [mode, setMode] = useState<Mode | null>(null);
  const [section, setSection] = useState<string>("");
  const [question, setQuestion] = useState<QuestionPayload | null>(null);
  const [pendingQuestion, setPendingQuestion] = useState<QuestionPayload | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [pendingSummary, setPendingSummary] = useState<Summary | null>(null);
  const [answering, setAnswering] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [learningDoneMessage, setLearningDoneMessage] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [bankExplanation, setBankExplanation] = useState<{ text: string; source: string | null } | null>(
    null,
  );

  const goToSummary = useCallback(
    (summary: Summary) => {
      navigate(`/test/${sessionId}/summary`, { replace: true, state: { summary, mode, section } });
    },
    [navigate, sessionId, mode, section],
  );

  useEffect(() => {
    const startState = location.state as { start?: StartTestResponse } | null;
    if (startState?.start && startState.start.session_id === Number(sessionId)) {
      setMode(startState.start.mode);
      setSection(startState.start.section);
      setQuestion(startState.start.question);
      setLoading(false);
      return;
    }

    api
      .get<SessionStateResponse>(`/api/tests/${sessionId}`)
      .then((res) => {
        setMode(res.mode);
        setSection(res.section);
        if (res.finished && res.summary) {
          goToSummary(res.summary);
          return;
        }
        setQuestion(res.question);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить тест"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  async function handleAnswer(letter: string) {
    if (answering || feedback) return;
    setAnswering(true);
    setError(null);
    try {
      const res = await api.post<AnswerResponse>(`/api/tests/${sessionId}/answer`, { letter });
      setFeedback({
        chosen: letter,
        correct: res.correct,
        correctLetter: res.correct_letter,
        correctText: res.correct_text,
      });
      setBankExplanation(res.explanation ? { text: res.explanation, source: res.source } : null);
      if (res.finished && res.summary) {
        setPendingSummary(res.summary);
      } else {
        setPendingQuestion(res.question);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось отправить ответ");
    } finally {
      setAnswering(false);
    }
  }

  function handleNext() {
    if (pendingSummary) {
      goToSummary(pendingSummary);
      return;
    }
    setQuestion(pendingQuestion);
    setPendingQuestion(null);
    setFeedback(null);
    setExplanation(null);
    setBankExplanation(null);
  }

  async function handleLearningNext() {
    if (answering) return;
    setAnswering(true);
    setError(null);
    try {
      const res = await api.post<LearningNextResponse>(`/api/tests/${sessionId}/next`);
      if (res.finished) {
        setLearningDoneMessage(res.message ?? "Просмотр завершён");
        setQuestion(null);
      } else {
        setQuestion(res.question);
        setExplanation(null);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось загрузить следующий вопрос");
    } finally {
      setAnswering(false);
    }
  }

  async function handleExplain() {
    if (explaining || explanation || !question) return;
    setExplaining(true);
    setError(null);
    try {
      const chosenText = feedback ? question.options.find((o) => o.letter === feedback.chosen)?.text ?? null : null;
      const res = await api.post<AiTextResponse>("/api/ai/explain", {
        question_id: question.id,
        chosen_text: chosenText,
      });
      setExplanation(res.text);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось получить объяснение");
    } finally {
      setExplaining(false);
    }
  }

  const handleExpire = useCallback(async () => {
    if (!sessionId) return;
    try {
      const res = await api.get<SessionStateResponse>(`/api/tests/${sessionId}`);
      if (res.finished && res.summary) {
        goToSummary(res.summary);
      }
    } catch {
      /* ignore — user can retry */
    }
  }, [sessionId, goToSummary]);

  if (loading) {
    return (
      <Layout title="Тест" hideNav>
        <div className="spinner-wrap">Загрузка…</div>
      </Layout>
    );
  }

  if (error && !question) {
    return (
      <Layout title="Тест" hideNav>
        <div className="card error-text">{error}</div>
      </Layout>
    );
  }

  if (learningDoneMessage) {
    return (
      <Layout title="Обучение" hideNav>
        <div className="centered-msg">{learningDoneMessage}</div>
        <button className="btn btn-primary btn-block" onClick={() => navigate("/", { replace: true })}>
          🏠 Главное меню
        </button>
      </Layout>
    );
  }

  if (!question) {
    return (
      <Layout title="Тест" hideNav>
        <div className="centered-msg">Вопросы закончились 🎉</div>
      </Layout>
    );
  }

  const isLearning = mode === "learning";

  // В режиме обучения разбор приходит вместе с вопросом, в остальных — вместе
  // с ответом. Он бесплатный и мгновенный, поэтому к Gemini идём только когда
  // разбора в банке нет (пока это вопросы по радиационной безопасности).
  const storedExplanation = isLearning
    ? question.explanation
      ? { text: question.explanation, source: question.source }
      : null
    : bankExplanation;

  const explainBlock = storedExplanation ? (
    <div className="card explanation-card">
      <div className="explanation-label">📖 Разбор</div>
      <p>{renderBold(storedExplanation.text)}</p>
      {storedExplanation.source && <div className="explanation-source">{storedExplanation.source}</div>}
    </div>
  ) : explanation ? (
    <div className="card explanation-card">
      <div className="explanation-label">🤖 Объяснение</div>
      <p>{renderBold(explanation)}</p>
    </div>
  ) : (
    <button className="btn btn-ghost btn-block" disabled={explaining} onClick={handleExplain}>
      {explaining ? "Думаю…" : "🤖 Объяснить"}
    </button>
  );

  return (
    <Layout title={mode ? MODE_LABELS[mode] : "Тест"} hideNav>
      <div className="test-progress">
        Вопрос {question.index} из {question.total}
      </div>

      {mode === "exam" && question.timer_seconds_left !== null && (
        <Timer secondsLeft={question.timer_seconds_left} onExpire={handleExpire} />
      )}

      <div className="card">
        <div className="question-text">{question.question}</div>
      </div>

      <div className="options">
        {question.options.map((opt) => {
          let cls = "option-btn";
          if (isLearning) {
            if (opt.letter === question.correct_letter) cls += " correct";
          } else if (feedback) {
            if (opt.letter === feedback.correctLetter) cls += " correct";
            else if (opt.letter === feedback.chosen) cls += " wrong";
          }
          return (
            <button
              key={opt.letter}
              className={cls}
              disabled={isLearning || answering || !!feedback}
              onClick={() => handleAnswer(opt.letter)}
            >
              <span className="letter">{opt.letter}</span>
              <span>{opt.text}</span>
            </button>
          );
        })}
      </div>

      {error && <div className="error-text">{error}</div>}

      {isLearning && (
        <>
          {explainBlock}
          <button className="btn btn-primary btn-block" disabled={answering} onClick={handleLearningNext}>
            Далее →
          </button>
        </>
      )}

      {!isLearning && feedback && (
        <>
          <div className={`feedback-banner ${feedback.correct ? "correct" : "wrong"}`}>
            {feedback.correct ? "✅ Верно!" : `❌ Неверно. Правильный ответ: ${feedback.correctText}`}
          </div>
          {explainBlock}
          <button className="btn btn-primary btn-block" onClick={handleNext}>
            {pendingSummary ? "Показать результат" : "Далее →"}
          </button>
        </>
      )}
    </Layout>
  );
}
