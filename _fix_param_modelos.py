import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PARAM_MODELOS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    # Procura o arquivo de rotas de parametrização
    arquivos = [
        "app/backend/routers/parametrizacao.py",
        "app/backend/routers/configuracoes.py"
    ]
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # Tenta achar o arquivo de rotas
    path = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    if not os.path.exists(path):
        path = os.path.join(raiz, "app", "backend", "routers", "configuracoes.py")

    if not os.path.exists(path):
        print("❌ Arquivo de rotas da parametrização não encontrado.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    alterado = False

    # 1. Adicionar o campo no modelo Pydantic (entrada)
    if "mostrar_seed_modelos: bool" not in c:
        # Procura a linha do marcas e adiciona o modelos logo abaixo
        if "mostrar_seed_marcas: bool = False" in c:
            c = c.replace(
                "mostrar_seed_marcas: bool = False",
                "mostrar_seed_marcas: bool = False\n    mostrar_seed_modelos: bool = False"
            )
            alterado = True
        elif "mostrar_seed_marcas: bool" in c:
            # Se não tiver o "= False", só adiciona a linha
            c = c.replace(
                "mostrar_seed_marcas: bool",
                "mostrar_seed_marcas: bool\n    mostrar_seed_modelos: bool = False"
            )
            alterado = True

    # 2. Adicionar o campo no dicionário de resposta padrão (GET)
    if '"mostrar_seed_modelos": False' not in c:
        if '"mostrar_seed_marcas": False' in c:
            c = c.replace(
                '"mostrar_seed_marcas": False',
                '"mostrar_seed_marcas": False, "mostrar_seed_modelos": False'
            )
            alterado = True

    # 3. Se o update for manual (ex: setando chaves uma por uma), garante que o modelos está lá
    if "doc[\"mostrar_seed_modelos\"]" not in c:
        if 'doc["mostrar_seed_marcas"]' in c:
            c = c.replace(
                'doc["mostrar_seed_marcas"] = body.mostrar_seed_marcas',
                'doc["mostrar_seed_marcas"] = body.mostrar_seed_marcas\n    doc["mostrar_seed_modelos"] = body.mostrar_seed_modelos'
            )
            alterado = True

    if alterado:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Campo 'mostrar_seed_modelos' injetado no modelo e na resposta com sucesso.")
    else:
        print("ℹ️ Backend: O campo já parece estar configurado ou a estrutura é diferente. Verifique manualmente se necessário.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    print("\n✅ Script finalizado! Faça o git push para o Render aplicar a mudança.")