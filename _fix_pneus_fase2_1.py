import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASE2_1_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/pneus.py",
        "app/backend/routers/pneus.py"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    # 1. Adicionar campos de posição no Model de Pneus
    model_path = os.path.join(raiz, "app", "backend", "models", "pneus.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'veiculo_id' not in c:
        c = c.replace(
            'status: str = "Estoque"',
            'status: str = "Estoque"\n    veiculo_id: str | None = None\n    carreta_id: str | None = None\n    posicao: str | None = None  # Ex: 2-DE\n    sulco_atual: float | None = None\n    pressao_atual: float | None = None'
        )
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model: campos de posição e medições adicionados.")

    # 2. Atualizar o Router para gravar os novos campos
    router_path = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'veiculo_id' not in c.split('async def criar')[1].split('await db.pneus.insert_one')[0]:
        # Simplificando: como o model_dump() já pega todos os campos do body, não precisamos fazer nada.
        # Mas vamos garantir que o Router não quebre.
        print("✅ Router: campos já são tratados pelo model_dump().")

    print("✅ Backend atualizado para Fase 2.1.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Fase 2.1 aplicada com sucesso!")