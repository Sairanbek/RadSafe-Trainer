import { useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { MessageResponse } from "../api/types";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const navigate = useNavigate();

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("Пароль должен быть не короче 8 символов");
      return;
    }
    if (password !== confirm) {
      setError("Пароли не совпадают");
      return;
    }

    setSubmitting(true);
    try {
      await api.post<MessageResponse>("/api/auth/reset-password", { token, new_password: password });
      navigate("/login", { replace: true, state: { resetDone: true } });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось изменить пароль");
    } finally {
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <p>Ссылка недействительна — токен отсутствует.</p>
        </div>
        <div className="auth-switch">
          <Link to="/forgot-password">Запросить новую ссылку</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="brand">
        <div className="emoji">☢</div>
        <h1>Новый пароль</h1>
      </div>
      <div className="auth-card">
        <form className="form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="password">Новый пароль</label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="confirm">Повторите пароль</label>
            <input
              id="confirm"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
            />
          </div>
          {error && <div className="error-text">{error}</div>}
          <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
            {submitting ? "Сохраняем…" : "Сохранить пароль"}
          </button>
        </form>
      </div>
    </div>
  );
}
