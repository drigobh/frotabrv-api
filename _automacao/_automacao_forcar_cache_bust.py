import os
import shutil
import datetime
import zipfile
import time

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_cache_bust_{agora}.zip"
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

def forcar_cache_bust(raiz):
    # Altera o arquivo index.html para incluir um parâmetro de versão no script
    caminho_html = os.path.join(raiz, "frontend", "index.html")
    with open(caminho_html, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    timestamp = str(int(time.time()))
    
    # Substitui a tag do script principal do Vite
    if 'src="/src/main.tsx"' in conteudo:
        conteudo = conteudo.replace(
            'src="/src/main.tsx"', 
            f'src="/src/main.tsx?v={timestamp}"'
        )
        with open(caminho_html, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"⚙️ index.html atualizado com hash de versão: v={timestamp}")
    else:
        print("⚠️ A tag do script main.tsx não foi encontrada no index.html.")

def criar_atalho_anonimo(raiz):
    # Cria um arquivo .bat para abrir o Chrome em modo anônimo direto no localhost
    caminho_bat = os.path.join(raiz, "abrir_sistema_anonimo.bat")
    with open(caminho_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('start chrome --incognito http://localhost:3000\n')
    print(f"✅ Atalho criado: abrir_sistema_anonimo.bat")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Cache Bust...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    forcar_cache_bust(raiz)
    criar_atalho_anonimo(raiz)

    print("\n🚀 Automação concluída! Siga os passos abaixo:")
    print("1. Pare o Vite (Ctrl+C) e rode 'yarn dev' novamente.")
    print("2. Dê um duplo clique no arquivo 'abrir_sistema_anonimo.bat' que foi criado na raiz.")
    print("   (Isso vai abrir o Chrome em modo anônimo, ignorando todo o cache)")

if __name__ == "__main__":
    executar()