import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_emergencia_500_{agora}.zip"
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

def corrigir_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Substitui a rota de listar por uma versão "à prova de falhas"
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
        print("⚙️ Backend: Rota de listagem corrigida para ser tolerante a dados antigos.")
    else:
        print("⚠️ A rota de listagem original não foi encontrada. Verifique se o arquivo já foi alterado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Emergência (Erro 500)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_backend(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'fix: corrigindo rota de listagem para aceitar dados antigos'")
    print("git push")

if __name__ == "__main__":
    executar()