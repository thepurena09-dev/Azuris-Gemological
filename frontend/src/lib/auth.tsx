import * as React from "react";
import { apiFetch, apiJson, unwrap, clearTokens, getToken, setTokens } from "@/lib/api";

interface AdminInfo {
  uuid: string;
  email: string;
  full_name: string;
  role: string;
}

interface AuthContextValue {
  admin: AdminInfo | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [admin, setAdmin] = React.useState<AdminInfo | null>(null);
  const [ready, setReady] = React.useState(false);

  React.useEffect(() => {
    (async () => {
      if (getToken()) {
        try {
          const me = await apiJson<AdminInfo>("/api/auth/me");
          setAdmin(me);
        } catch {
          clearTokens();
        }
      }
      setReady(true);
    })();
  }, []);

  const login = React.useCallback(async (email: string, password: string) => {
    const res = await apiFetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("login_failed");
    const data = await unwrap(res);
    setTokens(data.access_token, data.refresh_token);
    setAdmin(data.admin as AdminInfo);
  }, []);

  const logout = React.useCallback(async () => {
    try {
      await apiFetch("/api/auth/logout", {
        method: "POST",
        body: JSON.stringify({ all_devices: true }),
      });
    } catch {
      /* logout is best-effort */
    }
    clearTokens();
    setAdmin(null);
  }, []);

  const value = React.useMemo(
    () => ({ admin, ready, login, logout }),
    [admin, ready, login, logout]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export function useAuth(): AuthContextValue {
  const ctx = React.useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
