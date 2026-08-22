import { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { api, ApiError } from "../api/client";
import { useModule } from "../context/ModuleContext";
import type { HistoryRow, Mode } from "../api/types";

const MODE_LABELS: Record<Mode, string> = {
  training: "Тренировка",
  exam: "Аттестация",
  mistakes: "Мои ошибки",
  learning: "Обучение",
};

export function HistoryPage() {
  const [rows, setRows] = useState<HistoryRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { module } = useModule();

  useEffect(() => {
    setRows(null);
    api
      .get<HistoryRow[]>(`/api/history?module=${encodeURIComponent(module)}`)
      .then(setRows)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить историю"));
  }, [module]);

  return (
    <Layout title="История">
      {error && <div className="card error-text">{error}</div>}
      {!rows && !error && <div className="spinner-wrap">Загрузка…</div>}
      {rows && rows.length === 0 && <div className="centered-msg">История пуста — пройдите первый тест</div>}
      {rows && rows.length > 0 && (
        <div className="list">
          {rows.map((r) => (
            <div key={r.id} className="card">
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span>{MODE_LABELS[r.mode]}</span>
                <span className={r.percent >= 70 ? "verdict-tag pass" : "verdict-tag fail"}>{r.percent}%</span>
              </div>
              <p style={{ marginTop: 6 }}>{r.section}</p>
              <p style={{ marginTop: 4, fontSize: 12.5 }}>
                {r.date} · {r.correct}/{r.total} правильных
              </p>
            </div>
          ))}
        </div>
      )}
    </Layout>
  );
}
