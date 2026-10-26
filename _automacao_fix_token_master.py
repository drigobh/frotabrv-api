import os
import re

def fix_backend(raiz):
    # 1. Adicionar o campo token no Modelo LoginOut (se não existir)
    model_path = os.path.join(raiz, "app", "backend", "models", "auth.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'class LoginOut' in c and 'token:' not in c:
        c = c.replace('class LoginOut(BaseModel):', 'class LoginOut(BaseModel):\n    token: str | None = None')
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Modelo LoginOut atualizado com campo 'token'.")

    # 2. Retornar o token no Router de Auth
    router_path = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Substitui o retorno para incluir o token
    if 'return LoginOut(requires_2fa=False, user=user)' in c:
        c = c.replace(
            'return LoginOut(requires_2fa=False, user=user)',
            'return LoginOut(requires_2fa=False, user=user, token=token)'
        )
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router Auth atualizado para retornar o token.")

def fix_frontend(raiz):
    # 1. Atualizar session.ts para salvar o token
    session_path = os.path.join(raiz, "frontend", "src", "lib", "session.ts")
    codigo_session = '''import { queryClient } from "./queryClient";
import { apiPost } from "./api";

export function beginSession(token?: string): void {
  if (token) {
    localStorage.setItem("token", token);
    localStorage.setItem("auth_token", token);
  }
  queryClient.clear();
}

export async function endSession(redirectTo: string = "/login"): Promise<void> {
  try {
    await apiPost("/auth/logout");
  } finally {
    localStorage.removeItem("token");
    localStorage.removeItem("auth_token");
    queryClient.clear();
    window.location.assign(redirectTo);
  }
}
'''
    with open(session_path, 'w', encoding='utf-8') as f:
        f.write(codigo_session)
    print("✅ session.ts atualizado.")

    # 2. Atualizar Login.tsx para passar o token
    login_path = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    with open(login_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'beginSession(r.token)' not in c:
        c = c.replace('beginSession();', 'beginSession(r.token);')
        with open(login_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Login.tsx atualizado para passar o token ao beginSession.")

    # 3. Atualizar api.ts para usar o token
    api_path = os.path.join(raiz, "frontend", "src", "lib", "api.ts")
    with open(api_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'credentials: "include"' in c and 'localStorage.getItem("token")' not in c:
        # Se o api.ts não tem a função getHeaders com token, vamos reescrevê-lo
        codigo_api = '''const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000/api";

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
'''
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(codigo_api)
        print("✅ api.ts reescrito para usar o token do localStorage.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)