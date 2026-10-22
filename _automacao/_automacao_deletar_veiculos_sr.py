import os
import shutil
import datetime
import zipfile
from pymongo import MongoClient

# ATENÇÃO: Cole aqui a sua string de conexão do MongoDB Atlas
MONGO_URL = "mongodb+srv://drigobh_db_user:JTj1TazGWEC1oUV@cluster0.0nmnif3.mongodb.net/frotabrv?retryWrites=true&w=majority"

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_delete_sr_{agora}.zip"
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

def deletar_direto_no_mongo():
    print("🔄 Conectando ao MongoDB Atlas...")
    try:
        client = MongoClient(MONGO_URL)
        db = client["frotabrv"]
        veiculos_col = db["veiculos"]
        carretas_col = db["carretas"]

        # 1. Deletar veículos com "SR"
        query = {"modelo": {"$regex": "SR", "$options": "i"}}
        count = veiculos_col.count_documents(query)
        print(f"Encontrados {count} veículos 'SR' para deletar.")
        
        if count > 0:
            res = veiculos_col.delete_many(query)
            print(f"🗑️ {res.deleted_count} veículos deletados permanentemente do banco.")

        # 2. Reativar as carretas que o script anterior inativou por engano
        res_reativar = carretas_col.update_many(
            {"ativo": False}, 
            {"$set": {"ativo": True}}
        )
        if res_reativar.modified_count > 0:
            print(f"🔄 {res_reativar.modified_count} carretas foram reativadas.")

        print("🎉 Concluído!")
    except Exception as e:
        print(f"❌ Erro ao conectar ou deletar no MongoDB: {e}")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Exclusão Definitiva...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    deletar_direto_no_mongo()

if __name__ == "__main__":
    executar()