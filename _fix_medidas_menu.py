import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MEDIDAS_MENU_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/App.tsx",
        "frontend/src/components/layout/Sidebar.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_app(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar import
    if 'import PneuMedidas' not in c:
        c = 'import PneuMedidas from "@/pages/PneuMedidas";\n' + c
        print("✅ Import de PneuMedidas adicionado.")

    # 2. Adicionar rota (após a rota de Pneus)
    if 'path="/cadastros/pneu-medidas"' not in c:
        alvo = '<Route path="/pneus" element={<Pneus />} />'
        if alvo in c:
            c = c.replace(alvo, alvo + '\n              <Route path="/cadastros/pneu-medidas" element={<PneuMedidas />} />')
            print("✅ Rota /cadastros/pneu-medidas adicionada.")
        else:
            # Fallback: adicionar após o Dashboard
            alvo2 = '<Route path="/" element={<Dashboard />} />'
            if alvo2 in c:
                c = c.replace(alvo2, alvo2 + '\n              <Route path="/cadastros/pneu-medidas" element={<PneuMedidas />} />')
                print("✅ Rota adicionada via fallback.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_sidebar(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar o item no array MENUS, dentro de "cadastros"
    if 'Medidas de Pneus' not in c:
        # Procura o item "Cadastro de Planos" dentro de cadastros para inserir depois
        alvo = '{ label: "Cadastro de Planos", icon: Wrench, path: "/cadastros/planos-manutencao" },'
        novo = alvo + '\n      { label: "Medidas de Pneus", icon: Disc, path: "/cadastros/pneu-medidas" },'
        
        if alvo in c:
            c = c.replace(alvo, novo, 1)
            print("✅ Item 'Medidas de Pneus' adicionado ao menu Cadastro.")
        else:
            print("⚠️ Âncora 'Cadastro de Planos' não encontrada.")

    # 2. Garantir import do ícone Disc
    import_match = re.search(r'import\s*\{([^}]+)\}\s*from\s*["\']lucide-react["\']', c)
    if import_match:
        atuais = import_match.group(1)
        if 'Disc' not in atuais:
            novos = atuais + ", Disc"
            c = c[:import_match.start(1)] + novos + c[import_match.end(1):]
            print("✅ Import do ícone Disc adicionado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_app(raiz)
    fix_sidebar(raiz)
    print("\n✅ Script aplicado com sucesso!")