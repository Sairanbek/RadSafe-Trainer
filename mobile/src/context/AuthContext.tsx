import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { api, clearTokens, getAccessToken, getRefreshToken, setTokens } from "../api/client";
import type { Me, TokenResponse } from "../api/types";

interface AuthContextValue {
  user: Me | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName: string, consentAiTransfer: boolean) => Promise<void>;
  logout: () => Promise<void>;
  refreshMe: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const token = await getAccessToken();
    if (!token) {
      setUser(null);
      return;
    }
    try {
      const me = await api.get<Me>("/api/auth/me");
      setUser(me);
    } catch {
      await clearTokens();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    refreshMe().finally(() => setLoading(false));
  }, [refreshMe]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post<TokenResponse>("/api/auth/login", { email, password });
    await setTokens(res.access_token, res.refresh_token);
    await refreshMe();
  }, [refreshMe]);

  const register = useCallback(
    async (email: string, password: string, firstName: string, consentAiTransfer: boolean) => {
      const res = await api.post<TokenResponse>("/api/auth/register", {
        email,
        password,
        first_name: firstName,
        consent_ai_transfer: consentAiTransfer,
      });
      await setTokens(res.access_token, res.refresh_token);
      await refreshMe();
    },
    [refreshMe],
  );

  const logout = useCallback(async () => {
    const refreshToken = await getRefreshToken();
    if (refreshToken) {
      try {
        await api.post("/api/auth/logout", { refresh_token: refreshToken });
      } catch {
        /* лучшее усилие — не блокируем выход из UI */
      }
    }
    await clearTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshMe }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
