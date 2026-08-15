import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { MessageResponse } from "../api/types";

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [status, setStatus] = useState<"pending" | "done" | "error">("pending");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Ссылка недействительна — токен отсутствует.");
      return;
    }

    api
      .post<MessageResponse>("/api/auth/verify-email", { token })
      .then((res) => {
        setStatus("done");
        setMessage(res.message);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(err instanceof ApiError ? err.message : "Не удалось подтвердить email");
      });
  }, [token]);

  return (
    <div className="auth-page">
      <div className="brand">
        <img src="/logo-icon.png" alt="Казахатомэксперт" className="brand-logo" />
        <h1>Подтверждение email</h1>
      </div>
      <div className="auth-card">
        {status === "pending" && <p>Проверяем ссылку…</p>}
        {status !== "pending" && <p>{message}</p>}
      </div>
      <div className="auth-switch">
        <Link to="/login">Вернуться ко входу</Link>
      </div>
    </div>
  );
}
