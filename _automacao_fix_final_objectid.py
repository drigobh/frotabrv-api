import os

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Encontra a função importar_pdf
    inicio_func = -1
    for i, linha in enumerate(linhas):
        if "async def importar_pdf" in linha:
            inicio_func = i
            break

    if inicio_func == -1:
        print("❌ Função importar_pdf não encontrada.")
        return

    # Encontra o final da função (próximo @router)
    fim_func = -1
    for i in range(inicio_func + 1, len(linhas)):
        if linhas[i].strip().startswith("@router"):
            fim_func = i
            break

    if fim_func == -1:
        fim_func = len(linhas)

    # Nova função com TODAS as buscas usando {"_id": 0}
    nova_funcao = '''async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    placa_limpa = body.get("placa", "").strip().upper()
    
    # BUSCA 1: Veículo (com projeção _id: 0)
    veiculo = await db.veiculos.find_one({"placa": placa_limpa}, {"_id": 0})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {placa_limpa} não encontrado.")

    # CORREÇÃO MATEMÁTICA: Litros em milésimos (805000 -> 805.0), Preço em centavos (669 -> 6.69)
    litros_corrigidos = (body.get("litros") or 0) / 1000
    preco_corrigido = (body.get("preco_litro") or 0) / 100
    
    # Fallback para PDF (que pode vir em reais)
    if litros_corrigidos == 0 and body.get("litros", 0) > 0:
        litros_corrigidos = body.get("litros")
    if preco_corrigido == 0 and body.get("preco_litro", 0) > 0:
        preco_corrigido = body.get("preco_litro")

    # BUSCA 2: Último abastecimento (com projeção _id: 0)
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": body.get("data")}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and body.get("km"):
        km_rodados = body.get("km") - ultimo["km"]
        if km_rodados > 0 and litros_corrigidos > 0:
            media_km_l = km_rodados / litros_corrigidos
        else:
            km_rodados = None

    valor_total = litros_corrigidos * preco_corrigido

    doc = {
        "id": str(uuid.uuid4()),
        "data": body.get("data"),
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": None,
        "motorista_label": None,
        "litros": litros_corrigidos,
        "preco_litro": preco_corrigido,
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
        "created_at": now_iso()
    }

    await db.abastecimentos.insert_one(doc)
    return doc

'''

    novas_linhas = linhas[:inicio_func] + [nova_funcao] + linhas[fim_func:]
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    print("✅ Função importar_pdf corrigida! Todas as buscas usam {_id: 0} agora.")

if __name__ == "__main__":
    corrigir(os.getcwd())