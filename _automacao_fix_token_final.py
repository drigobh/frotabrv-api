import os

def fix_backend_login(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "auth.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garante que a resposta do login contenha o token no corpo
    if 'return {"requires_2fa": False, "user": user, "token": token}' not in c:
        c = c.replace(
            'return {"requires_2fa": False, "user": user}',
            'return {"requires_2fa": False, "user": user, "token": token}'
        )
        # Fallback se o retorno for outro
        c = c.replace(
            'return {"user": user}',
            'return {"user": user, "token": token}'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de login agora retorna o token.")
    else:
        print("ℹ️ Backend: Rota de login já estava correta.")

def fix_session(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "lib", "session.ts")
    codigo = r'''import { queryClient } from "./queryClient";
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
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ session.ts reescrito: Agora salva o token.")

def fix_login(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adapta a chamada beginSession para passar o token retornado
    if 'beginSession(r.token)' not in c:
        c = c.replace('beginSession();', 'beginSession(r.token);')
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Login.tsx: beginSession agora recebe o token.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend_login(raiz)
    fix_session(raiz)
    fix_login(raiz)