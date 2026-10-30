import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MENUS_CORRETO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/App.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_sidebar(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir o ID do menu "Cadastro" (que estava como "frota")
    c = c.replace('id: "frota", label: "Cadastro", icon: Truck,', 'id: "cadastros", label: "Cadastro", icon: Truck,')

    # 2. Remover o Financeiro de dentro de "Gestão"
    c = c.replace('      { label: "Financeiro", icon: DollarSign, path: "/financeiro" },\n', '')

    # 3. Inserir os novos menus principais (Frota e Financeiro) após o Dashboard
    alvo = '{ id: "dashboard", label: "Dashboard", icon: LayoutDashboard, path: "/", isDashboard: true, items: [] },'
    
    novo = alvo + '''
  { id: "frota", label: "Frota", icon: Truck, path: "/frota", items: [] },
  { id: "financeiro", label: "Financeiro", icon: DollarSign, path: "/financeiro", items: [] },'''
    
    if alvo in c:
        c = c.replace(alvo, novo, 1)
        print("✅ Menus Frota e Financeiro adicionados no topo.")
    else:
        print("⚠️ Dashboard não encontrado para inserir os menus.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_app(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar imports
    if 'import Frota from' not in c:
        c = 'import Frota from "@/pages/Frota";\n' + c
    if 'import Financeiro from' not in c:
        c = 'import Financeiro from "@/pages/Financeiro";\n' + c

    # 2. Adicionar rotas
    alvo = '<Route path="/" element={<Dashboard />} />'
    if alvo in c:
        novo = alvo + '\n              <Route path="/frota" element={<Frota />} />\n              <Route path="/financeiro" element={<Financeiro />} />'
        c = c.replace(alvo, novo, 1)
        print("✅ Rotas /frota e /financeiro adicionadas.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_sidebar(raiz)
    fix_app(raiz)
    print("\n✅ Script aplicado com sucesso!")