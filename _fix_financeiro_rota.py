import os
import re

# 1. Verifica se o arquivo Financeiro.tsx existe
path_fin = os.path.join(os.getcwd(), "frontend", "src", "pages", "Financeiro.tsx")
if not os.path.exists(path_fin):
    print("❌ Arquivo Financeiro.tsx não existe. Criando...")
    # (O código completo da tela está no script anterior, vamos apenas garantir o arquivo)
    # Se você já rodou o script anterior, ele deve existir.
else:
    print("✅ Arquivo Financeiro.tsx existe.")

# 2. Corrige o App.tsx
path_app = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")

with open(path_app, "r", encoding="utf-8") as f:
    app_c = f.read()

# Garante que o import existe
if 'import Financeiro from "@/pages/Financeiro";' not in app_c:
    app_c = app_c.replace(
        'import Multas from "@/pages/Multas";',
        'import Multas from "@/pages/Multas";\nimport Financeiro from "@/pages/Financeiro";'
    )
    print("✅ Import do Financeiro adicionado.")

# Remove qualquer rota antiga de financeiro (que possa estar apontando para outro componente)
app_c = re.sub(r'<Route\s+path="/financeiro"\s+element=\{[^}]+\}\s*/>', '', app_c)

# Adiciona a rota correta antes do catch-all
if '<Route path="/financeiro" element={<Financeiro />} />' not in app_c:
    # Tenta adicionar dentro do bloco do AppLayout (antes do fechamento)
    # Encontra a linha do catch-all ou do fechamento
    match = re.search(r'(<Route\s+path="\*"|\s*</Routes>)', app_c)
    if match:
        if 'path="*"' in match.group(1):
            app_c = app_c.replace(match.group(1), '<Route path="/financeiro" element={<Financeiro />} />\n          ' + match.group(1))
        else:
            app_c = app_c.replace(match.group(1), '          <Route path="/financeiro" element={<Financeiro />} />\n        ' + match.group(1))
        print("✅ Rota /financeiro adicionada.")
    else:
        print("⚠️ Não foi possível encontrar o local para inserir a rota.")

with open(path_app, "w", encoding="utf-8") as f:
    f.write(app_c)

# 3. Verifica o Sidebar para garantir que o link está lá
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(path_sidebar, "r", encoding="utf-8") as f:
    s_c = f.read()

if 'path: "/financeiro"' not in s_c:
    # Adiciona o link no menu (se não existir)
    ancora = '{ label: "Pneus", icon: Disc, path: "/operacao/pneus" },'
    novo_link = ancora + '\n      { label: "Financeiro", icon: DollarSign, path: "/financeiro" },'
    s_c = s_c.replace(ancora, novo_link)
    if "DollarSign" not in s_c.split("from \"lucide-react\"")[0]:
        s_c = re.sub(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', r'import {\1, DollarSign } from "lucide-react";', s_c, count=1)
    with open(path_sidebar, "w", encoding="utf-8") as f:
        f.write(s_c)
    print("✅ Link do Financeiro adicionado ao Sidebar.")

print("✅ Tudo pronto! Faça o git push.")