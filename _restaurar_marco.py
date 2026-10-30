import os
import subprocess
import datetime
import zipfile

def backup_atual(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ANTES_DE_RESTAURAR_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    print("Criando backup de segurança do estado atual...")
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ["app", "frontend"]:
            caminho_pasta = os.path.join(raiz, pasta)
            if not os.path.exists(caminho_pasta):
                continue
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in 
                           ['node_modules', '__pycache__', 'backups', 'dist', 'build', '.git', '.vscode', '.idea']]
                for file in files:
                    c = os.path.join(root, file)
                    r = os.path.relpath(c, raiz)
                    try:
                        zipf.write(c, r)
                    except Exception:
                        pass
    print(f"✅ Backup do estado atual salvo em:\n{caminho_zip}")

def restaurar_marco(raiz):
    print("\n🔄 Buscando o último commit de marco no Git...")
    
    # Verifica se o git está disponível
    try:
        res = subprocess.run(["git", "status", "--short"], cwd=raiz, capture_output=True, text=True)
        if res.returncode != 0:
            print("❌ Git não está configurado ou não foi encontrado.")
            return
    except Exception as e:
        print(f"❌ Erro ao acessar o Git: {e}")
        return

    # Lista os últimos commits para o usuário ver
    print("\nÚltimos 5 commits:")
    log_res = subprocess.run(["git", "log", "--oneline", "-5"], cwd=raiz, capture_output=True, text=True)
    print(log_res.stdout)

    # O usuário precisa informar o hash do commit de marco
    print("\n⚠️  ATENÇÃO: Para restaurar, precisamos do hash do commit de MARCO.")
    print("   Veja na lista acima o commit que você quer restaurar (ex: o commit de 'MARCO').")
    print("   Se o commit de marco for o mais recente antes das alterações, ele pode ser o primeiro da lista.")
    
    hash_marco = input("\n👉 Digite o hash do commit de marco (ou pressione Enter para cancelar): ").strip()
    
    if not hash_marco:
        print("❌ Restauração cancelada pelo usuário.")
        return

    # Confirma a restauração
    print(f"\n⚠️  Isso vai sobrescrever TODAS as alterações não commitadas no código.")
    print(f"   Você está restaurando o commit: {hash_marco}")
    confirm = input("   Digite 'SIM' para confirmar a restauração: ").strip().upper()

    if confirm != "SIM":
        print("❌ Restauração cancelada.")
        return

    print(f"\n🔄 Restaurando o código para o commit {hash_marco}...")
    
    # Restaura os arquivos para o commit específico
    res = subprocess.run(["git", "checkout", hash_marco, "--", "frontend/", "app/"], cwd=raiz, capture_output=True, text=True)
    
    if res.returncode == 0:
        print("✅ Código restaurado com sucesso para o commit de marco!")
        print("\n📋 O que fazer agora:")
        print("1. O Vite vai recarregar automaticamente.")
        print("2. Verifique se o sistema voltou ao normal.")
        print("3. Se estiver tudo certo, faça commit das alterações restauradas:")
        print("   git add .")
        print('   git commit -m "revert: restaura código para o último marco estável"')
        print("   git push")
    else:
        print(f"❌ Erro ao restaurar: {res.stderr}")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup_atual(raiz)
    restaurar_marco(raiz)
    print("\n✅ Script finalizado.")