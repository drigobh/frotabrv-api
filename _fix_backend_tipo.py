import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BACKEND_TIPO_OBRIG_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "app/backend/models/fornecedores.py")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    if not os.path.exists(caminho):
        print("❌ Arquivo models/fornecedores.py não encontrado.")
        return
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Troca Optional[str] por str no tipo_fornecedor_id
    if 'tipo_fornecedor_id: str | None = None' in c:
        c = c.replace(
            'tipo_fornecedor_id: str | None = None',
            'tipo_fornecedor_id: str  # Obrigatório'
        )
        print("✅ Backend: campo tipo_fornecedor_id agora é obrigatório.")
    elif 'tipo_fornecedor_id: Optional[str] = None' in c:
        c = c.replace(
            'tipo_fornecedor_id: Optional[str] = None',
            'tipo_fornecedor_id: str'
        )
        print("✅ Backend: campo tipo_fornecedor_id agora é obrigatório.")
    else:
        print("⚠️ Campo tipo_fornecedor_id não encontrado no Model. Verifique manualmente.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    print("✅ Script Backend finalizado.")