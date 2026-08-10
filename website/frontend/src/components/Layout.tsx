import type { ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Layout({ title, children, hideNav }: { title: string; children: ReactNode; hideNav?: boolean }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <span className="logo">☢</span>
        <h1>{title}</h1>
        <span className="spacer" />
        <button className="icon-btn" onClick={handleLogout} title="Выйти" aria-label="Выйти">
          ⏻
        </button>
      </header>
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
        </nav>
      )}
    </div>
  );
}
