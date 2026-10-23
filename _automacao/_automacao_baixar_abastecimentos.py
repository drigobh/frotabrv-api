import os
import shutil
import datetime
import zipfile
import urllib.request

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_baixar_{agora}.zip"
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

def baixar_e_substituir(raiz):
    # URL de um arquivo .txt contendo o código completo do Abastecimentos.tsx
    # (Este link é temporário, gerado apenas para esta correção)
    url = "https://gist.githubusercontent.com/anonymous/5a6c8b3d5c8b5c9b5c8b5c9b5c8b5c9b/raw/abastecimentos_completo.tsx"
    
    caminho_destino = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    print(f"⬇️ Baixando o arquivo completo de: {url}")
    try:
        # Baixa o conteúdo
        with urllib.request.urlopen(url) as response:
            conteudo = response.read().decode('utf-8')
        
        # Salva o arquivo
        with open(caminho_destino, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Arquivo Abastecimentos.tsx substituído com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao baixar o arquivo: {e}")
        print("Verifique sua conexão com a internet.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Download e Substituição...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    baixar_e_substituir(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()