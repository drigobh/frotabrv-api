import os
import datetime
import zipfile

def backup():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"BACKUP_MARCO_TEMPLATE_CHASSI_{agora}.zip"
    caminho_zip = os.path.join(os.getcwd(), "_automacao", "backups", nome_arquivo)
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    print("Criando backup completo (Código + Estrutura)...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ["app", "frontend"]:
            caminho_pasta = os.path.join(os.getcwd(), pasta)
            if not os.path.exists(caminho_pasta):
                continue
            
            for root, dirs, files in os.walk(caminho_pasta):
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

if __name__ == "__main__":
    backup()