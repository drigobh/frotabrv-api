import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MODEL_PLANO_ERRO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "app", "backend", "models", "planos_manutencao.py")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "app/backend/models/planos_manutencao.py")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "planos_manutencao.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Substitui a linha corrompida pela versão correta
    for i in range(len(linhas)):
        if 'carreta_id' in linhas[i]:
            linhas[i] = '    carreta_id: str | None = None\n'

    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    print("✅ Model corrigido: linha do 'carreta_id' limpa.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")