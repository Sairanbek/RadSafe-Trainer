import { useEffect, useState } from "react";
import { Layout } from "../components/Layout";
import { api, ApiError } from "../api/client";
import type { StatsResponse } from "../api/types";

export function StatsPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<StatsResponse>("/api/stats")
      .then(setStats)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить статистику"));
  }, []);

  return (
    <Layout title="Статистика">
      {error && <div className="card error-text">{error}</div>}
      {!stats && !error && <div className="spinner-wrap">Загрузка…</div>}
      {stats && (
        <>
          <div className="stat-grid">
            <div className="stat-tile">
              <div className="value">{stats.tests_count}</div>
              <div className="label">Пройдено тестов</div>
            </div>
            <div className="stat-tile">
              <div className="value">{stats.average_percent}%</div>
              <div className="label">Средний результат</div>
            </div>
          </div>

          {stats.sections.length === 0 ? (
            <div className="centered-msg">Пока нет данных — пройдите первый тест</div>
          ) : (
            <div className="list">
              {stats.sections.map((s) => (
                <div key={s.section} className="card">
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <span>{s.section}</span>
                    <span className="count">
                      {s.correct}/{s.asked} · {s.percent}%
                    </span>
                  </div>
                  <div className="timer-bar-track">
                    <div className="timer-bar-fill" style={{ width: `${s.percent}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </Layout>
  );
}
