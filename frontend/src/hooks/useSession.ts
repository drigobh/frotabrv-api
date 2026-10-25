import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => apiGet<any>("/auth/me"),
    retry: false,
    staleTime: 1000 * 60 * 5,
    refetchOnWindowFocus: false,
    // Removemos o 'enabled' para que ele sempre tente buscar o usuário via Cookie
  });
}

export function useHoje() {
  return new Date().toISOString().split("T")[0];
}
