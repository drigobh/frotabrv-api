import os

def fix_session(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "hooks", "useSession.ts")
    if not os.path.exists(caminho):
        print("❌ Arquivo useSession.ts não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Se não tiver a palavra "token" na lógica, o hook está tentando buscar sem parar
    if 'localStorage.getItem("token")' not in c:
        codigo = r'''import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: () => apiGet<any>("/auth/me"),
    retry: false, // Não fica tentando se der erro
    enabled: !!localStorage.getItem("token"), // Só busca se tiver token
  });
}

export function useHoje() {
  return new Date().toISOString().split("T")[0];
}
'''
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(codigo)
        print("✅ Hook useSession.ts reescrito: Loop infinito evitado.")
    else:
        print("ℹ️ O useSession.ts já possui a verificação de token.")

if __name__ == "__main__":
    fix_session(os.getcwd())