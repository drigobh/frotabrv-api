import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_campeoes_{agora}.zip"
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

def corrigir_model_dashboard(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "dashboard.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Altera o import e o tipo de Campeao para CampeaoMes
    if "from models.ranking import CampeaoMes" not in conteudo:
        conteudo = conteudo.replace(
            "from models.acoplamentos import HistoricoItem",
            "from models.acoplamentos import HistoricoItem\nfrom models.ranking import CampeaoMes"
        )

    # Altera a definição da classe Campeoes
    alvo_classe = '''class Campeoes(BaseModel):
    mes_passado: Campeao | None = None
    mes_atual: Campeao | None = None'''
    
    nova_classe = '''class Campeoes(BaseModel):
    mes_passado: CampeaoMes | None = None
    mes_atual: CampeaoMes | None = None'''

    if alvo_classe in conteudo:
        conteudo = conteudo.replace(alvo_classe, nova_classe)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ models/dashboard.py corrigido para usar CampeaoMes.")
    else:
        print("⚠️ Classe Campeoes não encontrada no modelo (pode já ter sido corrigida).")

def verificar_abastecimentos(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    if "@router.get(\"/ultimo-km/{veiculo_id}\")" in conteudo:
        print("✅ Rota de ultimo-km existe no backend.")
    else:
        print("⚠️ A rota ultimo-km NÃO está no arquivo abastecimentos.py. Vamos recriá-la.")
        rota = '''
@router.get("/ultimo-km/{veiculo_id}")
async def ultimo_km(veiculo_id: str, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id}, 
        sort=[("km", -1)]
    )
    
    km_veiculo = veiculo.get("hodometro_km", 0)
    km_abast = ultimo_abast["km"] if ultimo_abast else 0
    
    return {"ultimo_km": max(km_veiculo, km_abast)}
'''
        # Insere antes do POST
        alvo = '@router.post("", response_model=Abastecimento, status_code=201)'
        conteudo = conteudo.replace(alvo, rota + "\n" + alvo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Rota de ultimo-km recriada no abastecimentos.py.")

def verificar_server(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    if "api_router.include_router(abastecimentos.router)" in conteudo:
        print("✅ server.py inclui a rota de abastecimentos.")
    else:
        print("⚠️ server.py NÃO inclui a rota de abastecimentos. Corrigindo...")
        conteudo = conteudo.replace(
            "api_router.include_router(manutencoes.router)",
            "api_router.include_router(manutencoes.router)\napi_router.include_router(abastecimentos.router)"
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ server.py corrigido.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção dos Campeões...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_model_dashboard(raiz)
    verificar_abastecimentos(raiz)
    verificar_server(raiz)

    print("🚀 Automação concluída! Faça o commit e push para o Render.")

if __name__ == "__main__":
    executar()
    