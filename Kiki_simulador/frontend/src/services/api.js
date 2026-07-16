// services/api.js — Camada de comunicação com o backend Django

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");
  const headers = {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });

  if (response.status === 401 && token) {
    const renovado = await renovarToken();
    if (renovado) {
      headers.Authorization = `Bearer ${localStorage.getItem("access_token")}`;
      const retry = await fetch(`${BASE_URL}${endpoint}`, { ...options, headers });
      const retryData = retry.status !== 204 ? await retry.json().catch(() => null) : null;
      if (!retry.ok) throw new ApiError(retryData?.detail || "Não autorizado", retry.status, retryData);
      return retryData;
    }
    localStorage.clear();
    window.location.href = "/login";
    return;
  }

  const data = response.status !== 204 ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    const msg =
      data?.detail ||
      data?.non_field_errors?.[0] ||
      (typeof data === "object" && data ? Object.values(data).flat()[0] : null) ||
      "Erro na requisição";
    throw new ApiError(msg, response.status, data);
  }

  return data;
}

async function renovarToken() {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE_URL}/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem("access_token", data.access);
    return true;
  } catch {
    return false;
  }
}

/**
 * Descarrega um ficheiro binário (ex: relatório em PDF) autenticado e
 * despoleta o download no browser. fetch() simples não chega aqui porque
 * é preciso enviar o cabeçalho Authorization, o que um <a href> não faz.
 */
async function baixarFicheiro(endpoint, nomeFicheiro) {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { ...(token && { Authorization: `Bearer ${token}` }) },
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(data?.detail || "Não foi possível gerar o relatório.", response.status, data);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeFicheiro;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ─── Auth ────────────────────────────────────────────────────────────────────
export const authApi = {
  registo: async (dados) => {
    const data = await request("/auth/registo/", { method: "POST", body: JSON.stringify(dados) });
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    return data;
  },

  login: async (email, password) => {
    const data = await request("/auth/login/", { method: "POST", body: JSON.stringify({ email, password }) });
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    return data;
  },

  logout: async () => {
    const refresh = localStorage.getItem("refresh_token");
    try {
      await request("/auth/logout/", { method: "POST", body: JSON.stringify({ refresh }) });
    } catch {
      // mesmo que falhe no servidor, limpamos localmente
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },

  me: () => request("/auth/me/"),

  editarPerfil: (dados) => request("/auth/me/", { method: "PATCH", body: JSON.stringify(dados) }),

  pedirRecuperacao: (email) =>
    request("/auth/recuperar-password/", { method: "POST", body: JSON.stringify({ email }) }),

  confirmarRecuperacao: (uid, token, nova_password) =>
    request("/auth/redefinir-password/", { method: "POST", body: JSON.stringify({ uid, token, nova_password }) }),
};

// ─── Carteira ─────────────────────────────────────────────────────────────────
export const carteiraApi = {
  criar: (dados) => request("/carteira/criar/", { method: "POST", body: JSON.stringify(dados) }),
  obter: () => request("/carteira/"),
  posicoes: () => request("/carteira/posicoes/"),
  movimentos: () => request("/carteira/movimentos/"),
  adicionarAtivo: (dados) => request("/carteira/adicionar-ativo/", { method: "POST", body: JSON.stringify(dados) }),
  removerAtivo: (posicaoId) => request(`/carteira/posicoes/${posicaoId}/`, { method: "DELETE" }),
};

// ─── Mercado ──────────────────────────────────────────────────────────────────
export const mercadoApi = {
  listar: (tipo) => request(`/mercado/${tipo ? `?tipo=${tipo}` : ""}`),
  detalhe: (id) => request(`/mercado/${id}/`),
  historico: (id) => request(`/mercado/${id}/historico/`),
  inflacao: () => request("/mercado/inflacao/"),
};

// ─── Simulações ───────────────────────────────────────────────────────────────
export const simulacaoApi = {
  simular: (dados) => request("/simulacoes/simular/", { method: "POST", body: JSON.stringify(dados) }),
  historico: () => request("/simulacoes/"),
  comparar: (ids) => request(`/simulacoes/comparar/?ids=${ids.join(",")}`),
  relatorio: (id, nomeFicheiro) => baixarFicheiro(`/simulacoes/${id}/relatorio/`, nomeFicheiro || `simulacao_${id}.pdf`),
};

// ─── Dashboards ───────────────────────────────────────────────────────────────
export const dashboardApi = {
  investidor: () => request("/dashboard/investidor/"),
  admin: () => request("/dashboard/admin/"),
};

// ─── Administração ────────────────────────────────────────────────────────────
export const adminApi = {
  utilizadores: (q = "") => request(`/admin/utilizadores/${q ? `?q=${encodeURIComponent(q)}` : ""}`),
  bloquearUtilizador: (id) => request(`/admin/utilizadores/${id}/bloquear/`, { method: "POST" }),
  desbloquearUtilizador: (id) => request(`/admin/utilizadores/${id}/desbloquear/`, { method: "POST" }),
  excluirUtilizador: (id) => request(`/admin/utilizadores/${id}/`, { method: "DELETE" }),

  listarInflacao: () => request("/admin/inflacao/"),
  criarInflacao: (dados) => request("/admin/inflacao/", { method: "POST", body: JSON.stringify(dados) }),
  atualizarInflacao: (id, dados) =>
    request(`/admin/inflacao/${id}/`, { method: "PATCH", body: JSON.stringify(dados) }),
  eliminarInflacao: (id) => request(`/admin/inflacao/${id}/`, { method: "DELETE" }),

  listarAtivos: () => request("/admin/ativos/"),
  criarAtivo: (dados) => request("/admin/ativos/", { method: "POST", body: JSON.stringify(dados) }),
  atualizarAtivo: (id, dados) => request(`/admin/ativos/${id}/`, { method: "PATCH", body: JSON.stringify(dados) }),
  precosHistoricos: (ativoId) => request(`/admin/ativos/${ativoId}/precos/`),
  inserirPrecoHistorico: (ativoId, dados) =>
    request(`/admin/ativos/${ativoId}/precos/`, { method: "POST", body: JSON.stringify(dados) }),

  logs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/admin/logs/${query ? `?${query}` : ""}`);
  },
  relatorioLogs: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return baixarFicheiro(`/admin/logs/relatorio/${query ? `?${query}` : ""}`, "relatorio_logs.pdf");
  },

  monitor: () => request("/admin/monitor/"),
};
