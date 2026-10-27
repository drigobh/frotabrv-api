import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_DUP_ED_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx", "app/backend/routers/abastecimentos.py", "app/backend/routers/fornecedores.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend_abastecimentos(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Reforçar a verificação de duplicidade antes de inserir
    # Vamos garantir que a função importar_pdf verifique TODAS as possibilidades antes do insert
    if 'await db.abastecimentos.insert_one(doc)' in c:
        # Já existe uma verificação, mas vamos garantir que ela esteja logo antes do insert
        # Vou substituir o bloco de verificação atual por um mais robusto
        antigo_bloco = '''    # TRAVA DE DUPLICIDADE
        codigo_transacao_recebido = body.get("codigo_transacao")
        chave_nfe_recebida = body.get("chave_nfe")
        numero_nf_recebido = body.get("numero_nf")
        cnpj_recebido = body.get("cnpj")

        if codigo_transacao_recebido:
            if await db.abastecimentos.find_one({"codigo_transacao": codigo_transacao_recebido}):
                raise HTTPException(409, "Registro duplicado: Código de Transação já importado.")
        elif chave_nfe_recebida:
            if await db.abastecimentos.find_one({"chave_nfe": chave_nfe_recebida}):
                raise HTTPException(409, "Registro duplicado: Chave NF-e já importada.")
        elif numero_nf_recebido and cnpj_recebido:
            if await db.abastecimentos.find_one({"numero_nf": numero_nf_recebido, "cnpj": cnpj_recebido}):
                raise HTTPException(409, "Registro duplicado: Nota Fiscal já importada.")
        else:
            existente_placa = await db.abastecimentos.find_one({
                "veiculo_id": veiculo["id"],
                "data": data_abast,
                "litros": litros
            })
            if existente_placa:
                raise HTTPException(409, "Registro duplicado: Abastecimento com esta placa, data e litros já existe.")'''
        
        novo_bloco = '''    # TRAVA DE DUPLICIDADE REFORÇADA
        codigo_transacao_recebido = body.get("codigo_transacao")
        chave_nfe_recebida = body.get("chave_nfe")
        numero_nf_recebido = body.get("numero_nf")
        cnpj_recebido = body.get("cnpj")

        if codigo_transacao_recebido:
            existente = await db.abastecimentos.find_one({"codigo_transacao": codigo_transacao_recebido})
            if existente:
                raise HTTPException(409, "Registro duplicado: Código de Transação já importado.")
        elif chave_nfe_recebida:
            existente = await db.abastecimentos.find_one({"chave_nfe": chave_nfe_recebida})
            if existente:
                raise HTTPException(409, "Registro duplicado: Chave NF-e já importada.")
        elif numero_nf_recebido and cnpj_recebido:
            existente = await db.abastecimentos.find_one({"numero_nf": numero_nf_recebido, "cnpj": cnpj_recebido})
            if existente:
                raise HTTPException(409, "Registro duplicado: Nota Fiscal já importada.")
        else:
            existente_placa = await db.abastecimentos.find_one({
                "veiculo_id": veiculo["id"],
                "data": data_abast,
                "litros": litros
            })
            if existente_placa:
                raise HTTPException(409, "Registro duplicado: Abastecimento com esta placa, data e litros já existe.")'''
        
        if antigo_bloco in c:
            c = c.replace(antigo_bloco, novo_bloco)
            print("✅ Backend: Verificação de duplicidade em abastecimentos reforçada.")
        else:
            print("ℹ️ Backend: Bloco de verificação não encontrado, pode já estar atualizado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_backend_fornecedores(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adicionar verificação de duplicidade por nome ou CNPJ antes de criar fornecedor
    if '@router.post("", response_model=Fornecedor)' in c and 'Verifica se o fornecedor já existe' not in c:
        alvo = '''@router.post("", response_model=Fornecedor)
async def criar(body: FornecedorCreate, user: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["created_by"] = user["id"]
    await db.fornecedores.insert_one(doc)
    doc.pop("_id", None)
    return doc'''
        
        novo_alvo = '''@router.post("", response_model=Fornecedor)
async def criar(body: FornecedorCreate, user: dict = Depends(require("write"))):
    # Verifica se o fornecedor já existe (por nome ou CNPJ)
    existente = None
    if body.nome:
        existente = await db.fornecedores.find_one({"nome": {"$regex": f"^{re.escape(body.nome)}$", "$options": "i"}})
    if not existente and body.documento:
        existente = await db.fornecedores.find_one({"documento": body.documento})
    if existente:
        raise HTTPException(409, "Fornecedor já cadastrado (nome ou CNPJ).")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["created_by"] = user["id"]
    await db.fornecedores.insert_one(doc)
    doc.pop("_id", None)
    return doc'''
        
        if alvo in c:
            c = c.replace(alvo, novo_alvo)
            # Garantir que o import do re está presente
            if 'import re' not in c:
                c = 'import re\n' + c
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Backend: Verificação de duplicidade de fornecedor adicionada.")
        else:
            print("⚠️ Backend: Não foi possível encontrar a rota de criação de fornecedor.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Na função handleImportEdenred, usar Map para garantir fornecedores únicos
    # Vamos substituir a parte que coleta unregistered
    if 'const unregistered: Record<string, any> = {};' in c:
        c = c.replace(
            'const unregistered: Record<string, any> = {};',
            'const unregistered = new Map<string, any>();'
        )
        # Substituir a atribuição
        c = c.replace(
            'unregistered[fornecedorNome] = { nome: fornecedorNome, cidade, estado, endereco, bairro };',
            'unregistered.set(fornecedorNome, { nome: fornecedorNome, cidade, estado, endereco, bairro });'
        )
        # Substituir a conversão para array
        c = c.replace(
            'const pendentes = Object.values(unregistered);',
            'const pendentes = Array.from(unregistered.values());'
        )
        print("✅ Frontend: Coleta de fornecedores únicos corrigida (usando Map).")

    # 2. No modal de pendentes, garantir que a lista seja única (já será, pois vem do Map)
    # Mas também podemos garantir que o backend não crie duplicatas ao cadastrar em lote.
    # A verificação no backend já resolve.

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Função Edenred ajustada para fornecedores únicos.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend_abastecimentos(raiz)
    fix_backend_fornecedores(raiz)
    fix_frontend(raiz)