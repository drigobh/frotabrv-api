import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_forcar_{agora}.zip"
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

def forcar_login_definitivo(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "AppLayout.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # A lógica atual redireciona se não houver user. Vamos forçar a ida para o login
    # caso o usuário tente acessar a raiz (index) sem ter acabado de logar.
    alvo = 'if (isError || !user) return <Navigate to="/login" replace />;'
    novo = '''if (isError || !user) return <Navigate to="/login" replace />;
  
  // FORÇAR LOGIN: Se estiver na raiz e não tiver vindo do login, joga para o login
  if (window.location.pathname === "/" && !sessionStorage.getItem("logado_agora")) {
      return <Navigate to="/login" replace />;
  }'''
    
    if alvo in conteudo:
        conteudo = conteudo.replace(alvo, novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ AppLayout.tsx alterado para forçar o login se não houver sessão recente.")
    else:
        print("⚠️ Aviso: O padrão de login não foi encontrado no AppLayout.tsx.")

    # Altera o Login.tsx para setar a flag ao logar
    caminho_login = os.path.join(raiz, "frontend", "src", "pages", "Login.tsx")
    if os.path.exists(caminho_login):
        with open(caminho_login, 'r', encoding='utf-8') as f:
            content_login = f.read()
        # Antes de navegar para "/", salva a flag
        if 'navigate("/")' in content_login:
            content_login = content_login.replace('navigate("/")', 'sessionStorage.setItem("logado_agora", "true"); navigate("/")')
        elif 'navigate("/dashboard")' in content_login:
            content_login = content_login.replace('navigate("/dashboard")', 'sessionStorage.setItem("logado_agora", "true"); navigate("/dashboard")')
            
        with open(caminho_login, 'w', encoding='utf-8') as f:
            f.write(content_login)
        print("⚙️ Login.tsx alterado para registrar a sessão.")

def forcar_css_cards(raiz):
    caminho_css = os.path.join(raiz, "frontend", "src", "index.css")
    with open(caminho_css, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Adiciona regras CSS para forçar o tamanho dos cards no final do arquivo
    regras_css = '''
/* FORÇAR TAMANHO DOS CARDS DO DASHBOARD */
article[data-testid^="kpi-"] {
    padding: 12px !important;
    height: 120px !important;
    max-height: 120px !important;
}
article[data-testid^="kpi-"] p.font-heading {
    font-size: 24px !important;
    margin-top: 4px !important;
}
article[data-testid^="kpi-"] .mt-1.h-6 {
    height: 32px !important;
    margin-top: 8px !important;
}
'''
    if "FORÇAR TAMANHO DOS CARDS" not in conteudo:
        with open(caminho_css, 'a', encoding='utf-8') as f:
            f.write(regras_css)
        print("⚙️ index.css atualizado com regras de tamanho dos cards.")
    else:
        print("✅ index.css já possui as regras de tamanho.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação Forçada...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    forcar_login_definitivo(raiz)
    forcar_css_cards(raiz)

    print("🚀 Automação concluída! Faça o commit e reinicie o frontend.")

if __name__ == "__main__":
    executar()
    