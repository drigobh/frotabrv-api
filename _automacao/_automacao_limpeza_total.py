import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_limpeza_total_{agora}.zip"
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

def limpar_cache_frontend(raiz):
    # Apaga a pasta de cache do Vite para forçar a recompilação
    caminho_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("🧹 Cache do Vite (frontend) limpo com sucesso!")
    else:
        print("ℹ️ Cache do Vite já estava limpo.")

def forcar_limpeza_cookie_no_backend(raiz):
    # Altera o nome do cookie de sessão. Assim, o cookie antigo que está no navegador
    # não será mais reconhecido pelo backend, forçando o login.
    caminho = os.path.join(raiz, "app", "backend", "lib", "security.py")
    if not os.path.exists(caminho):
        print("❌ Erro: security.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    if 'COOKIE_NAME = "frota_session"' in conteudo:
        conteudo = conteudo.replace('COOKIE_NAME = "frota_session"', 'COOKIE_NAME = "frota_session_v2"')
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Backend: Nome do cookie alterado para 'frota_session_v2'.")
        print("   Isso vai forçar o navegador a pedir login novamente.")
    else:
        print("⚠️ Aviso: O cookie já foi alterado ou tem outro nome.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Limpeza Total...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    limpar_cache_frontend(raiz)
    forcar_limpeza_cookie_no_backend(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()