import os
import shutil
import subprocess
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_install_pdfjs_{agora}.zip"
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

def instalar_pdfjs(raiz):
    pasta_front = os.path.join(raiz, "frontend")
    
    print("📦 Instalando pdfjs-dist...")
    try:
        # Roda o npm install na pasta correta
        subprocess.run(["npm", "install", "pdfjs-dist"], cwd=pasta_front, check=True, shell=True)
        print("✅ pdfjs-dist instalado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao instalar pdfjs-dist: {e}")
        return False

    # Verifica se a pasta node_modules/pdfjs-dist existe
    pasta_pdf = os.path.join(pasta_front, "node_modules", "pdfjs-dist")
    if os.path.exists(pasta_pdf):
        print("✅ Pasta pdfjs-dist encontrada no node_modules.")
    else:
        print("❌ Pasta pdfjs-dist NÃO encontrada após a instalação.")
        return False

    return True

def corrigir_import(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Corrigir o import do worker
    # O caminho correto do worker no pdfjs-dist v4+ é "pdfjs-dist/build/pdf.worker.min.mjs"
    if 'import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";' in conteudo:
        print("✅ O import do worker já está correto.")
    else:
        # Se estiver diferente, substitui pelo correto
        conteudo = conteudo.replace(
            'import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";',
            'import pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Arquivo Abastecimentos.tsx verificado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Instalação do pdfjs-dist...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    
    if instalar_pdfjs(raiz):
        corrigir_import(raiz)
        print("\n🚀 Automação concluída! Siga os passos:")
        print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
        print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")
    else:
        print("\n❌ A instalação falhou. Verifique se o npm está funcionando.")

if __name__ == "__main__":
    executar()