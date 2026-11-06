import os
import re

# ==========================================
# 1. CRIAR FUNÇÃO DE LOGOFF NUCLEAR
# ==========================================
path_logoff = os.path.join(os.getcwd(), "frontend", "src", "lib", "logoff.ts")

conteudo = r'''export function realizarLogoff() {
  // 1. Limpa TODO o armazenamento
  localStorage.clear();
  sessionStorage.clear();
  
  // 2. Limpa cookies (se houver)
  document.cookie.split(";").forEach((c) => {
    document.cookie = c
      .replace(/^ +/, "")
      .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
  });

  // 3. Força o redirecionamento para o login com um parâmetro que indica logoff
  window.location.replace("/login?logoff=true");
}
'''

with open(path_logoff, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Função de logoff nuclear criada.")

# ==========================================
# 2. ATUALIZAR O SIDEBAR
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    c = f.read()

# Remove qualquer função de logoff antiga
c = re.sub(r'const handleLogoff = \(\) => \{[\s\S]*?\};', '', c)

# Adiciona o import
if "realizarLogoff" not in c:
    c = c.replace(
        'import { useMe } from "@/hooks/useSession";',
        'import { useMe } from "@/hooks/useSession";\nimport { realizarLogoff } from "@/lib/logoff";'
    )

# Substitui o onClick do botão Sair
c = re.sub(
    r'onClick=\{[^}]*handleLogoff[^}]*\}',
    'onClick={realizarLogoff}',
    c
)
c = re.sub(
    r'onClick=\{\(\) => \{.*?localStorage.*?\}\}',
    'onClick={realizarLogoff}',
    c
)

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Sidebar: Botão Sair agora chama realizarLogoff (nuclear).")

# ==========================================
# 3. PROTEGER O API.TS CONTRA CHAMADAS SEM TOKEN
# ==========================================
path_api = os.path.join(os.getcwd(), "frontend", "src", "lib", "api.ts")

with open(path_api, "r", encoding="utf-8") as f:
    a_c = f.read()

# Adiciona uma verificação: se a URL for /auth/me e não houver token, não faz a chamada
if "return Promise.reject" not in a_c:
    # Modifica a função de request (se existir) ou adiciona um interceptor
    a_c = a_c.replace(
        'async function handleResponse<T>',
        '''// Interceptor para evitar chamadas sem token
const originalFetch = window.fetch;
window.fetch = function (input: RequestInfo | URL, init?: RequestInit) {
  const url = typeof input === 'string' ? input : input.toString();
  if (url.includes('/auth/me')) {
    const token = localStorage.getItem("token") || localStorage.getItem("auth_token");
    if (!token) {
      return Promise.reject(new Error("Sem token - ignorando /auth/me"));
    }
  }
  return originalFetch.apply(this, [input, init]);
};

async function handleResponse<T>'''
    )
    with open(path_api, "w", encoding="utf-8") as f:
        f.write(a_c)
    print("✅ api.ts: Chamadas para /auth/me sem token serão ignoradas.")

# ==========================================
# 4. ATUALIZAR O LOGIN PARA LIMPAR O PARÂMETRO DE LOGOFF
# ==========================================
path_login = os.path.join(os.getcwd(), "frontend", "src", "pages", "Login.tsx")

with open(path_login, "r", encoding="utf-8") as f:
    l_c = f.read()

# No login, após sucesso, limpa o parâmetro da URL
if "useNavigate" not in l_c:
    l_c = l_c.replace(
        'import { useState } from "react";',
        'import { useState, useEffect } from "react";\nimport { useNavigate } from "react-router-dom";'
    )

if "const navigate = useNavigate" not in l_c:
    l_c = l_c.replace(
        'export default function Login() {',
        'export default function Login() {\n  const navigate = useNavigate();'
    )

if "logoff=true" not in l_c:
    l_c = l_c.replace(
        'onSuccess: (data: any) => {',
        '''onSuccess: (data: any) => {
      // Remove o parâmetro de logoff da URL
      if (window.location.search.includes("logoff=true")) {
        window.history.replaceState({}, document.title, "/login");
      }'''
    )

with open(path_login, "w", encoding="utf-8") as f:
    f.write(l_c)
print("✅ Login.tsx: Parâmetro de logoff removido após login.")

print("✅ Tudo pronto! Faça o git push.")