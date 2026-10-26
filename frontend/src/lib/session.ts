import { queryClient } from "./queryClient";
import { apiPost } from "./api";

// Salva o token no localStorage e limpa o cache do React Query
export function beginSession(token?: string): void {
  if (token) {
    localStorage.setItem("token", token);
    localStorage.setItem("auth_token", token);
  }
  queryClient.clear();
}

// Limpa o token e o cache
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
