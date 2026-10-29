import os
import datetime
import zipfile
import subprocess

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_REVERTER_DASH_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    print(f"✅ Backup de segurança salvo: {caminho_zip}")
    return caminho_zip

def reverter(raiz):
    print("\n🔄 Revertendo o Dashboard...")

    # 1. Restaurar o frontend Dashboard.tsx do Git
    try:
        subprocess.run(["git", "checkout", "HEAD", "--", "frontend/src/pages/Dashboard.tsx"], check=True, cwd=raiz)
        print("✅ frontend/src/pages/Dashboard.tsx restaurado do Git.")
    except Exception as e:
        print(f"⚠️ Erro ao restaurar Dashboard.tsx: {e}")

    # 2. Restaurar o backend dashboard.py do Git
    try:
        subprocess.run(["git", "checkout", "HEAD", "--", "app/backend/routers/dashboard.py"], check=True, cwd=raiz)
        print("✅ app/backend/routers/dashboard.py restaurado do Git.")
    except Exception as e:
        print(f"⚠️ Erro ao restaurar dashboard.py: {e}")

    # 3. Remover scripts temporários de dashboard (se existirem)
    for script in ["_add_dashboard_backend.py", "_add_dashboard_frontend.py"]:
        caminho = os.path.join(raiz, script)
        if os.path.exists(caminho):
            try:
                os.remove(caminho)
                print(f"🗑️ Script temporário removido: {script}")
            except Exception as e:
                print(f"⚠️ Erro ao remover {script}: {e}")

if __name__ == "__main__":
    raiz = os.getcwd()
    caminho_zip = backup(raiz)
    reverter(raiz)
    print("\n✅ Reversão concluída! Agora faça o git push para atualizar o Render.")