import os

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Verifica se a rota já existe no menu
if "/admin/manutencoes" in c:
    print("ℹ️ O link já existe no menu.")
else:
    # 1. Encontra o bloco do menu Administração para injetar o link
    # Vamos usar o link "Base (Limpeza)" como âncora
    ancora = '{ label: "Base (Limpeza)", icon: FileText, path: "/admin/base" },'
    
    novo_link = ancora + '\n      { label: "Kanban Manutenção", icon: Wrench, path: "/admin/manutencoes" },'
    
    if ancora in c:
        c = c.replace(ancora, novo_link)
        print("✅ Link 'Kanban Manutenção' injetado no menu Administração.")
    else:
        print("⚠️ Âncora 'Base (Limpeza)' não encontrada. Verifique se o nome está certo.")

# 2. Adiciona a rota no App.tsx
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "Manutencoes" not in app_c:
    # Import
    if 'import Manutencoes from "@/pages/Manutencoes";' not in app_c:
        app_c = app_c.replace(
            'import Pneus from "@/pages/Pneus";',
            'import Pneus from "@/pages/Pneus";\nimport Manutencoes from "@/pages/Manutencoes";'
        )
    
    # Rota (A rota existente de /manutencoes pode conflitar, então removemos ela e adicionamos a /admin)
    # Se já existir uma rota /manutencoes, o React Router pode reclamar.
    app_c = app_c.replace('<Route path="/manutencoes" element={<Manutencoes />} />', '')
    
    # Injeta a nova rota dentro de admin (vamos colocar junto com as outras de admin)
    app_c = app_c.replace(
        '<Route path="/admin/usuarios"',
        '<Route path="/admin/manutencoes" element={<Manutencoes />} />\n          <Route path="/admin/usuarios"'
    )
    # Se a rota de admin/usuarios não existir, adiciona em qualquer lugar (fallback)
    if '<Route path="/admin/manutencoes" element={<Manutencoes />} />' not in app_c:
         app_c = app_c.replace(
            '<Route path="/operacao/pneus"',
            '<Route path="/admin/manutencoes" element={<Manutencoes />} />\n          <Route path="/operacao/pneus"'
        )
    
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_c)
    print("✅ Rota '/admin/manutencoes' configurada no App.tsx.")