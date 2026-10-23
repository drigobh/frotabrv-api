import os

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Encontra a função importar_pdf
    inicio = -1
    for i, linha in enumerate(linhas):
        if "async def importar_pdf" in linha:
            inicio = i
            break

    if inicio == -1:
        print("❌ Função importar_pdf não encontrada.")
        return

    fim = -1
    for i in range(inicio + 1, len(linhas)):
        if linhas[i].strip().startswith("@router"):
            fim = i
            break

    if fim == -1:
        fim = len(linhas)

    nova_funcao = '''async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    placa_limpa = body.get("placa", "").strip().upper()
    
    veiculo = await db.veiculos.find_one({"placa": placa_limpa}, {"_id": 0})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {placa_limpa} não encontrado.")

    # O Frontend já envia litros e preco_litro divididos corretamente.
    litros = body.get("litros") or 0
    preco_litro = body.get("preco_litro") or 0
    data_abast = body.get("data")

    # Busca o último abastecimento ANTES da data atual para calcular os KM rodados
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and body.get("km"):
        km_rodados = body.get("km") - ultimo["km"]
        if km_rodados > 0 and litros > 0:
            media_km_l = km_rodados / litros
        else:
            km_rodados = None

    valor_total = litros * preco_litro

    doc = {
        "id": str(uuid.uuid4()),
        "data": data_abast,
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": None,
        "motorista_label": None,
        "litros": litros,
        "preco_litro": preco_litro,
        "valor_total": valor_total,
        "posto": body.get("fornecedor") or "Importado",
        "km": body.get("km"),
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": "pdf",
        "numero_nf": body.get("numero_nf"),
        "chave_nfe": body.get("chave_nfe"),
        "hora": body.get("hora"),
        "cnpj": body.get("cnpj"),
        "fornecedor": body.get("fornecedor"),
        "created_by": user.get("id", "sistema"),
        "created_at": now_iso()
    }

    await db.abastecimentos.insert_one(doc)
    doc.pop("_id", None)
    return doc

'''

    novas_linhas = linhas[:inicio] + [nova_funcao] + linhas[fim:]
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    print("✅ Função importar_pdf corrigida para calcular KM Rodados e Média.")

if __name__ == "__main__":
    corrigir(os.getcwd())