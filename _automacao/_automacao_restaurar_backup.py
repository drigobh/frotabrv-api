import os
import shutil
import zipfile
import datetime

def restaurar_backup(raiz):
    # 1. Faz um backup de segurança do estado atual (por via das dúvidas)
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_estado_atual = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ESTADO_QUEBRADO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_estado_atual), exist_ok=True)
    
    print("📦 Salvando o estado atual (quebrado) por segurança...")
    with zipfile.ZipFile(caminho_estado_atual, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta)
            if os.path.exists(caminho_pasta):
                for root, dirs, files in os.walk(caminho_pasta):
                    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'dist', 'build', '__pycache__', '.venv']]
                    for file in files:
                        c = os.path.join(root, file)
                        r = os.path.relpath(c, raiz)
                        try: zipf.write(c, r)
                        except: pass

    # 2. Define o backup a ser restaurado
    nome_backup = "BACKUP_FULL_ANTES_HODOMETRO_20261023_103903.zip"
    caminho_backup = os.path.join(raiz, "_automacao", "backups", nome_backup)

    if not os.path.exists(caminho_backup):
        print(f"❌ Backup não encontrado: {caminho_backup}")
        return

    print(f"♻️ Iniciando restauração do backup: {nome_backup}")
    
    # 3. Apaga as pastas atuais (app e frontend) para extrair as limpas
    pastas_para_apagar = ['app', 'frontend']
    for pasta in pastas_para_apagar:
        caminho_pasta = os.path.join(raiz, pasta)
        if os.path.exists(caminho_pasta):
            print(f"🗑️ Removendo pasta atual: {pasta}")
            shutil.rmtree(caminho_pasta, ignore_errors=True)

    # 4. Extrai o backup
    print(f"📂 Extraindo arquivos do backup...")
    with zipfile.ZipFile(caminho_backup, 'r') as zipf:
        zipf.extractall(raiz)

    print("\n✅ RESTAURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("O sistema voltou ao estado exato de 23/10/2026 10:39:03.")

if __name__ == "__main__":
    raiz = os.getcwd()
    restaurar_backup(raiz)