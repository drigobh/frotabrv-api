import os
import datetime
import zipfile

def backup_marco():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome = f"MARCO_PNEUS_VISUAL_{agora}.zip"
    caminho_zip = os.path.join(os.getcwd(), "_automacao", "backups", nome)
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)

    print("Iniciando backup do marco (Módulo de Pneus Visual)...")
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ["app", "frontend"]:
            caminho_pasta = os.path.join(os.getcwd(), pasta)
            if not os.path.exists(caminho_pasta):
                continue
            
            for root, dirs, files in os.walk(caminho_pasta):
                # Ignora pastas de build e cache para o zip ficar leve
                dirs[:] = [d for d in dirs if d not in 
                           ['node_modules', '__pycache__', 'backups', 'dist', 'build', '.git', '.vscode', '.idea']]
                
                for file in files:
                    c = os.path.join(root, file)
                    r = os.path.relpath(c, os.getcwd())
                    try:
                        zipf.write(c, r)
                    except Exception:
                        pass
                        
    print(f"✅ Backup do MARCO salvo com sucesso em:\n{caminho_zip}")
    print("Tamanho do arquivo:", round(os.path.getsize(caminho_zip) / (1024*1024), 2), "MB")

if __name__ == "__main__":
    backup_marco()