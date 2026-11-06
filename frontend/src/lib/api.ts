const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000/api";

export class ApiError extends Error {
  public status: number;
  public body: any;
  constructor(status: number, body: any, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function getHeaders() {
  const token = localStorage.getItem("token") || localStorage.getItem("auth_token");
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

// Interceptor para evitar chamadas sem token
const originalFetch = window.fetch;
window.fetch = function (input: RequestInfo | URL, init?: RequestInit) {
  const url = typeof input === 'string' ? input : input.toString();
  if (url.includes('/auth/me')) {
    const token = localStorage.getItem("token") || localStorage.getItem("auth_token");
    if (!token) {
      return Promise.reject(new Error("Sem token - ignorando /auth/me"));
    }
  }
  return originalFetch.apply(this, [input, init]);
};

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const msg = errorData.detail || errorData.message || `Erro ${res.status}`;
    throw new ApiError(res.status, errorData, typeof msg === "string" ? msg : "Erro na requisição");
  }
  if (res.status === 204) return {} as T;
  return res.json();
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { headers: getHeaders(), credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiPost<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "POST", headers: getHeaders(), body: body ? JSON.stringify(body) : undefined, credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiPut<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "PUT", headers: getHeaders(), body: body ? JSON.stringify(body) : undefined, credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiPatch<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "PATCH", headers: getHeaders(), body: body ? JSON.stringify(body) : undefined, credentials: "include" });
  return handleResponse<T>(res);
}
export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { method: "DELETE", headers: getHeaders(), credentials: "include" });
  return handleResponse<T>(res);
}
