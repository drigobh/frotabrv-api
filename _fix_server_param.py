import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_SERVER_PARAM_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "app", "backend", "server.py")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "app/backend/server.py")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remover a linha duplicada de import
    c = c.replace(
        'from routers import parametrizacao, admin\n',
        'from routers import admin\n'
    )
    print("✅ Import duplicado removido.")

    # 2. Remover o include_router da parametrizacao no app (fora do api_router)
    c = c.replace('app.include_router(parametrizacao.router)\n', '')
    c = c.replace('app.include_router(parametrizacao.router)', '')
    print("✅ Include fora do api_router removido.")

    # 3. Adicionar o include_router dentro do api_router (antes do app.include_router(api_router))
    if 'api_router.include_router(parametrizacao.router)' not in c:
        c = c.replace(
            'api_router.include_router(manutencoes.router)',
            'api_router.include_router(manutencoes.router)\napi_router.include_router(parametrizacao.router)'
        )
        print("✅ Include adicionado dentro do api_router.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)