import { useState, type ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import type { MessageResponse } from "../api/types";

export function Layout({ title, children, hideNav }: { title: string; children: ReactNode; hideNav?: boolean }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [resendMessage, setResendMessage] = useState<string | null>(null);
  const [resending, setResending] = useState(false);

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  async function handleResend() {
    setResending(true);
    try {
      const res = await api.post<MessageResponse>("/api/auth/resend-verification");
      setResendMessage(res.message);
    } catch (err) {
      setResendMessage(err instanceof ApiError ? err.message : "Не удалось отправить письмо");
    } finally {
      setResending(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <img src="/logo-icon.png" alt="Казахатомэксперт" className="logo-icon" />
        <h1>{title}</h1>
        <span className="spacer" />
        {user?.is_admin && (
          <button
            className="icon-btn"
            onClick={() => navigate("/admin/questions")}
            title="Админ-панель"
            aria-label="Админ-панель"
          >
            🛠
          </button>
        )}
        <button className="icon-btn" onClick={handleLogout} title="Выйти" aria-label="Выйти">
          ⏻
        </button>
      </header>
      {user && !user.email_verified && (
        <div className="verify-banner">
          {resendMessage ?? (
            <>
              Email не подтверждён.{" "}
              <button className="link-btn" onClick={handleResend} disabled={resending}>
                {resending ? "Отправляем…" : "Отправить письмо ещё раз"}
              </button>
            </>
          )}
        </div>
      )}
      <main className="page">{children}</main>
      {!hideNav && (
        <nav className="bottom-nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            <span className="nav-emoji">🏠</span>
            Главная
          </NavLink>
          <NavLink to="/stats" className={({ isActive }) => (isActive ? "active" : "")}>
            <span className="nav-emoji">📊</span>
            Статистика
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => (isActive ? "active" : "")}>
            <span className="nav-emoji">🕘</span>
            История
          </NavLink>
          <NavLink to="/profile" className={({ isActive }) => (isActive ? "active" : "")}>
            <span className="nav-emoji">👤</span>
            Профиль
          </NavLink>
          <NavLink to="/assistant" className={({ isActive }) => (isActive ? "active" : "")}>
            <span className="nav-emoji">🤖</span>
            ИИ
          </NavLink>
        </nav>
      )}
    </div>
  );
}
