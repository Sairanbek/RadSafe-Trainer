import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Layout } from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import { useModule } from "../context/ModuleContext";
import type { StartTestResponse, StatsResponse } from "../api/types";

export function DashboardPage() {
  const { refreshMe } = useAuth();
  const { module, setModule, modules } = useModule();
  const navigate = useNavigate();

  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [mistakes, setMistakes] = useState<number | null>(null);

  useEffect(() => {
    refreshMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Цифры пересчитываются при смене направления.
  useEffect(() => {
    const q = `?module=${encodeURIComponent(module)}`;
    api.get<StatsResponse>(`/api/stats${q}`).then(setStats).catch(() => setStats(null));
    api
      .get<{ count: number }>(`/api/mistakes/count${q}`)
      .then((r) => setMistakes(r.count))
      .catch(() => setMistakes(null));
  }, [module, busy]);

  async function startDirect(mode: "exam" | "mistakes") {
    setBusy(true);
    setNotice(null);
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", { mode, module });
      if (!res.session_id || !res.question) {
        setNotice(res.message ?? "Вопросы не найдены");
        return;
      }
      navigate(`/test/${res.session_id}`, { state: { start: res } });
    } catch (err) {
      setNotice(err instanceof ApiError ? err.message : "Не удалось начать тест");
    } finally {
      setBusy(false);
      refreshMe();
    }
  }

  return (
    <Layout title="RST — RadSafe Trainer">
      {modules.length > 1 && (
        <div className="module-switch">
          <div className="module-switch-label">Направление подготовки</div>
          <div className="module-chips">
            {modules.map((m) => (
              <button
                key={m.name}
                className={`module-chip${m.name === module ? " active" : ""}`}
                onClick={() => setModule(m.name)}
              >
                {m.name}
                <span className="module-chip-count">{m.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="stat-grid">
        <div className="stat-tile">
          <div className="value">{stats?.tests_count ?? 0}</div>
          <div className="label">Пройдено тестов</div>
        </div>
        <div className="stat-tile">
          <div className="value">{stats?.average_percent ?? 0}%</div>
          <div className="label">Средний результат</div>
        </div>
      </div>

      {notice && <div className="card">{notice}</div>}

      <div className="mode-list">
        <button className="mode-btn" onClick={() => navigate("/training/sections")}>
          <span className="emoji">📝</span>
          <span>
            <div className="title">Тренировка</div>
            <div className="subtitle">По разделам, без ограничения времени</div>
          </span>
          <span className="chev">›</span>
        </button>

        <button className="mode-btn" disabled={busy} onClick={() => startDirect("exam")}>
          <span className="emoji">☢</span>
          <span>
            <div className="title">Аттестация</div>
            <div className="subtitle">50 вопросов, 75 минут</div>
          </span>
          <span className="chev">›</span>
        </button>

        <button className="mode-btn" disabled={busy} onClick={() => startDirect("mistakes")}>
          <span className="emoji">🔁</span>
          <span>
            <div className="title">Мои ошибки</div>
            <div className="subtitle">{mistakes ?? 0} вопрос(ов) на повторении</div>
          </span>
          <span className="chev">›</span>
        </button>

        <button className="mode-btn" onClick={() => navigate("/training/sections?mode=learning")}>
          <span className="emoji">📖</span>
          <span>
            <div className="title">Обучение</div>
            <div className="subtitle">Правильный ответ виден сразу, без баллов</div>
          </span>
          <span className="chev">›</span>
        </button>
      </div>
    </Layout>
  );
}
