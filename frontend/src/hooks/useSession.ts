import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { ApiRoot, Usuario } from "@/types/auth";

export function useMe() {
  return useQuery({ queryKey: ["me"], queryFn: () => apiGet<Usuario>("/auth/me"), retry: false });
}

// "Hoje" vem do servidor (fuso America/Sao_Paulo), nunca do relógio do navegador.
export function useHoje(): string {
  const q = useQuery({ queryKey: ["hoje"], queryFn: () => apiGet<ApiRoot>("/"), staleTime: 60 * 60 * 1000 });
  return q.data?.hoje ?? "";
}
