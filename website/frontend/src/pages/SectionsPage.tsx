import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Layout } from "../components/Layout";
import { api, ApiError } from "../api/client";
import type { Section, StartTestResponse, Subsection } from "../api/types";

export function SectionsPage() {
  const navigate = useNavigate();
  const [sections, setSections] = useState<Section[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busySection, setBusySection] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Section[]>("/api/sections")
      .then(setSections)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить разделы"));
  }, []);

  async function startTraining(section: string, subsection?: string) {
    setBusySection(section + (subsection ?? ""));
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", {
        mode: "training",
        section,
        subsection,
      });
      if (!res.session_id || !res.question) {
        setError(res.message ?? "Вопросы не найдены");
        return;
      }
      navigate(`/test/${res.session_id}`, { state: { start: res } });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось начать тренировку");
    } finally {
      setBusySection(null);
    }
  }

  async function handlePick(section: string) {
    setBusySection(section);
    setError(null);
    try {
      const subs = await api.get<Subsection[]>(`/api/subsections?section=${encodeURIComponent(section)}`);
      if (subs.length > 0) {
        navigate(`/training/sections/${encodeURIComponent(section)}/subsections`);
      } else {
        await startTraining(section);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось загрузить раздел");
    } finally {
      setBusySection(null);
    }
  }

  return (
    <Layout title="Выбор раздела">
      {error && <div className="card error-text">{error}</div>}
      {!sections && !error && <div className="spinner-wrap">Загрузка…</div>}
      {sections && (
        <div className="list">
          <button
            className="list-item"
            disabled={busySection === "ALL"}
            onClick={() => startTraining("ALL")}
          >
            <span>🎲 Все разделы</span>
          </button>
          {sections.map((s) => (
            <button
              key={s.name}
              className="list-item"
              disabled={busySection === s.name}
              onClick={() => handlePick(s.name)}
            >
              <span>{s.name}</span>
              <span className="count">{s.count}</span>
            </button>
          ))}
        </div>
      )}
    </Layout>
  );
}
