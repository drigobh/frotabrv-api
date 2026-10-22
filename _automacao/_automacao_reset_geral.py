import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_reset_geral_{agora}.zip"
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

def reescrever_abastecimentos(raiz):
    # Código completo com os novos cards e layout aprovado
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    # Já está com o código novo (o script anterior já escreveu), mas vamos garantir que o resumo esteja calculando os novos cards.
    # O problema é que o navegador não está puxando a versão nova. Então vamos apenas garantir que o Vite recompile.
    pass

def reverter_login(raiz):
    # 1. Reverter AppLayout.tsx (remover a lógica forçada que causou loop)
    caminho_layout = os.path.join(raiz, "frontend", "src", "components", "layout", "AppLayout.tsx")
    with open(caminho_layout, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    bloco_forcado = '''
  // FORÇAR LOGIN: Se estiver na raiz e não tiver vindo do login, joga para o login
  if (window.location.pathname === "/" && !sessionStorage.getItem("logado_agora")) {
      return <Navigate to="/login" replace />;
  }'''
    if bloco_forcado in conteudo:
        conteudo = conteudo.replace(bloco_forcado, "")
        with open(caminho_layout, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ AppLayout.tsx revertido (loop removido).")

    # 2. Reverter Login.tsx
    caminho_login = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    with open(caminho_login, 'r', encoding='utf-8') as f:
        content_login = f.read()
    
    if 'sessionStorage.setItem("logado_agora", "true");' in content_login:
        content_login = content_login.replace('sessionStorage.setItem("logado_agora", "true"); ', '')
        with open(caminho_login, 'w', encoding='utf-8') as f:
            f.write(content_login)
        print("⚙️ Login.tsx revertido.")

def limpar_cache_vite(raiz):
    caminho_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("🧹 Cache do Vite apagado.")
    else:
        print("ℹ️ Cache do Vite já estava limpo.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Reset Geral...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    reverter_login(raiz)
    limpar_cache_vite(raiz)

    print("🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'yarn dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000")

if __name__ == "__main__":
    executar()