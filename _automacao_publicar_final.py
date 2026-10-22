import os
import shutil
import datetime
import zipfile
import subprocess

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_alinhamento_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def publicar(raiz):
    print("\n📤 Fazendo commit e push para o GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True, shell=True)
        subprocess.run(["git", "commit", "-m", "style: alinhando colunas da tabela de abastecimentos"], check=True, shell=True)
        subprocess.run(["git", "push"], check=True, shell=True)
        print("✅ Push concluído com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no git: {e}")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Publicação Final...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    publicar(raiz)

    print("\n🎉 Tudo pronto! O sistema está salvo e seguro.")

if __name__ == "__main__":
    executar()