import os
import re

path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remover o link de Multas do grupo "Gestão"
c = re.sub(r'\s*\{ label: "Multas e Infrações".*?\},', '', c)

# 2. Adicionar o link no grupo "Frota", logo após Pneus
ancora_frota = '{ label: "Pneus", icon: Disc, path: "/operacao/pneus" },'
novo_link = ancora_frota + '\n      { label: "Multas e Infrações", icon: AlertTriangle, path: "/multas" },'

if ancora_frota in c:
    c = c.replace(ancora_frota, novo_link)
    print("✅ Link de Multas movido para o grupo 'Frota'.")
else:
    print("⚠️ Âncora 'Pneus' não encontrada no menu Frota.")

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx atualizado!")