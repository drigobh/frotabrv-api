import os
import re

# ==========================================
# 1. CORRIGIR IMPORTS DO SIDEBAR
# ==========================================
sidebar_path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    side_c = f.read()

# Garante todos os ícones necessários
icones_necessarios = ["BellRing", "FileBarChart", "CalendarClock", "LayoutDashboard", "Fuel", "Wrench", "Truck", "Users", "Car", "Settings", "Package", "Disc", "Activity", "BarChart3", "FileText", "DollarSign", "LogOut", "ChevronDown", "ChevronRight", "PanelLeftClose", "PanelLeftOpen", "Briefcase", "Shield", "Bell", "UserCog", "FileBox", "Tag", "Building", "FolderOpen", "Layers"]

# Pega o bloco de importação do lucide-react
match = re.search(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', side_c)
if match:
    importados = [i.strip() for i in match.group(1).replace("\n", " ").split(",") if i.strip()]
    faltando = [ic for ic in icones_necessarios if ic not in importados]
    if faltando:
        novos_imports = match.group(1).rstrip() + ", " + ", ".join(faltando)
        side_c = side_c.replace(match.group(0), f'import {{ {novos_imports} }} from "lucide-react";')
        print(f"✅ Ícones adicionados: {', '.join(faltando)}")
    else:
        print("✅ Todos os ícones já estavam importados.")

with open(sidebar_path, "w", encoding="utf-8") as f:
    f.write(side_c)

# ==========================================
# 2. GARANTIR ROTAS NO APP.TSX
# ==========================================
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

# Verificar imports das páginas
paginas_necessarias = {
    "Dashboard": "@/pages/Dashboard",
    "Manutencoes": "@/pages/Manutencoes",
    "CentralAlertas": "@/pages/CentralAlertas"
}

for nome, path_imp in paginas_necessarias.items():
    if f'import {nome} from "{path_imp}";' not in app_c:
        # Tenta achar a última importação de página para adicionar logo depois
        match_imp = re.search(r'import\s+\w+\s+from\s+"@/pages/[^"]+";', app_c)
        if match_imp:
            app_c = app_c.replace(match_imp.group(0), match_imp.group(0) + f'\nimport {nome} from "{path_imp}";')
            print(f"✅ Import de {nome} adicionado.")

# Garantir rotas
rotas_necessarias = {
    "/alertas": "CentralAlertas",
    "/admin/manutencoes": "Manutencoes"
}
for rota, componente in rotas_necessarias.items():
    if f'path="{rota}"' not in app_c:
        # Coloca antes do último Route para não quebrar a estrutura
        match_route = re.search(r'(<Route\s+path="[^"]+"\s+element=\{<\w+\s*\/>\}\s*\/>)', app_c)
        if match_route:
            nova_rota = f'\n          <Route path="{rota}" element={{<{componente} />}} />'
            app_c = app_c.replace(match_route.group(0), match_route.group(0) + nova_rota)
            print(f"✅ Rota {rota} injetada.")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_c)

print("\n✅ Consolidação concluída! Rode: git add . && git commit -m 'chore: consolida melhorias 2.0' && git push")