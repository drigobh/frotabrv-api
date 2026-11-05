import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Encontrar o bloco de rotas do AppLayout
# Precisamos garantir que as rotas protegidas estejam DENTRO do <Route element={<AppLayout />}>
# e não como irmãs.

# Verifica se o bloco protegido está dentro do AppLayout
if '<Route element={<ProtectedRoute modulo="Administração" />}>' in c:
    # Encontra o índice do AppLayout e do fechamento do Route
    idx_layout_start = c.find('<Route element={<AppLayout />}')
    idx_layout_end = c.find('</Route>', idx_layout_start)
    
    # Encontra o bloco protegido
    idx_protegido = c.find('<Route element={<ProtectedRoute modulo="Administração" />}>')
    
    # Se o bloco protegido estiver FORA do AppLayout (índice menor que o layout ou maior que o fechamento)
    if idx_protegido < idx_layout_start or idx_protegido > idx_layout_end:
        print("⚠️ Rotas protegidas estão FORA do AppLayout. Movendo para dentro...")
        
        # Extrai o bloco protegido
        match_protegido = re.search(r'(<Route element=\{<ProtectedRoute modulo="Administração" />\}>[\s\S]*?</Route>)', c)
        if match_protegido:
            bloco = match_protegido.group(1)
            # Remove o bloco de onde está
            c = c.replace(bloco, '')
            
            # Insere dentro do AppLayout (antes do fechamento do último Route filho)
            # Encontra o fechamento do AppLayout
            idx_layout_end = c.find('</Route>', c.find('<Route element={<AppLayout />}'))
            if idx_layout_end != -1:
                c = c[:idx_layout_end] + '        ' + bloco + '\n      ' + c[idx_layout_end:]
                print("✅ Bloco de rotas protegidas movido para dentro do AppLayout.")

# 2. Garantir que o AppLayout envolve todas as rotas filhas
# Se o AppLayout não tem filhos (está vazio), precisamos adicionar as rotas
if '<Route element={<AppLayout />}>' not in c and '<Route element={<AppLayout />} />' in c:
    print("⚠️ AppLayout está sem filhos. Vou adicionar as rotas.")
    # Substituir o AppLayout auto-fechado por um com filhos
    c = c.replace(
        '<Route element={<AppLayout />} />',
        '<Route element={<AppLayout />}>' + re.findall(r'<Route[^>]*element=\{[^}]+\}[^>]*/>', c)[0] + '</Route>'
    )

# 3. Verificar se os imports do ProtectedRoute estão corretos
if "import { ProtectedRoute }" not in c:
    c = c.replace(
        'import Perfil from "@/pages/Perfil";',
        'import Perfil from "@/pages/Perfil";\nimport { ProtectedRoute } from "@/components/auth/ProtectedRoute";'
    )

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ App.tsx corrigido! As rotas protegidas agora ficam dentro do AppLayout.")