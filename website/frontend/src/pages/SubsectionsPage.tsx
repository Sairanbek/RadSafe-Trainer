import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { Layout } from "../components/Layout";
import { api, ApiError } from "../api/client";
import { useModule } from "../context/ModuleContext";
import type { Mode, StartTestResponse, Subsection } from "../api/types";

export function SubsectionsPage() {
  const { section: encodedSection } = useParams<{ section: string }>();
  const section = decodeURIComponent(encodedSection ?? "");
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const mode = (searchParams.get("mode") as Mode) || "training";
  const { module } = useModule();
  const [subsections, setSubsections] = useState<Subsection[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Subsection[]>(
        `/api/subsections?section=${encodeURIComponent(section)}&module=${encodeURIComponent(module)}`,
      )
      .then(setSubsections)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Не удалось загрузить подразделы"));
  }, [section, module]);

  const totalCount = subsections?.reduce((sum, s) => sum + s.count, 0) ?? 0;

  async function start(subsection?: string) {
    setBusy(subsection ?? "ALL");
    setError(null);
    try {
      const res = await api.post<StartTestResponse>("/api/tests/start", {
        mode,
        module,
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
      setBusy(null);
    }
  }

  return (
    <Layout title={section}>
      {error && <div className="card error-text">{error}</div>}
      {!subsections && !error && <div className="spinner-wrap">Загрузка…</div>}
      {subsections && (
        <div className="list">
          <button className="list-item" disabled={busy === "ALL"} onClick={() => start(undefined)}>
            <span>🎲 Весь раздел</span>
            <span className="count">{totalCount}</span>
          </button>
          {subsections.map((s) => (
            <button
              key={s.name}
              className="list-item"
              disabled={busy === s.name}
              onClick={() => start(s.name)}
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
