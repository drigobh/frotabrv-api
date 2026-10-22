import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_dedupe_{agora}.zip"
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

def corrigir_vite_config(raiz):
    caminho = os.path.join(raiz, "frontend", "vite.config.ts")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Verifica se o resolve já existe
    if "resolve: {" in conteudo:
        # Se já existe, insere o dedupe dentro dele
        if "dedupe:" not in conteudo:
            conteudo = conteudo.replace(
                "resolve: {",
                "resolve: {\n      dedupe: ['react', 'react-dom', 'react-router-dom'],"
            )
    else:
        # Se não existe, cria um bloco resolve antes do server
        bloco_resolve = """
    resolve: {
      dedupe: ['react', 'react-dom', 'react-router-dom'],
    },
    """
        # Insere antes do "server: {"
        conteudo = conteudo.replace("    server: {", bloco_resolve + "    server: {")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ vite.config.ts atualizado com dedupe do React.")

def limpar_cache(raiz):
    caminho_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("🧹 Cache do Vite apagado para forçar recompilação.")
    else:
        print("ℹ️ Cache do Vite já estava limpo.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do React (Dedupe)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_vite_config(raiz)
    limpar_cache(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. No terminal, rode: cd frontend")
    print("2. Rode: yarn dev")
    print("3. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000")

if __name__ == "__main__":
    executar()
    