import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Layout } from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import type { StartTestResponse } from "../api/types";

export function DashboardPage() {
  const { user, refreshMe } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    refreshMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function startDirect(mode: "exam" | "mistakes") {
    setBusy(true);
    setNotice(null);
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", { mode });
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
      <div className="stat-grid">
        <div className="stat-tile">
          <div className="value">{user?.tests_count ?? 0}</div>
          <div className="label">Пройдено тестов</div>
        </div>
        <div className="stat-tile">
          <div className="value">{user?.average_percent ?? 0}%</div>
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
            <div className="subtitle">{user?.mistakes_count ?? 0} вопрос(ов) на повторении</div>
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
