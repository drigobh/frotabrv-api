import os
import zipfile
import datetime
import subprocess

def criar_backup_e_publicar():
    raiz = os.getcwd()
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    
    nome_zip = f"MARCO_NOVA_ETAPA_CHATGPT_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_zip)
    
    ignorar = {
        'node_modules', '.git', 'dist', 'build', '__pycache__', 
        '.venv', 'venv', '.next', 'coverage', '.pytest_cache', '_automacao'
    }
    
    print(f"📦 Iniciando backup do projeto (Marco Nova Etapa ChatGPT)...")
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(raiz):
            dirs[:] = [d for d in dirs if d not in ignorar and not d.startswith('.')]
            for file in files:
                if file.endswith(('.pyc', '.pyo', '.log', '.zip')):
                    continue
                caminho_abs = os.path.join(root, file)
                caminho_rel = os.path.relpath(caminho_abs, raiz)
                zipf.write(caminho_abs, caminho_rel)
                
    tamanho = os.path.getsize(caminho_zip) / (1024 * 1024)
    print(f"✅ Backup concluído! Tamanho: {tamanho:.2f} MB")
    print(f"📁 Arquivo salvo em: _automacao/backups/{nome_zip}")

    # ============================================================
    # COMMIT E PUSH PARA O GITHUB
    # ============================================================
    print("\n📤 Fazendo commit e push das alterações para o GitHub...")
    
    # 1. Adiciona todas as alterações (o _automacao está no .gitignore, então não sobe)
    subprocess.run(["git", "add", "."], cwd=raiz)
    
    # 2. Faz o commit com a mensagem do marco
    commit_msg = "marco: nova etapa de revisão chatgpt e limpeza do waha"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=raiz)
    
    # 3. Cria a tag de versão
    tag_nome = f"v2.4-revisao-chatgpt-{agora}"
    subprocess.run(["git", "tag", "-a", tag_nome, "-m", "Versão estável após revisão do ChatGPT e limpeza do WAHA"], cwd=raiz)
    
    # 4. Faz o push da branch principal e da tag
    subprocess.run(["git", "push"], cwd=raiz)
    subprocess.run(["git", "push", "origin", tag_nome], cwd=raiz)
    
    print(f"✅ Push concluído! Tag criada: {tag_nome}")
    print("🎉 Processo finalizado com sucesso!")

if __name__ == "__main__":
    criar_backup_e_publicar()