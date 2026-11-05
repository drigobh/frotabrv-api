import os
import zipfile
import datetime

def criar_backup():
    raiz = os.getcwd()
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    
    nome_zip = f"BACKUP_PRE_IMPORTACAO_2_0_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_zip)
    
    # Pastas e arquivos a ignorar
    ignorar = {
        'node_modules', '.git', 'dist', 'build', '__pycache__', 
        '.venv', 'venv', '.next', 'coverage', '.pytest_cache', '_automacao'
    }
    
    print(f"📦 Iniciando backup do projeto...")
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(raiz):
            dirs[:] = [d for d in dirs if d not in ignorar and not d.startswith('.')]
            for file in files:
                if file.endswith(('.pyc', '.pyo', '.log')):
                    continue
                caminho_abs = os.path.join(root, file)
                caminho_rel = os.path.relpath(caminho_abs, raiz)
                zipf.write(caminho_abs, caminho_rel)
                
    tamanho = os.path.getsize(caminho_zip) / (1024 * 1024)
    print(f"✅ Backup concluído! Tamanho: {tamanho:.2f} MB")
    print(f"📁 Arquivo salvo em: _automacao/backups/{nome_zip}")

if __name__ == "__main__":
    criar_backup()