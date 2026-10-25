import os
import datetime
import zipfile

def backup():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(os.getcwd(), "_automacao", "backups", f"BACKUP_ESTOQUE_V3_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ["app", "frontend"]:
            caminho_pasta = os.path.join(os.getcwd(), pasta)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', 'backups', 'dist', 'build', '.git']]
                for file in files:
                    c = os.path.join(root, file)
                    r = os.path.relpath(c, os.getcwd())
                    try: zipf.write(c, r)
                    except: pass
    print(f"✅ Backup salvo: {caminho_zip}")

if __name__ == "__main__": backup()