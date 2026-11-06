import os
import re

# 1. Verificar o arquivo App.tsx
path_app = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")

with open(path_app, "r", encoding="utf-8") as f:
    app_c = f.read()

# Procura a rota /financeiro
match_rota = re.search(r'<Route\s+path="/financeiro"\s+element=\{<(\w+)\s*\/>\}', app_c)
if match_rota:
    componente_atual = match_rota.group(1)
    print(f"⚠️ A rota /financeiro está apontando para o componente: {componente_atual}")
    
    if componente_atual != "Financeiro":
        # Substitui pela nossa tela nova
        app_c = app_c.replace(
            f'<Route path="/financeiro" element={{<{componente_atual} />}} />',
            '<Route path="/financeiro" element={<Financeiro />} />'
        )
        print("✅ Rota corrigida para o novo componente Financeiro.")
    else:
        print("✅ A rota já aponta para o componente Financeiro.")
else:
    # Se não achou a rota, verifica se o import existe e adiciona
    if 'import Financeiro from "@/pages/Financeiro";' not in app_c:
        app_c = app_c.replace(
            'import Multas from "@/pages/Multas";',
            'import Multas from "@/pages/Multas";\nimport Financeiro from "@/pages/Financeiro";'
        )
        # Adiciona a rota no bloco de rotas (antes do catch-all)
        if '<Route path="*"' in app_c:
            app_c = app_c.replace('<Route path="*"', '<Route path="/financeiro" element={<Financeiro />} />\n          <Route path="*"')
        print("✅ Import e rota do Financeiro adicionados.")

with open(path_app, "w", encoding="utf-8") as f:
    f.write(app_c)

# 2. Verificar se o arquivo Financeiro.tsx existe
path_fin = os.path.join(os.getcwd(), "frontend", "src", "pages", "Financeiro.tsx")
if os.path.exists(path_fin):
    print("✅ Arquivo Financeiro.tsx existe.")
else:
    print("❌ Arquivo Financeiro.tsx NÃO existe! O script anterior pode ter falhado.")