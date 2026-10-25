import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";

export function useMe() {
  const token = localStorage.getItem("token");
  
  return useQuery({
    queryKey: ["me"],
    queryFn: () => apiGet<any>("/auth/me"),
    retry: false,
    enabled: !!token,
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}

export function useHoje() {
  return new Date().toISOString().split("T")[0];
}
