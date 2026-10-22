import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    """Cria um backup do sistema inteiro, ignorando pastas pesadas."""
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_sistema_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema (isso pode levar alguns segundos)...")
    
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
                    except Exception as e:
                        print(f"⚠️ Aviso ao copiar {file}: {e}")

    with open(os.path.join(pasta_backups, f"backup_FULL_{agora}_LEIAME.txt"), "w", encoding="utf-8") as f:
        f.write(f"Backup Full gerado em: {agora}\n")
        f.write("Motivo: Criação das rotas básicas de API (veiculos, carretas, motoristas).\n")
        f.write("Estado anterior: Backend com apenas rota de auth.\n")
    
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def criar_arquivos_rotas(raiz):
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    os.makedirs(pasta_routers, exist_ok=True)

    # Rota de Veículos
    with open(os.path.join(pasta_routers, "veiculos.py"), "w", encoding="utf-8") as f:
        f.write('''from lib.cadastro_base import build_cadastro_router
from models.cadastros import VeiculoCreate, Veiculo

router = build_cadastro_router(
    prefix="/veiculos", collection="veiculos", entidade="Veículo",
    create_model=VeiculoCreate, out_model=Veiculo,
    unique_field="placa", unique_label="Placa", acop_field="veiculo_id", sort_field="placa"
)
''')

    # Rota de Carretas
    with open(os.path.join(pasta_routers, "carretas.py"), "w", encoding="utf-8") as f:
        f.write('''from lib.cadastro_base import build_cadastro_router
from models.cadastros import CarretaCreate, Carreta

router = build_cadastro_router(
    prefix="/carretas", collection="carretas", entidade="Carreta",
    create_model=CarretaCreate, out_model=Carreta,
    unique_field="codigo", unique_label="Código", acop_field="carreta_id", sort_field="codigo"
)
''')

    # Rota de Motoristas
    with open(os.path.join(pasta_routers, "motoristas.py"), "w", encoding="utf-8") as f:
        f.write('''from lib.cadastro_base import build_cadastro_router
from models.cadastros import MotoristaCreate, Motorista

router = build_cadastro_router(
    prefix="/motoristas", collection="motoristas", entidade="Motorista",
    create_model=MotoristaCreate, out_model=Motorista,
    unique_field="cnh", unique_label="CNH", acop_field="motorista_id", sort_field="nome"
)
''')
    print("✅ Arquivos de rotas (veiculos, carretas, motoristas) criados.")

def atualizar_server(raiz):
    caminho_server = os.path.join(raiz, "app", "backend", "server.py")
    if not os.path.exists(caminho_server):
        print("❌ Erro: server.py não encontrado.")
        return

    with open(caminho_server, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    imports = '''from routers import auth, veiculos, carretas, motoristas
api_router.include_router(auth.router)
api_router.include_router(veiculos.router)
api_router.include_router(carretas.router)
api_router.include_router(motoristas.router)'''

    alvo = 'from routers import auth\napi_router.include_router(auth.router)'
    
    if alvo in conteudo:
        conteudo = conteudo.replace(alvo, imports)
        with open(caminho_server, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ server.py atualizado com as novas rotas!")
    else:
        print("⚠️ Aviso: Não foi possível encontrar o bloco do auth no server.py para substituir.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação Full...")

    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    criar_arquivos_rotas(raiz)
    atualizar_server(raiz)

    print("🚀 Automação concluída! Reinicie o backend para testar.")

if __name__ == "__main__":
    executar()