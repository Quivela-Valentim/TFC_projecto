// store/AuthContext.jsx
import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { authApi } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [carregando, setCarregando] = useState(true);

  const carregarPerfil = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setCarregando(false);
      return;
    }
    try {
      const dados = await authApi.me();
      setUser(dados);
    } catch {
      localStorage.clear();
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    carregarPerfil();
  }, [carregarPerfil]);

  const login = async (email, password) => {
    const dados = await authApi.login(email, password);
    setUser(dados.user || (await authApi.me()));
    return dados;
  };

  const registar = async (dados) => {
    const resposta = await authApi.registo(dados);
    setUser(resposta.user);
    return resposta;
  };

  const logout = async () => {
    await authApi.logout();
    setUser(null);
  };

  const atualizarUser = (parcial) => setUser((atual) => ({ ...atual, ...parcial }));

  return (
    <AuthContext.Provider
      value={{ user, setUser, login, registar, logout, atualizarUser, carregando, recarregar: carregarPerfil }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de AuthProvider");
  return ctx;
};
