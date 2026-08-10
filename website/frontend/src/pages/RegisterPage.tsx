import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Пароль должен быть не короче 8 символов");
      return;
    }
    setSubmitting(true);
    try {
      await register(email, password, firstName);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Не удалось зарегистрироваться");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="brand">
        <img src="/logo-icon.png" alt="Казахатомэксперт" className="brand-logo" />
        <h1>RST — RadSafe Trainer</h1>
        <p>Готовьтесь к аттестации эффективно</p>
      </div>
      <div className="auth-card">
        <form className="form" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="firstName">Имя</label>
            <input
              id="firstName"
              type="text"
              autoComplete="given-name"
              required
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
          </div>
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
          <div className="field">
            <label htmlFor="password">Пароль</label>
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
          {error && <div className="error-text">{error}</div>}
          <button className="btn btn-primary btn-block" type="submit" disabled={submitting}>
            {submitting ? "Создаём аккаунт…" : "Зарегистрироваться"}
          </button>
        </form>
      </div>
      <div className="auth-switch">
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </div>
    </div>
  );
}
