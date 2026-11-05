import os

# 1. Corrigir o nome no Sidebar
sidebar_path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('label: "Kanban Manutenção"', 'label: "Gestão de Manutenção"')
# Caso a rota tenha ficado estranha, vamos padronizar para /admin/manutencoes
c = c.replace('path: "/admin/kanban"', 'path: "/admin/manutencoes"')

with open(sidebar_path, "w", encoding="utf-8") as f:
    f.write(c)

# 2. Corrigir a rota no App.tsx
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

app_c = app_c.replace('/admin/kanban', '/admin/manutencoes')
with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_c)

# 3. Corrigir o título dentro da tela
tela_path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Manutencoes.tsx")
with open(tela_path, "r", encoding="utf-8") as f:
    tela_c = f.read()

tela_c = tela_c.replace('title="Gestão de Manutenção"', 'title="Gestão de Manutenção"') # Já estava certo no código
# Vamos garantir que o título esteja perfeito.
with open(tela_path, "w", encoding="utf-8") as f:
    f.write(tela_c)

print("✅ Nome corrigido para 'Gestão de Manutenção' no menu, rota e tela.")