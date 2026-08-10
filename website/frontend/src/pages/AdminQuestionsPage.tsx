import { useCallback, useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Layout } from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import type { QuestionListResponse, Section } from "../api/types";

const PAGE_SIZE = 20;

export function AdminQuestionsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [sections, setSections] = useState<Section[]>([]);
  const [section, setSection] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<QuestionListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(() => {
    const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
    if (section) params.set("section", section);
    if (search) params.set("search", search);

    api
      .get<QuestionListResponse>(`/api/admin/questions?${params.toString()}`)
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить вопросы"));
  }, [page, section, search]);

  useEffect(() => {
    if (user?.is_admin) load();
  }, [user, load]);

  useEffect(() => {
    if (user?.is_admin) {
      api.get<Section[]>("/api/sections").then(setSections).catch(() => {});
    }
  }, [user]);

  if (user && !user.is_admin) {
    return <Navigate to="/" replace />;
  }

  async function handleDelete(id: number) {
    if (!confirm("Удалить этот вопрос?")) return;
    setBusyId(id);
    try {
      await api.delete(`/api/admin/questions/${id}`);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось удалить вопрос");
    } finally {
      setBusyId(null);
    }
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <Layout title="Админ · Вопросы">
      <button className="btn btn-primary btn-block" onClick={() => navigate("/admin/questions/new")}>
        + Добавить вопрос
      </button>

      <div className="form">
        <div className="field">
          <label htmlFor="search">Поиск</label>
          <input
            id="search"
            type="text"
            value={search}
            onChange={(e) => {
              setPage(1);
              setSearch(e.target.value);
            }}
            placeholder="Текст вопроса или ответа"
          />
        </div>
        <div className="field">
          <label htmlFor="section">Раздел</label>
          <select
            id="section"
            value={section}
            onChange={(e) => {
              setPage(1);
              setSection(e.target.value);
            }}
          >
            <option value="">Все разделы</option>
            {sections.map((s) => (
              <option key={s.name} value={s.name}>
                {s.name} ({s.count})
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="card error-text">{error}</div>}

      {data && (
        <>
          <div className="list">
            {data.items.map((q) => (
              <div key={q.id} className="list-item" style={{ cursor: "default", alignItems: "flex-start" }}>
                <span onClick={() => navigate(`/admin/questions/${q.id}`)} style={{ cursor: "pointer", flex: 1 }}>
                  <strong>#{q.id}</strong> {q.question.slice(0, 90)}
                  {q.question.length > 90 ? "…" : ""}
                  <div className="count" style={{ marginTop: 4, display: "inline-block" }}>
                    {q.section}
                  </div>
                </span>
                <button
                  className="btn btn-ghost"
                  disabled={busyId === q.id}
                  onClick={() => handleDelete(q.id)}
                >
                  Удалить
                </button>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <button className="btn btn-ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              ← Назад
            </button>
            <span className="test-progress">
              Стр. {data.page} из {totalPages} ({data.total})
            </span>
            <button className="btn btn-ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              Далее →
            </button>
          </div>
        </>
      )}
    </Layout>
  );
}
