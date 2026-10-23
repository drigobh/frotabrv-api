import os
import datetime
import zipfile

def criar_backup_full(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"BACKUP_FULL_ANTES_HODOMETRO_{agora}.zip"
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Iniciando Backup Full...")
    print(f"💾 Destino: {caminho_zip}")
    
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build', '.pytest_cache', '.emergent']
    pastas_alvo = ['app', 'backend', 'frontend']
    arquivos_salvos = 0
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in pastas_alvo:
            caminho_pasta = os.path.join(raiz, pasta)
            if not os.path.exists(caminho_pasta):
                continue
                
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    if file.endswith('.zip') or file.endswith('.tmp'):
                        continue
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                        arquivos_salvos += 1
                    except Exception as e:
                        print(f"⚠️ Erro ao salvar {caminho_relativo}: {e}")

    tamanho_mb = os.path.getsize(caminho_zip) / (1024 * 1024)
    print(f"\n✅ Backup concluído com sucesso!")
    print(f"📊 Total de arquivos salvos: {arquivos_salvos}")
    print(f"📦 Tamanho do arquivo: {tamanho_mb:.2f} MB")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_full(raiz)