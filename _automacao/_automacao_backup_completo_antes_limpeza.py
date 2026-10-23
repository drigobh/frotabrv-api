import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz):
    # Define o nome do arquivo com data e hora
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"BACKUP_FULL_ANTES_LIMPEZA_{agora}.zip"
    
    # Cria a pasta de backups se não existir
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Iniciando a criação do Backup Full do Sistema...")
    print(f"📂 Origem: {raiz}")
    print(f"💾 Destino: {caminho_zip}")
    
    # Pastas e arquivos que serão ignorados para não deixar o backup gigante
    ignorar = [
        'node_modules', '.git', '__pycache__', '.venv', 'venv', 
        'dist', 'build', '.pytest_cache', '.emergent'
    ]
    
    # Pastas principais que queremos salvar
    pastas_alvo = ['app', 'backend', 'frontend']
    
    arquivos_salvos = 0
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in pastas_alvo:
            caminho_pasta = os.path.join(raiz, pasta)
            if not os.path.exists(caminho_pasta):
                print(f"⚠️ Pasta {pasta} não encontrada, pulando...")
                continue
                
            for root, dirs, files in os.walk(caminho_pasta):
                # Filtra as pastas ignoradas
                dirs[:] = [d for d in dirs if d not in ignorar]
                
                for file in files:
                    # Ignora arquivos de backup antigos ou temporários
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
    print(f"📁 Localização: {caminho_zip}")
    print("\n💡 Guarde este arquivo. Se algo der errado, basta extraí-lo de volta para a pasta do projeto.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_full(raiz)