import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_server_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print("📦 Criando Backup Rápido...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_backend = os.path.join(raiz, "app", "backend")
        if os.path.exists(pasta_backend):
            for root, dirs, files in os.walk(pasta_backend):
                dirs[:] = [d for d in dirs if d not in ['__pycache__', 'backups']]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup salvo: {nome_backup}")

def injetar_rota(raiz):
    # Caminho do server.py
    caminho_server = os.path.join(raiz, "app", "backend", "server.py")
    
    if not os.path.exists(caminho_server):
        print("❌ server.py não encontrado.")
        return

    with open(caminho_server, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adiciona o import do admin, se não existir
    if "from routers import admin" not in conteudo:
        # Procura por "from routers import" (outros routers) e adiciona depois
        if "from routers import" in conteudo:
            linhas = conteudo.split('\n')
            for i, linha in enumerate(linhas):
                if linha.startswith("from routers import"):
                    linhas.insert(i + 1, "from routers import admin")
                    break
            conteudo = '\n'.join(linhas)
            print("✅ Import do admin adicionado após outro import de routers.")
        else:
            # Se não achar, adiciona no topo
            conteudo = "from routers import admin\n" + conteudo
            print("✅ Import do admin adicionado no topo.")
    else:
        print("ℹ️ Import do admin já existe.")

    # 2. Adiciona o include_router, se não existir
    if "app.include_router(admin.router)" not in conteudo:
        # Procura por "app.include_router(" (outros routers) e adiciona depois
        if "app.include_router(" in conteudo:
            linhas = conteudo.split('\n')
            for i, linha in enumerate(linhas):
                if linha.startswith("app.include_router("):
                    linhas.insert(i + 1, "app.include_router(admin.router)")
                    break
            conteudo = '\n'.join(linhas)
            print("✅ include_router do admin adicionado após outro include_router.")
        else:
            # Se não achar, adiciona após "app = FastAPI()"
            if "app = FastAPI()" in conteudo:
                conteudo = conteudo.replace(
                    "app = FastAPI()",
                    "app = FastAPI()\napp.include_router(admin.router)"
                )
                print("✅ include_router do admin adicionado após app = FastAPI().")
            else:
                print("⚠️ Não foi possível encontrar 'app = FastAPI()' ou outros include_router. Adicione manualmente.")
    else:
        print("ℹ️ include_router do admin já existe.")

    with open(caminho_server, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ server.py atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Injeção da Rota Admin no server.py...")
    criar_backup_rapido(raiz)
    injetar_rota(raiz)
    print("\n🚀 Concluído! Agora faça o commit e push para o Render.")