import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ADMIN_LIST_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "app", "backend", "routers", "admin.py")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "app/backend/routers/admin.py")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "admin.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # A lista atual
    lista_antiga = 'colecoes_permitidas = ["veiculos", "carretas", "motoristas", "acoplamentos", "abastecimentos"]'
    
    # A lista com fornecedores
    lista_nova = 'colecoes_permitidas = ["veiculos", "carretas", "motoristas", "acoplamentos", "abastecimentos", "fornecedores"]'

    if lista_antiga in c:
        c = c.replace(lista_antiga, lista_nova)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: 'fornecedores' adicionado à lista de coleções permitidas.")
    else:
        print("⚠️ A lista exata não foi encontrada. O código pode já ter sido alterado ou formatado diferente.")
        # Fallback flexível
        if '"abastecimentos"' in c and '"fornecedores"' not in c:
            c = c.replace('"abastecimentos"]', '"abastecimentos", "fornecedores"]')
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Backend: 'fornecedores' adicionado via fallback.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)