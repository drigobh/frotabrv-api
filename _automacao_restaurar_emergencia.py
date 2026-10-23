import os
import zipfile

def restaurar(raiz):
    print("🚨 RESTAURAÇÃO DE EMERGÊNCIA (SOBRESCREVENDO) 🚨")
    caminho_backup = os.path.join(raiz, "_automacao", "backups", "BACKUP_FULL_ANTES_HODOMETRO_20261023_103903.zip")
    
    if not os.path.exists(caminho_backup):
        print("❌ Backup não encontrado!")
        return

    print("📂 Extraindo backup por cima dos arquivos atuais...")
    with zipfile.ZipFile(caminho_backup, 'r') as zipf:
        zipf.extractall(raiz)
    
    print("✅ Restauração concluída! O código voltou ao estado funcional de antes das alterações no hodômetro.")

if __name__ == "__main__":
    restaurar(os.getcwd())