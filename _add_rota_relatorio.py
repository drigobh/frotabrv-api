import os

# 1. Adiciona a rota no App.tsx
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    c = f.read()

if "RelatoriosPneus" not in c:
    c = c.replace(
        'import Pneus from "@/pages/Pneus";',
        'import Pneus from "@/pages/Pneus";\nimport RelatoriosPneus from "@/pages/RelatoriosPneus";'
    )
    c = c.replace(
        '<Route path="/operacao/pneus" element={<Pneus />} />',
        '<Route path="/operacao/pneus" element={<Pneus />} />\n          <Route path="/operacao/relatorios-pneus" element={<RelatoriosPneus />} />'
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Rota adicionada no App.tsx.")

# 2. Adiciona no Menu Lateral (Sidebar)
# Vamos procurar o arquivo do menu (geralmente Sidebar.tsx ou AppSidebar.tsx)
menu_path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
if not os.path.exists(menu_path):
    menu_path = os.path.join(os.getcwd(), "frontend", "src", "components", "AppSidebar.tsx")

if os.path.exists(menu_path):
    with open(menu_path, "r", encoding="utf-8") as f:
        m = f.read()
    
    if "relatorios-pneus" not in m:
        # Encontra o link de pneus e adiciona embaixo
        import re
        match = re.search(r'(<Link to="/operacao/pneus".*?</Link>)', m, re.DOTALL)
        if match:
            link_original = match.group(1)
            # Cria uma cópia do link para o relatório
            link_relatorio = link_original.replace("/operacao/pneus", "/operacao/relatorios-pneus").replace("Pneus", "Relatórios Pneus").replace("Disc", "BarChart3")
            m = m.replace(link_original, link_original + "\n" + link_relatorio)
            with open(menu_path, "w", encoding="utf-8") as f:
                f.write(m)
            print("✅ Link adicionado no Menu Lateral.")
        else:
            print("⚠️ Não encontrei o link de Pneus no Menu.")