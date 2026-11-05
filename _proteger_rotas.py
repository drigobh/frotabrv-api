import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Importar o ProtectedRoute
if "ProtectedRoute" not in c:
    # Procura a última importação de página para adicionar depois
    match_imp = re.search(r'(import\s+\w+\s+from\s+"@/pages/[^"]+";\n)', c)
    if match_imp:
        c = c.replace(match_imp.group(1), match_imp.group(1) + 'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";\n')
    else:
        c = 'import { ProtectedRoute } from "@/components/auth/ProtectedRoute";\n' + c

# 2. Envolver as rotas de administração com o ProtectedRoute
# Vamos usar um regex para encontrar o bloco de rotas e adicionar o wrapper
# Como as rotas podem estar em um array ou em JSX, vamos usar uma abordagem mais simples:
# Substituir as rotas de admin por um grupo protegido

# Lista de rotas de admin
rotas_admin = [
    ("/admin/usuarios", "<Usuarios />"),
    ("/admin/perfis", "<Perfis />"),
    ("/admin/parametrizacao", "<Parametrizacao />"),
]

# Verifica se as rotas existem soltas e as agrupa
for rota, elemento in rotas_admin:
    padrao = rf'<Route\s+path="{rota}"\s+element=\{{{elemento}\}}\s*/>'
    if re.search(padrao, c):
        # Remove a rota solta
        c = re.sub(padrao, '', c)
        print(f"✅ Rota {rota} removida do nível principal.")

# Adiciona o grupo protegido de rotas de admin antes do fechamento do AppLayout ou do Routes
# Procura o fechamento de </Routes> ou </AppLayout> para inserir
bloco_protegido = '''
        {/* Rotas de Administração Protegidas */}
        <Route element={<ProtectedRoute modulo="Administração" />}>
          <Route path="/admin/usuarios" element={<Usuarios />} />
          <Route path="/admin/perfis" element={<Perfis />} />
          <Route path="/admin/parametrizacao" element={<Parametrizacao />} />
        </Route>
'''

if "ProtectedRoute modulo=\"Administração\"" not in c:
    # Tenta inserir antes do fechamento do último Route (que seria o catch-all)
    match_fim = re.search(r'(<Route\s+path="\*"[^>]*/>)', c)
    if match_fim:
        c = c.replace(match_fim.group(1), bloco_protegido + "\n        " + match_fim.group(1))
        print("✅ Bloco de rotas protegidas inserido antes do catch-all.")
    else:
        # Tenta inserir antes do </Routes>
        c = c.replace("</Routes>", bloco_protegido + "\n      </Routes>")
        print("✅ Bloco de rotas protegidas inserido antes do </Routes>.")

# 3. Garantir que os imports das páginas de admin existem
for page in ["Usuarios", "Perfis", "Parametrizacao"]:
    if f'import {page} from "@/pages/{page}";' not in c:
        # Tenta achar o último import de página
        match_imp = re.search(r'(import\s+\w+\s+from\s+"@/pages/[^"]+";\n)', c)
        if match_imp:
            c = c.replace(match_imp.group(1), match_imp.group(1) + f'import {page} from "@/pages/{page}";\n')
            print(f"✅ Import da página {page} adicionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("\n✅ App.tsx atualizado com as rotas protegidas!")