import os
import shutil
import datetime
import zipfile
import requests

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_emergencia_{agora}.zip"
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

def corrigir_backend_500(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. A rota de listar (`GET`) precisa ser resiliente a dados antigos que não têm os novos campos
    rota_antiga = '''@router.get("", response_model=list[Abastecimento])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.abastecimentos.find({}, {"_id": 0}).sort("data", -1).to_list(1000)
    return [Abastecimento(**d) for d in docs]'''

    rota_nova = '''@router.get("", response_model=list[Abastecimento])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.abastecimentos.find({}, {"_id": 0}).sort("data", -1).to_list(1000)
    # Garante que todos os documentos tenham os campos novos (mesmo os antigos)
    for d in docs:
        if "numero_nf" not in d: d["numero_nf"] = None
        if "chave_nfe" not in d: d["chave_nfe"] = None
        if "hora" not in d: d["hora"] = None
        if "cnpj" not in d: d["cnpj"] = None
        if "fornecedor" not in d: d["fornecedor"] = None
        if "origem" not in d: d["origem"] = "manual"
    return [Abastecimento(**d) for d in docs]'''

    if rota_antiga in conteudo:
        conteudo = conteudo.replace(rota_antiga, rota_nova)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Backend: Rota de listagem corrigida para ser resiliente a dados antigos.")
    else:
        print("⚠️ A rota de listagem original não foi encontrada. O arquivo pode já ter sido alterado.")

def testar_mongo():
    print("\n🔍 Testando conexão direta com o MongoDB (para ver se os dados existem)...")
    # Usando a URL que está no .env (vamos tentar ler do arquivo)
    env_path = os.path.join(os.getcwd(), "app", "backend", ".env")
    if not os.path.exists(env_path):
        print("❌ Arquivo .env não encontrado. Não é possível testar o Mongo.")
        return

    with open(env_path, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    import re
    mongo_url_match = re.search(r'MONGO_URL=(.+)', env_content)
    if not mongo_url_match:
        print("❌ MONGO_URL não encontrada no .env.")
        return

    mongo_url = mongo_url_match.group(1).strip()
    
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_url)
        db = client.get_database() # Pega o DB_NAME do final da URL
        count = db["abastecimentos"].count_documents({})
        print(f"✅ Conexão com Mongo OK. Total de abastecimentos na coleção: {count}")
        if count == 0:
            print("⚠️ ALERTA: A coleção de abastecimentos está VAZIA no banco de dados!")
    except Exception as e:
        print(f"❌ Erro ao conectar no MongoDB: {e}")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Emergência (Erro 500)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_backend_500(raiz)
    testar_mongo()

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'fix: corrigindo rota de listagem para aceitar dados antigos'")
    print("git push")

if __name__ == "__main__":
    executar()