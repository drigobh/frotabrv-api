import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_fix_time_{agora}.zip")
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

def corrigir_imports(raiz):
    # 1. Descobre onde está now_iso
    pasta_lib = os.path.join(raiz, "app", "backend", "lib")
    origem_now_iso = None
    
    if os.path.exists(pasta_lib):
        for file in os.listdir(pasta_lib):
            if file.endswith(".py"):
                with open(os.path.join(pasta_lib, file), 'r', encoding='utf-8') as f:
                    if "def now_iso" in f.read():
                        origem_now_iso = f"lib.{file[:-3]}"
                        break

    if not origem_now_iso:
        print("❌ Função 'now_iso' não encontrada na pasta lib.")
        return

    print(f"✅ Função 'now_iso' encontrada em: {origem_now_iso}")

    # 2. Corrige o abastecimentos.py
    caminho_abast = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    if os.path.exists(caminho_abast):
        with open(caminho_abast, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            
        # Substitui o import errado pelo correto
        conteudo = re.sub(r'from lib\.time import now_iso', f'from {origem_now_iso} import now_iso', conteudo)
        
        with open(caminho_abast, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Import corrigido no arquivo abastecimentos.py.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    corrigir_imports(raiz)
    print("\n🚀 Faça o commit e push para o Render.")