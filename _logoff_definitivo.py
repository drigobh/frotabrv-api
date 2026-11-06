import os
import re

# ==========================================
# 1. CRIAR UTILITÁRIO DE LOGOFF
# ==========================================
path_utils = os.path.join(os.getcwd(), "frontend", "src", "lib", "auth.ts")

conteudo_utils = r'''import { queryClient } from "@/main"; // Importa o queryClient global

export function realizarLogoff() {
  // 1. Limpa o cache do React Query
  if (queryClient) {
    queryClient.clear();
  }
  
  // 2. Limpa o armazenamento local
  localStorage.clear();
  sessionStorage.clear();

  // 3. Força o redirecionamento para o login, recarregando a página inteira
  // Usamos window.location.replace para impedir que o usuário volte com o botão "Voltar"
  window.location.replace("/login");
}
'''

os.makedirs(os.path.dirname(path_utils), exist_ok=True)
with open(path_utils, "w", encoding="utf-8") as f:
    f.write(conteudo_utils)
print("✅ Utilitário de logoff criado.")

# ==========================================
# 2. ATUALIZAR O SIDEBAR PARA USAR O UTILITÁRIO
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    c = f.read()

# Remove a função handleLogoff antiga (se existir)
c = re.sub(r'const handleLogoff = \(\) => \{[\s\S]*?\};', '', c)

# Adiciona o import do utilitário
if "realizarLogoff" not in c:
    c = c.replace(
        'import { useMe } from "@/hooks/useSession";',
        'import { useMe } from "@/hooks/useSession";\nimport { realizarLogoff } from "@/lib/auth";'
    )

# Substitui o onClick do botão Sair por realizarLogoff
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
print("✅ Sidebar: Botão Sair agora chama realizarLogoff.")

# ==========================================
# 3. EXPORTAR O QUERY CLIENT NO MAIN.TSX
# ==========================================
path_main = os.path.join(os.getcwd(), "frontend", "src", "main.tsx")

with open(path_main, "r", encoding="utf-8") as f:
    m_c = f.read()

if "export const queryClient" not in m_c:
    # Se o queryClient já existe, exporta ele
    if "const queryClient" in m_c:
        m_c = m_c.replace("const queryClient", "export const queryClient")
    else:
        # Se não existe, cria um
        m_c = "import { QueryClient } from '@tanstack/react-query';\nexport const queryClient = new QueryClient();\n" + m_c
    
    with open(path_main, "w", encoding="utf-8") as f:
        f.write(m_c)
    print("✅ main.tsx: queryClient exportado.")

print("✅ Tudo pronto! Faça o git push.")