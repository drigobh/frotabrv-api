import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DATA_ACOPL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    for arquivo in ["models/acoplamentos.py", "routers/acoplamentos.py"]:
        caminho_abs = os.path.join(raiz, "app", "backend", arquivo.replace("/", os.sep))
        if os.path.exists(caminho_abs):
            with zipfile.ZipFile(caminho_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(caminho_abs, f"app/backend/{arquivo}")

    caminho_front = os.path.join(raiz, "frontend", "src", "pages", "Acoplamentos.tsx")
    if os.path.exists(caminho_front):
        with zipfile.ZipFile(caminho_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_front, "frontend/src/pages/Acoplamamentos.tsx")
            
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Corrigir o Model para aceitar as datas
    path_model = os.path.join(raiz, "app", "backend", "models", "acoplamentos.py")
    if os.path.exists(path_model):
        with open(path_model, 'r', encoding='utf-8') as f:
            c = f.read()
        
        # Se o AcoplamentoCreate não tem data_inicio, injetamos
        if 'class AcoplamentoCreate' in c:
            # Adiciona data_inicio e data_fim se não existirem no Create ou no Base
            if 'data_inicio' not in c:
                c = c.replace(
                    'class AcoplamentoCreate(BaseModel):\n',
                    'class AcoplamentoCreate(BaseModel):\n    data_inicio: str | None = None\n    data_fim: str | None = None\n'
                )
            with open(path_model, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Model garantido com campos de data.")

    # 2. Corrigir o Router (salvar datas no POST e preencher no GET para registros antigos)
    path_router = os.path.join(raiz, "app", "backend", "routers", "acoplamentos.py")
    with open(path_router, 'r', encoding='utf-8') as f:
        c = f.read()

    # Forçar a salvar as datas no POST
    if '"data_inicio": body.data_inicio' not in c:
        c = c.replace(
            '"created_by": user["nome"],',
            '"created_by": user["nome"],\n        "data_inicio": body.data_inicio,\n        "data_fim": body.data_fim,'
        )
    
    # Corrigir o GET para preencher a data com created_at se estiver vazia (registros antigos)
    if 'd["data_inicio"] = d.get("created_at", "").split("T")[0]' not in c:
        c = re.sub(
            r'async def listar\(_u: dict = Depends\(require\("read"\)\)\):\n    docs = await db\.acoplamentos\.find\(\{"status": "ativo"\}, \{"_id": 0\}\)\.sort\("created_at", -1\)\.to_list\(1000\)\n    return \[Acoplamento\(\*\*d\) for d in docs\]',
            '''async def listar(_u: dict = Depends(require("read"))):
    docs = await db.acoplamentos.find({"status": "ativo"}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for d in docs:
        if not d.get("data_inicio"):
            d["data_inicio"] = d.get("created_at", "").split("T")[0]
    return [Acoplamento(**d) for d in docs]''',
            c
        )

    with open(path_router, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Router atualizado (salva datas e corrige registros antigos).")

def fix_frontend(raiz):
    path_front = os.path.join(raiz, "frontend", "src", "pages", "Acoplamentos.tsx")
    with open(path_front, 'r', encoding='utf-8') as f:
        c = f.read()

    # Apenas garantir que a data está no form e sendo enviada
    if 'data_inicio: ""' not in c and 'data_inicio: new Date()' not in c:
        c = c.replace(
            'const [form, setForm] = useState({ veiculo_id: "", carreta_id: "", motorista_id: "", data_inicio: "", data_fim: "" });',
            'const [form, setForm] = useState({ veiculo_id: "", carreta_id: "", motorista_id: "", data_inicio: new Date().toISOString().split("T")[0], data_fim: "" });'
        )

    with open(path_front, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend verificado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push para atualizar o Backend.")