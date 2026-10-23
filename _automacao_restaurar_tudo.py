import os
import shutil
import zipfile

def restaurar(raiz):
    print("🚨 INICIANDO RESTAURAÇÃO DE EMERGÊNCIA 🚨")
    caminho_backup = os.path.join(raiz, "_automacao", "backups", "BACKUP_FULL_ANTES_HODOMETRO_20261023_103903.zip")
    
    if not os.path.exists(caminho_backup):
        print("❌ Backup não encontrado! Verifique a pasta _automacao/backups.")
        return

    print("🗑️ Apagando pastas corrompidas...")
    shutil.rmtree(os.path.join(raiz, "app"), ignore_errors=True)
    shutil.rmtree(os.path.join(raiz, "frontend"), ignore_errors=True)

    print("📂 Extraindo backup...")
    with zipfile.ZipFile(caminho_backup, 'r') as zipf:
        zipf.extractall(raiz)
    
    print("✅ Restauração concluída! O sistema voltou ao estado funcional.")

if __name__ == "__main__":
    restaurar(os.getcwd())