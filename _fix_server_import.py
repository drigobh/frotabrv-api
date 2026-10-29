import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FIX_SERVER_IMPORT_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "app", "backend", "server.py")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "app/backend/server.py")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "server.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    for i in range(len(linhas)):
        # Corrige a linha que tem "from routers import empresa," isolada
        if linhas[i].strip() == 'from routers import empresa,':
            linhas[i] = 'from routers import empresa\n'
        
        # Corrige se por acaso ficou "from routers import empresa, auth" (na mesma linha)
        if 'from routers import empresa, ' in linhas[i]:
            linhas[i] = linhas[i].replace('from routers import empresa, ', 'from routers import empresa, ')
            # Vamos remover o import avulso que criamos e deixar o original
            if 'from routers import tipos_fornecedores,' in linhas[i]:
                linhas[i] = 'from routers import empresa, tipos_fornecedores, parametrizacao, auth, movimentacoes, pecas, fornecedores, combustiveis, veiculos, carretas, motoristas, dashboard, acoplamentos, abastecimentos, manutencoes\n'

    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print("✅ server.py corrigido: vírgula removida e import agrupado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)