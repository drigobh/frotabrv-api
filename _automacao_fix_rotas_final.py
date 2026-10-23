import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_fix_rotas_final_{agora}.zip")
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

def corrigir(raiz):
    # 1. Corrige o abastecimentos.py
    caminho_abast = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    if os.path.exists(caminho_abast):
        with open(caminho_abast, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Garante que o prefixo está no router
        if 'router = APIRouter(tags=["Abastecimentos"])' in conteudo:
            conteudo = conteudo.replace(
                'router = APIRouter(tags=["Abastecimentos"])',
                'router = APIRouter(prefix="/api/abastecimentos", tags=["Abastecimentos"])'
            )
            print("✅ Prefixo re-adicionado ao abastecimentos.py.")
        
        with open(caminho_abast, 'w', encoding='utf-8') as f:
            f.write(conteudo)

    # 2. Corrige o server.py
    caminho_server = os.path.join(raiz, "app", "backend", "server.py")
    if os.path.exists(caminho_server):
        with open(caminho_server, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Remove APENAS o include_router de abastecimentos (pois já tem prefixo no router)
        # Não mexe nos outros!
        conteudo = re.sub(r'app\.include_router\(abastecimentos\.router[^\)]*\)\n', '', conteudo)
        
        with open(caminho_server, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ include_router de abastecimentos removido do server.py.")
    print("✅ Correções aplicadas.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    corrigir(raiz)
    print("\n🚀 Faça o commit e push para o Render.")