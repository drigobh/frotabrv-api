import os
import re
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_fix_prefixo_{agora}.zip")
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

def corrigir_server(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    
    if not os.path.exists(caminho):
        print("❌ server.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Remove TODOS os prefixos dos include_router, pois os routers já têm o prefixo interno
    # Ex: app.include_router(auth.router, prefix="/api/auth") -> app.include_router(auth.router)
    conteudo = re.sub(r'(app\.include_router\(\w+\.router),\s*prefix=["\'][^"\']+["\']\)', r'\1)', conteudo)

    # Caso o router de abastecimentos também tenha prefixo duplicado, remove
    conteudo = re.sub(r'(app\.include_router\(abastecimentos\.router),\s*prefix=["\'][^"\']+["\']\)', r'\1)', conteudo)
    conteudo = re.sub(r'(app\.include_router\(admin\.router),\s*prefix=["\'][^"\']+["\']\)', r'\1)', conteudo)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Prefixos duplicados removidos do server.py.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    corrigir_server(raiz)
    print("\n🚀 Faça o commit e push para o Render.")
    