import { queryClient } from "./queryClient";
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
