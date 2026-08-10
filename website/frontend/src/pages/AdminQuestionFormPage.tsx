import { useEffect, useState, type FormEvent } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { Layout } from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import type { QuestionAdmin, QuestionSaveInput } from "../api/types";

const EMPTY: QuestionSaveInput = {
  section: "",
  subsection: "",
  question: "",
  answer: "",
  wrong1: "",
  wrong2: "",
  wrong3: "",
  wrong4: "",
};

export function AdminQuestionFormPage() {
  const { user } = useAuth();
  const { id } = useParams<{ id: string }>();
  const isNew = !id || id === "new";
  const navigate = useNavigate();

  const [form, setForm] = useState<QuestionSaveInput>(EMPTY);
  const [loading, setLoading] = useState(!isNew);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isNew || !user?.is_admin) return;
    api
      .get<QuestionAdmin>(`/api/admin/questions/${id}`)
      .then((q) => setForm(q))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить вопрос"))
      .finally(() => setLoading(false));
  }, [id, isNew, user]);

  if (user && !user.is_admin) {
    return <Navigate to="/" replace />;
  }

  function update<K extends keyof QuestionSaveInput>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (isNew) {
        await api.post("/api/admin/questions", form);
      } else {
        await api.put(`/api/admin/questions/${id}`, form);
      }
      navigate("/admin/questions");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось сохранить вопрос");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <Layout title="Админ · Вопрос">
        <div className="spinner-wrap">Загрузка…</div>
      </Layout>
    );
  }

  return (
    <Layout title={isNew ? "Новый вопрос" : `Вопрос #${id}`}>
      <form className="form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="section">Раздел</label>
          <input id="section" required value={form.section} onChange={(e) => update("section", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="subsection">Подраздел</label>
          <input
            id="subsection"
            required
            value={form.subsection}
            onChange={(e) => update("subsection", e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="question">Текст вопроса</label>
          <textarea id="question" required value={form.question} onChange={(e) => update("question", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="answer">Правильный ответ</label>
          <textarea id="answer" required value={form.answer} onChange={(e) => update("answer", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="wrong1">Неверный вариант 1</label>
          <textarea id="wrong1" required value={form.wrong1} onChange={(e) => update("wrong1", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="wrong2">Неверный вариант 2</label>
          <textarea id="wrong2" required value={form.wrong2} onChange={(e) => update("wrong2", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="wrong3">Неверный вариант 3</label>
          <textarea id="wrong3" required value={form.wrong3} onChange={(e) => update("wrong3", e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="wrong4">Неверный вариант 4</label>
          <textarea id="wrong4" required value={form.wrong4} onChange={(e) => update("wrong4", e.target.value)} />
        </div>

        {error && <div className="error-text">{error}</div>}

        <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
          {submitting ? "Сохраняем…" : "Сохранить"}
        </button>
        <button className="btn btn-ghost btn-block" type="button" onClick={() => navigate("/admin/questions")}>
          Отмена
        </button>
      </form>
    </Layout>
  );
}
