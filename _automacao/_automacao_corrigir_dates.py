import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_fix_dates_{agora}.zip")
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
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo abastecimentos.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui o import errado pelo correto
    conteudo = conteudo.replace("from lib.time import now_iso", "from lib.dates import now_iso")
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Import corrigido para 'from lib.dates import now_iso'.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    corrigir(raiz)
    print("\n🚀 Faça o commit e push para o Render.")