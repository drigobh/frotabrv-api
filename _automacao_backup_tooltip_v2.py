import os
import datetime
import zipfile

def backup():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(os.getcwd(), "_automacao", "backups", f"BACKUP_TOOLTIP_V2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta = os.path.join(os.getcwd(), "frontend", "src")
        for root, dirs, files in os.walk(pasta):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
            for file in files:
                c = os.path.join(root, file)
                r = os.path.relpath(c, os.getcwd())
                try: zipf.write(c, r)
                except: pass
    print(f"✅ Backup salvo: {caminho_zip}")

if __name__ == "__main__": backup()