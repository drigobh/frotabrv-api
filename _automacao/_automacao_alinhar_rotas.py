import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_alinhar_rotas_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta = os.path.join(raiz, "app", "backend")
        for root, dirs, files in os.walk(pasta):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'backups']]
            for file in files:
                c = os.path.join(root, file)
                r = os.path.relpath(c, raiz)
                try: zipf.write(c, r)
                except: pass
    print("📦 Backup criado.")

def alinhar(raiz):
    caminho_server = os.path.join(raiz, "app", "backend", "server.py")
    caminho_abast = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")

    if not os.path.exists(caminho_server) or not os.path.exists(caminho_abast):
        print("❌ Arquivos não encontrados.")
        return

    with open(caminho_server, 'r', encoding='utf-8') as f:
        server_conteudo = f.read()

    # Verifica se o server.py usa prefixo no include_router
    # Ex: app.include_router(abastecimentos.router, prefix="/api/abastecimentos")
    # Ou se o prefixo está no próprio arquivo de rotas.

    with open(caminho_abast, 'r', encoding='utf-8') as f:
        abast_conteudo = f.read()

    # 1. Garante que o arquivo abastecimentos.py NÃO tenha prefixo, para evitar duplicação
    if 'router = APIRouter(prefix="/api/abastecimentos"' in abast_conteudo:
        abast_conteudo = abast_conteudo.replace(
            'router = APIRouter(prefix="/api/abastecimentos", tags=["Abastecimentos"])',
            'router = APIRouter(tags=["Abastecimentos"])'
        )
        print("✅ Prefixo removido do abastecimentos.py (será controlado pelo server.py).")

    # 2. Garante que as rotas no abastecimentos.py estejam corretas (sem /api/abastecimentos no path)
    # O server.py vai cuidar do prefixo.
    # A rota "importar" deve ser apenas "/importar"
    if '@router.post("/api/abastecimentos/importar")' in abast_conteudo:
        abast_conteudo = abast_conteudo.replace(
            '@router.post("/api/abastecimentos/importar")',
            '@router.post("/importar")'
        )
        print("✅ Rota 'importar' corrigida para apenas '/importar'.")

    # 3. Verifica se o server.py inclui o router corretamente
    if "app.include_router(abastecimentos.router" not in server_conteudo:
        print("⚠️ O server.py não parece incluir o router de abastecimentos. Verifique manualmente.")
    else:
        # Verifica se o server.py tem um prefixo definido para o router
        match = re.search(r'app\.include_router\(abastecimentos\.router,\s*prefix=["\']([^"\']+)["\']', server_conteudo)
        if match:
            prefixo = match.group(1)
            print(f"✅ O server.py usa o prefixo: {prefixo}")
            # Se o prefixo for /api/abastecimentos, está correto
            if prefixo == "/api/abastecimentos":
                print("✅ O prefixo está correto.")
            else:
                print(f"⚠️ O prefixo no server.py é {prefixo}, mas esperávamos /api/abastecimentos.")
        else:
            print("⚠️ O server.py não tem prefixo definido no include_router. Vamos adicionar.")
            # Adiciona o prefixo no server.py se não existir
            server_conteudo = re.sub(
                r'app\.include_router\(abastecimentos\.router\)',
                'app.include_router(abastecimentos.router, prefix="/api/abastecimentos")',
                server_conteudo
            )
            with open(caminho_server, 'w', encoding='utf-8') as f:
                f.write(server_conteudo)
            print("✅ Prefixo adicionado no server.py.")

    with open(caminho_abast, 'w', encoding='utf-8') as f:
        f.write(abast_conteudo)
    print("✅ abastecimentos.py atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    alinhar(raiz)
    print("\n🚀 Faça o commit e push para o Render.")