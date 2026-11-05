import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Importar o ProtectedRoute
if "ProtectedRoute" not in c:
    c = c.replace(
        'import Perfil from "@/pages/Perfil";',
        'import Perfil from "@/pages/Perfil";\nimport { ProtectedRoute } from "@/components/auth/ProtectedRoute";'
    )

# 2. Envolver as rotas administrativas com o ProtectedRoute
# Vamos agrupar as rotas dentro de um <Route element={<ProtectedRoute modulo="Administração" />}>
rotas_admin = ["/admin/usuarios", "/admin/perfis", "/admin/parametrizacao", "/admin/seguranca", "/admin/base", "/admin/empresa", "/admin/avisos", "/admin/auditoria"]

for rota in rotas_admin:
    # Procura a rota exata e envolve com o ProtectedRoute
    padrao = rf'(<Route path="{rota}" element=\{{<[^>]+>\s*/>\}} />)'
    match = re.search(padrao, c)
    if match:
        rota_original = match.group(1)
        # Como não podemos envolver um único Route, vamos usar o "element" com uma verificação
        # Melhor abordagem: substituir a rota por um componente que checa a permissão
        # Mas para simplificar, vamos apenas adicionar um wrapper manual depois.
        pass

# Como o React Router v6 permite agrupar, vamos criar um bloco de rotas protegidas
# Vamos substituir as rotas admin individuais por um grupo
# (Isso exige reescrever a estrutura, então vamos fazer um replace mais simples: adicionar um componente de proteção em cada página)

print("✅ App.tsx precisa de ajuste manual. Vou te passar o script de reescrita das rotas.")