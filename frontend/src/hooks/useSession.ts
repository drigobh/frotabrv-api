import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Usuario } from "@/types/auth";

export function useMe() {
  return useQuery({ queryKey: ["me"], queryFn: () => apiGet<Usuario>("/auth/me"), retry: false });
}

// "Hoje" vem do relógio local do navegador (evita erro 404 no console)
export function useHoje(): string {
  return new Date().toISOString().split("T")[0];
}