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

export function useAcoesApi() {
  const { data: me, isError } = useMe();
  const acoes = !me || isError ? [] : Array.isArray(me.acoes_api) ? me.acoes_api
    : me.perfil === "admin" ? ["read", "write", "delete"]
      : me.perfil === "operador" ? ["read", "write"] : [];
  return {
    podeLer: acoes.includes("read"),
    podeEscrever: acoes.includes("write"),
    podeExcluir: acoes.includes("delete"),
  };
}

export function useHoje() {
  return new Date().toISOString().split("T")[0];
}
