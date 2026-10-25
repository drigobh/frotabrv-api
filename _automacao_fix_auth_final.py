import os

def fix_backend_token(raiz):
    # Aumenta o tempo de expiração do token no Backend
    caminho = os.path.join(raiz, "app", "backend", "lib", "security.py")
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as f:
            c = f.read()
        
        # Altera a expiração do token para 30 dias (padrão do JWT)
        c = c.replace('expire=timedelta(hours=2)', 'expire=timedelta(days=30)')
        c = c.replace('expire=timedelta(minutes=30)', 'expire=timedelta(days=30)')
        c = c.replace('expire=timedelta(minutes=60)', 'expire=timedelta(days=30)')
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Tempo de expiração do token aumentado para 30 dias.")

def fix_frontend_session(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "hooks", "useSession.ts")
    
    codigo = r'''import { useQuery } from "@tanstack/react-query";
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
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend: Hook useMe corrigido (sem loop).")

def fix_frontend_login(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    if not os.path.exists(caminho):
        print("⚠️ Arquivo Login.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garantir que o Login salve o token e recarregue a página
    if 'window.location.href = "/"' not in c:
        c = c.replace(
            'onSuccess: (data) => {',
            '''onSuccess: (data) => {
        if (data && data.token) {
          localStorage.setItem("token", data.token);
        }'''
        )
        c = c.replace(
            'localStorage.setItem("token", data.token);\n          // Redireciona',
            'localStorage.setItem("token", data.token);\n          window.location.href = "/";'
        )
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Frontend: Login corrigido para salvar o token e recarregar.")
    else:
        print("ℹ️ O Login.tsx já parece estar configurado corretamente.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend_token(raiz)
    fix_frontend_session(raiz)
    fix_frontend_login(raiz)