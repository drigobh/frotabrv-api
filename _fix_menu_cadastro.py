import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MENU_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/components/layout/Sidebar.tsx"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    
    if not os.path.exists(caminho):
        print("⚠️ Arquivo Sidebar.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Procura por "Frota" no título do menu ou label e troca por "Cadastro"
    # Vamos usar um Regex para encontrar onde está escrito "Frota" no menu
    if '"Frota"' in c:
        c = c.replace('"Frota"', '"Cadastro"')
        print("✅ Menu alterado de 'Frota' para 'Cadastro'.")
    elif "'Frota'" in c:
        c = c.replace("'Frota'", "'Cadastro'")
        print("✅ Menu alterado de 'Frota' para 'Cadastro'.")
    elif 'Frota' in c:
        # Fallback genérico caso esteja sem aspas no JSX
        c = re.sub(r'\bFrota\b', 'Cadastro', c)
        print("✅ Menu alterado de 'Frota' para 'Cadastro' (via fallback).")
    else:
        print("ℹ️ Não encontrei a palavra 'Frota' no menu.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)