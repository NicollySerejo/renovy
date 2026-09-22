import React, { createContext, useContext, useState, useCallback } from "react";

interface Session {
  token: string;
  role: string;
  nome: string;
}

interface AuthContextValue {
  session: Session | null;
  login: (s: Session) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function readSession(): Session | null {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");
  const nome = localStorage.getItem("nome");
  if (!token || !role) return null;
  return { token, role, nome: nome || "" };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(readSession());

  const login = useCallback((s: Session) => {
    localStorage.setItem("token", s.token);
    localStorage.setItem("role", s.role);
    localStorage.setItem("nome", s.nome);
    setSession(s);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("nome");
    setSession(null);
  }, []);

  return <AuthContext.Provider value={{ session, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de AuthProvider");
  return ctx;
}
