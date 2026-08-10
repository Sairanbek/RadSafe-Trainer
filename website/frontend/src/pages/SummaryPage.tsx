import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Layout } from "../components/Layout";
import { api, ApiError } from "../api/client";
import type { Mode, SessionStateResponse, Summary } from "../api/types";

const MODE_LABELS: Record<Mode, string> = {
  training: "Тренировка",
  exam: "Аттестация",
  mistakes: "Мои ошибки",
  learning: "Обучение",
};

export function SummaryPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const location = useLocation();
  const navigate = useNavigate();

  const initial = location.state as { summary?: Summary; mode?: Mode; section?: string } | null;
  const [summary, setSummary] = useState<Summary | null>(initial?.summary ?? null);
  const [mode, setMode] = useState<Mode | undefined>(initial?.mode);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (summary) return;
    api
      .get<SessionStateResponse>(`/api/tests/${sessionId}`)
      .then((res) => {
        if (res.summary) setSummary(res.summary);
        setMode(res.mode);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить результат"));
  }, [sessionId, summary]);

  return (
    <Layout title="Результат" hideNav>
      {error && <div className="card error-text">{error}</div>}
      {!summary && !error && <div className="spinner-wrap">Загрузка…</div>}
      {summary && (
        <>
          {mode && <div className="test-progress">{MODE_LABELS[mode]}</div>}
          <div className="card summary-verdict">
            <div className="percent">{summary.percent}%</div>
            <div className={`verdict-tag ${summary.passed ? "pass" : "fail"}`}>
              {summary.passed ? "✅ Сдал" : "❌ Не сдал"}
            </div>
          </div>
          <div className="card summary-rows">
            <div className="summary-row">
              <span>Отвечено</span>
              <span>
                {summary.asked} из {summary.total}
              </span>
            </div>
            {summary.unanswered > 0 && (
              <div className="summary-row">
                <span>Не отвечено (время вышло)</span>
                <span>{summary.unanswered}</span>
              </div>
            )}
            <div className="summary-row">
              <span>Правильных</span>
              <span>{summary.correct}</span>
            </div>
            <div className="summary-row">
              <span>Ошибок</span>
              <span>{summary.wrong}</span>
            </div>
            <div className="summary-row">
              <span>Порог сдачи</span>
              <span>{summary.threshold}%</span>
            </div>
          </div>
          <button className="btn btn-primary btn-block" onClick={() => navigate("/", { replace: true })}>
            🏠 Главное меню
          </button>
        </>
      )}
    </Layout>
  );
}
