import os
import zipfile
import shutil
import datetime

def encontrar_ultimo_backup(raiz):
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    if not os.path.exists(pasta_backups):
        print("❌ Pasta de backups não encontrada.")
        return None
    
    # Pega todos os arquivos .zip na pasta
    zips = [f for f in os.listdir(pasta_backups) if f.endswith('.zip')]
    if not zips:
        print("❌ Nenhum backup encontrado.")
        return None
    
    # Ordena por data de modificação (mais recente primeiro)
    zips.sort(key=lambda x: os.path.getmtime(os.path.join(pasta_backups, x)), reverse=True)
    
    # Retorna o mais recente que tenha o Dashboard (para garantir que é um backup completo)
    for zip_nome in zips:
        caminho_zip = os.path.join(pasta_backups, zip_nome)
        try:
            with zipfile.ZipFile(caminho_zip, 'r') as z:
                if 'frontend/src/pages/Dashboard.tsx' in z.namelist():
                    return caminho_zip
        except:
            pass
    
    # Se não achou um com Dashboard, pega o mais recente de qualquer jeito
    return os.path.join(pasta_backups, zips[0])

def restaurar(raiz):
    backup_path = encontrar_ultimo_backup(raiz)
    if not backup_path:
        return

    print(f"🔄 Restaurando do backup: {os.path.basename(backup_path)}")

    # Lista de arquivos que queremos restaurar do backup
    arquivos_para_restaurar = [
        "frontend/src/pages/Dashboard.tsx",
        "app/backend/routers/dashboard.py"
    ]

    with zipfile.ZipFile(backup_path, 'r') as z:
        for arq in arquivos_para_restaurar:
            if arq in z.namelist():
                # Extrai para a raiz do projeto
                z.extract(arq, raiz)
                print(f"✅ Restaurado: {arq}")
            else:
                print(f"⚠️ Arquivo não encontrado no backup: {arq}")

    print("\n✅ Restauração concluída!")

if __name__ == "__main__":
    raiz = os.getcwd()
    restaurar(raiz)
    