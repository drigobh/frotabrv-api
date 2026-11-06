import os
import re

# 1. Ler o Sidebar para pegar todos os paths
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(path_sidebar, "r", encoding="utf-8") as f:
    sidebar_c = f.read()

# Extrair todos os paths do Sidebar
paths_sidebar = set(re.findall(r'path:\s*["\']([^"\']+)["\']', sidebar_c))

# 2. Ler o App.tsx para pegar todas as rotas registradas
path_app = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(path_app, "r", encoding="utf-8") as f:
    app_c = f.read()

# Extrair todos os paths do App
paths_app = set(re.findall(r'path="([^"]+)"', app_c))

# 3. Comparar
print("📋 ROTAS NO SIDEBAR (que o menu mostra):")
for p in sorted(paths_sidebar):
    if p == "/": continue
    status = "✅" if p in paths_app else "❌ (não existe no App.tsx)"
    print(f"  {status} {p}")

print("\n📋 ROTAS NO APP.TSX (que estão registradas):")
for p in sorted(paths_app):
    if p == "*": continue
    status = "✅" if p in paths_sidebar else "⚠️ (existe no App, mas não está no Sidebar)"
    print(f"  {status} {p}")

print("\n🔍 FALTANDO NO APP.TSX (menu mostra, mas a página não abre):")
faltando = paths_sidebar - paths_app - {"/"}
if faltando:
    for p in sorted(faltando):
        print(f"  ❌ {p}")
else:
    print("  ✅ Todas as rotas do Sidebar estão registradas no App.")