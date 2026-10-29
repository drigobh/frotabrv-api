import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BACK_DEF_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "app/backend/models/fornecedores.py")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    for i in range(len(linhas)):
        # Corrige qualquer linha que tenha tipo_fornecedor_id e esteja duplicada
        if 'tipo_fornecedor_id' in linhas[i]:
            linhas[i] = '    tipo_fornecedor_id: str | None = None\n'

    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print("✅ Backend: linha corrigida para 'tipo_fornecedor_id: str | None = None'")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)