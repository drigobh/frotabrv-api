import os
import shutil
import datetime
import zipfile
import requests

API_URL = "https://frotabrv-api.onrender.com/api"
EMAIL = "admin@frotabrv.com"
SENHA = "admin123"

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_inativar_{agora}.zip"
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

def inativar_veiculos():
    print("🔄 Inativando veículos SR remanescentes...")
    session = requests.Session()
    
    # Login
    res = session.post(f"{API_URL}/auth/login", json={"email": EMAIL, "senha": SENHA})
    if res.status_code != 200:
        print(f"❌ Falha no login: {res.text}")
        return

    # Buscar veículos ativos
    res = session.get(f"{API_URL}/veiculos")
    veiculos = res.json()
    
    inativados = 0
    for v in veiculos:
        # Verifica se o modelo contém "SR"
        if "SR" in v.get("modelo", "").upper():
            print(f"🔄 Inativando: {v['placa']} - {v['modelo']}")
            
            # Chama a rota correta de status (PATCH)
            res_patch = session.patch(
                f"{API_URL}/veiculos/{v['id']}/status", 
                json={"ativo": False}
            )
            
            if res_patch.status_code == 200:
                print(f"✅ Inativado com sucesso.")
                inativados += 1
            else:
                print(f"⚠️ Erro ao inativar: {res_patch.status_code} - {res_patch.text}")

    print(f"🎉 Concluído! {inativados} veículos inativados.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Inativação de Veículos SR...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    inativar_veiculos()

    print("\n🚀 Tudo pronto!")

if __name__ == "__main__":
    executar()