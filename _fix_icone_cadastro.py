import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ICONE_CADASTRO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/components/layout/Sidebar.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Trocar o ícone do Cadastro (de Truck para FolderOpen)
    c = c.replace('id: "cadastros", label: "Cadastro", icon: Truck,', 'id: "cadastros", label: "Cadastro", icon: FolderOpen,')

    # 2. Garantir import do FolderOpen APENAS na linha do lucide-react
    # Pega a linha do import do lucide-react
    linhas = c.split('\n')
    for i, linha in enumerate(linhas):
        if 'from "lucide-react"' in linha:
            # Se o FolderOpen não estiver na linha, adiciona
            if 'FolderOpen' not in linha:
                linhas[i] = linha.replace('}', ', FolderOpen }')
                print("✅ FolderOpen adicionado ao import do lucide-react.")
            break
    
    c = '\n'.join(linhas)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Sidebar.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")