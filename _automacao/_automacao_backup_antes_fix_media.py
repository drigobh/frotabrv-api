import os
import datetime
import zipfile

def criar_backup_full(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"BACKUP_FULL_ANTES_FIX_MEDIA_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Iniciando Backup Full...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ['app', 'backend', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta)
            if not os.path.exists(caminho_pasta): continue
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try: zipf.write(caminho_completo, caminho_relativo)
                    except: pass
    print(f"✅ Backup salvo: {nome_backup}")

if __name__ == "__main__":
    criar_backup_full(os.getcwd())