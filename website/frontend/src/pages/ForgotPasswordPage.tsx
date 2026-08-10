import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { MessageResponse } from "../api/types";

export function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await api.post<MessageResponse>("/api/auth/forgot-password", { email });
      setMessage(res.message);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось отправить запрос");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="brand">
        <div className="emoji">☢</div>
        <h1>Восстановление пароля</h1>
        <p>Укажите email, привязанный к аккаунту</p>
      </div>
      <div className="auth-card">
        {message ? (
          <p>{message}</p>
        ) : (
          <form className="form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            {error && <div className="error-text">{error}</div>}
            <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
              {submitting ? "Отправляем…" : "Отправить ссылку"}
            </button>
          </form>
        )}
      </div>
      <div className="auth-switch">
        <Link to="/login">Вернуться ко входу</Link>
      </div>
    </div>
  );
}
