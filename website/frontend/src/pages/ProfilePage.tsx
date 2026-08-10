import { useState, type FormEvent } from "react";
import { Layout } from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { api, ApiError } from "../api/client";
import type { MessageResponse, User } from "../api/types";

export function ProfilePage() {
  const { user, refreshMe } = useAuth();

  const [firstName, setFirstName] = useState(user?.first_name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [profileMessage, setProfileMessage] = useState<string | null>(null);
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSubmitting, setProfileSubmitting] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordMessage, setPasswordMessage] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSubmitting, setPasswordSubmitting] = useState(false);

  async function handleProfileSubmit(e: FormEvent) {
    e.preventDefault();
    setProfileError(null);
    setProfileMessage(null);
    setProfileSubmitting(true);
    try {
      await api.patch<User>("/api/auth/me", { first_name: firstName, email });
      await refreshMe();
      setProfileMessage("Профиль обновлён");
    } catch (err) {
      setProfileError(err instanceof ApiError ? err.message : "Не удалось обновить профиль");
    } finally {
      setProfileSubmitting(false);
    }
  }

  async function handlePasswordSubmit(e: FormEvent) {
    e.preventDefault();
    setPasswordError(null);
    setPasswordMessage(null);

    if (newPassword.length < 8) {
      setPasswordError("Новый пароль должен быть не короче 8 символов");
      return;
    }

    setPasswordSubmitting(true);
    try {
      const res = await api.post<MessageResponse>("/api/auth/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordMessage(res.message);
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordError(err instanceof ApiError ? err.message : "Не удалось изменить пароль");
    } finally {
      setPasswordSubmitting(false);
    }
  }

  return (
    <Layout title="Профиль">
      <div className="card">
        <h3>Личные данные</h3>
        <form className="form" onSubmit={handleProfileSubmit}>
          <div className="field">
            <label htmlFor="firstName">Имя</label>
            <input
              id="firstName"
              type="text"
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
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          {profileMessage && <div className="feedback-banner correct">{profileMessage}</div>}
          {profileError && <div className="error-text">{profileError}</div>}
          <button className="btn btn-primary btn-block" type="submit" disabled={profileSubmitting}>
            {profileSubmitting ? "Сохраняем…" : "Сохранить"}
          </button>
        </form>
      </div>

      <div className="card">
        <h3>Смена пароля</h3>
        <form className="form" onSubmit={handlePasswordSubmit}>
          <div className="field">
            <label htmlFor="currentPassword">Текущий пароль</label>
            <input
              id="currentPassword"
              type="password"
              autoComplete="current-password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
            />
          </div>
          <div className="field">
            <label htmlFor="newPassword">Новый пароль</label>
            <input
              id="newPassword"
              type="password"
              autoComplete="new-password"
              required
              minLength={8}
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
            />
          </div>
          {passwordMessage && <div className="feedback-banner correct">{passwordMessage}</div>}
          {passwordError && <div className="error-text">{passwordError}</div>}
          <button className="btn btn-primary btn-block" type="submit" disabled={passwordSubmitting}>
            {passwordSubmitting ? "Меняем…" : "Изменить пароль"}
          </button>
        </form>
      </div>
    </Layout>
  );
}
