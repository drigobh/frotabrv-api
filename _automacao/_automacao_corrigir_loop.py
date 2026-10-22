import os
import shutil
import datetime
import zipfile
import subprocess

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_corrigir_loop_{agora}.zip"
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

def reverter_react_router(raiz):
    # 1. Reverter AppLayout.tsx
    caminho_layout = os.path.join(raiz, "frontend", "src", "components", "layout", "AppLayout.tsx")
    with open(caminho_layout, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Remove a lógica de "logado_agora" que causou o loop
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

def limpar_navegador_e_cookies():
    print("🧹 Fechando o Chrome para limpar os cookies...")
    # Fecha o Chrome à força
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("✅ Chrome fechado. Por favor, reabra o Chrome e acesse http://localhost:3000")
    print("💡 Dica: Se ainda não aparecer o login, abra uma janela anônima (Ctrl+Shift+N).")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    reverter_react_router(raiz)
    limpar_navegador_e_cookies()

    print("🚀 Automação concluída! Reinicie o frontend e teste no navegador limpo.")

if __name__ == "__main__":
    executar()