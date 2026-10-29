import os
import subprocess
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DASH_ORIGINAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Dashboard.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Dashboard.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def reverter(raiz):
    print("🔄 Buscando o commit anterior ao Dashboard...")
    
    # 1. Listar os últimos commits
    try:
        logs = subprocess.check_output(["git", "log", "--oneline", "-n", "5"], cwd=raiz, text=True)
        print("Últimos commits:\n", logs)
        
        # 2. Pegar o hash do commit anterior (o penúltimo da lista)
        linhas = logs.strip().split('\n')
        if len(linhas) >= 2:
            commit_anterior = linhas[1].split()[0]
            print(f"🔄 Restaurando Dashboard.tsx do commit: {commit_anterior}")
            
            # Restaurar o arquivo
            subprocess.run(["git", "checkout", commit_anterior, "--", "frontend/src/pages/Dashboard.tsx"], check=True, cwd=raiz)
            print("✅ Dashboard.tsx restaurado para a versão anterior.")
            
            # Remover o script de backend se ele foi criado
            script_backend = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
            if os.path.exists(script_backend):
                # Também vamos reverter o backend para o commit anterior
                subprocess.run(["git", "checkout", commit_anterior, "--", "app/backend/routers/dashboard.py"], check=True, cwd=raiz)
                print("✅ dashboard.py do backend restaurado.")
        else:
            print("⚠️ Não foi possível encontrar um commit anterior.")
    except Exception as e:
        print(f"❌ Erro ao reverter: {e}")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    reverter(raiz)
    print("\n✅ Script finalizado! Faça o git push para atualizar o Render.")
    