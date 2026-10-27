import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FINAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx", "app/backend/routers/abastecimentos.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui a função importar_pdf inteira para garantir que não há erros de sintaxe e adicionar a trava
    padrao = re.compile(r'@router\.post\("/importar"[\s\S]*?(?=@router\.|$)', re.DOTALL)
    
    nova_funcao = '''@router.post("/importar", response_model=None, status_code=201)
async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    placa_limpa = body.get("placa", "").strip().upper()
    
    veiculo = await db.veiculos.find_one({"placa": placa_limpa}, {"_id": 0})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {placa_limpa} não encontrado.")

    litros = body.get("litros") or 0
    preco_litro = body.get("preco_litro") or 0
    data_recebida = body.get("data")
    km_atual = body.get("km") or 0
    produto = body.get("produto", "DIESEL").upper()

    try:
        if "/" in data_recebida:
            data_abast = datetime.strptime(data_recebida, "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            data_abast = data_recebida
    except:
        data_abast = data_recebida

    # TRAVA DE SEGURANÇA: BLOQUEIO DE DUPLICIDADE
    codigo_transacao_recebido = body.get("codigo_transacao")
    chave_nfe_recebida = body.get("chave_nfe")
    numero_nf_recebido = body.get("numero_nf")
    
    if codigo_transacao_recebido:
        if await db.abastecimentos.find_one({"codigo_transacao": codigo_transacao_recebido}):
            raise HTTPException(409, "Registro duplicado: Código de Transação já importado.")
    elif chave_nfe_recebida:
        if await db.abastecimentos.find_one({"chave_nfe": chave_nfe_recebida}):
            raise HTTPException(409, "Registro duplicado: Chave NF-e já importada.")
    elif numero_nf_recebido and body.get("cnpj"):
        if await db.abastecimentos.find_one({"numero_nf": numero_nf_recebido, "cnpj": body.get("cnpj")}):
            raise HTTPException(409, "Registro duplicado: Nota Fiscal já importada.")
    else:
        # Para BSOFT (sem código/nf), checa placa, data e litros
        existente_placa = await db.abastecimentos.find_one({
            "veiculo_id": veiculo["id"],
            "data": data_abast,
            "litros": float(litros)
        })
        if existente_placa:
            raise HTTPException(409, "Registro duplicado: Abastecimento com esta placa, data e litros já existe.")

    # Resto da lógica original
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    if body.get("origem") == "excel" and body.get("km_rodados") is not None:
        km_rodados = body.get("km_rodados")
        media_km_l = body.get("media_km_l")
    else:
        km_rodados, media_km_l = calcular_km(km_atual, litros, produto, ultimo, veiculo)

    try:
        valor_total = float(body.get("valor_total") or 0)
    except:
        valor_total = 0
        
    if valor_total == 0:
        valor_total = float(litros) * float(preco_litro)
    valor_total = round(valor_total, 2)

    acoplamento = await db.acoplamentos.find_one(
        {"veiculo_id": veiculo["id"]},
        {"_id": 0},
        sort=[("created_at", -1)]
    )
        
    motorista_id = acoplamento.get("motorista_id") if acoplamento else None
    motorista_label = None
    if motorista_id:
        mot = await db.motoristas.find_one({"id": motorista_id}, {"_id": 0})
        motorista_label = mot["nome"] if mot else None

    doc = {
        "id": str(uuid.uuid4()),
        "data": data_abast,
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": motorista_id,
        "motorista_label": motorista_label,
        "litros": litros,
        "preco_litro": preco_litro,
        "valor_total": valor_total,
        "posto": body.get("fornecedor") or "Importado",
        "km": km_atual,
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": body.get("origem", "excel"),
        "produto": produto,
        "numero_nf": body.get("numero_nf"),
        "chave_nfe": body.get("chave_nfe"),
        "codigo_transacao": body.get("codigo_transacao"),
        "hora": body.get("hora"),
        "cnpj": body.get("cnpj"),
        "cidade": body.get("cidade"),
        "estado": body.get("estado"),
        "fornecedor": body.get("fornecedor"),
        "created_by": user.get("id", "sistema"),
        "created_by_name": user.get("nome", user.get("email", "Sistema")),
        "created_at": now_iso()
    }

    await db.abastecimentos.insert_one(doc)
    if km_atual > 0:
        await db.veiculos.update_one({"id": veiculo["id"]}, {"$set": {"hodometro_km": km_atual}})
    doc.pop("_id", None)
    return doc
'''
    
    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota /importar reescrita com sucesso e proteção contra duplicidade.")
    else:
        print("⚠️ Não foi possível encontrar a rota /importar no Backend.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Forçar formatação da data no grid (DD/MM/YYYY)
    # Substitui qualquer chamada de formatação de data no TableCell por uma conversão manual string
    c = re.sub(
        r'\{dataBR\(r\.data\)\}|\{formatData\(r\.data\)\}',
        '{r.data ? r.data.split("T")[0].split("-").reverse().join("/") : "—"}',
        c
    )

    # 2. Atualizar o catch do BSOFT e EDENRED para avisar sobre duplicidade
    c = c.replace(
        'erros.push({ linha: i + 1, placa: placa, erro: err.message || "Erro" });',
        'erros.push({ linha: i + 1, placa: placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") });'
    )
    c = c.replace(
        'erros.push({ linha: i + 1, placa: payload.placa, erro: err.message || "Erro" });',
        'erros.push({ linha: i + 1, placa: payload.placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") });'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Formatação de data forçada para DD/MM/YYYY no grid.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)