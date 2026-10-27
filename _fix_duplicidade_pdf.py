import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DUP_PDF_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["app/backend/routers/abastecimentos.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Encontra a rota de criação manual (POST "")
    alvo = '''@router.post("", response_model=Abastecimento, status_code=201)
async def criar(body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")'''

    novo_alvo = '''@router.post("", response_model=Abastecimento, status_code=201)
async def criar(body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
        
    # TRAVA DE SEGURANÇA: Bloqueio de PDF Duplicado no Formulário
    if body.origem == "pdf":
        if body.chave_nfe:
            if await db.abastecimentos.find_one({"chave_nfe": body.chave_nfe}):
                raise HTTPException(409, "Esta Nota Fiscal (PDF) já foi importada no sistema.")
        elif body.numero_nf and body.cnpj:
            if await db.abastecimentos.find_one({"numero_nf": body.numero_nf, "cnpj": body.cnpj}):
                raise HTTPException(409, "Esta Nota Fiscal (PDF) já foi importada no sistema.")'''

    if alvo in c:
        c = c.replace(alvo, novo_alvo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Trava de duplicidade adicionada com sucesso na rota de criação (PDF).")
    else:
        print("⚠️ Não foi possível encontrar a rota de criação para aplicar a trava. O código pode estar diferente.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)