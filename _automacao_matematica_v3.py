import os

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Encontra a linha onde começa a função importar_abastecimento
    inicio_func = -1
    for i, linha in enumerate(linhas):
        if "async def importar_abastecimento" in linha:
            inicio_func = i
            break

    if inicio_func == -1:
        print("❌ Função importar_abastecimento não encontrada.")
        return

    # Encontra o final da função (o próximo @router)
    fim_func = -1
    for i in range(inicio_func + 1, len(linhas)):
        if linhas[i].strip().startswith("@router"):
            fim_func = i
            break

    if fim_func == -1:
        fim_func = len(linhas)

    # Nova função (mantendo o cabeçalho original e substituindo o corpo)
    nova_funcao = '''async def importar_abastecimento(payload: dict, user: dict = Depends(require("write"))):
    placa = payload.get("placa")
    if not placa:
        raise HTTPException(status_code=400, detail="Placa não informada.")
        
    veiculo = await db.veiculos.find_one({"placa": placa})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {placa} não encontrado.")

    # CORREÇÃO: Litros vêm em milésimos (ex: 805000 = 805L), Preço em centavos (ex: 669 = R$ 6,69)
    litros_corrigidos = (payload.get("litros") or 0) / 1000
    preco_corrigido = (payload.get("preco_litro") or 0) / 100
    
    # Fallback para PDF (que pode vir em reais)
    if litros_corrigidos == 0 and payload.get("litros", 0) > 0:
        litros_corrigidos = payload.get("litros")
    if preco_corrigido == 0 and payload.get("preco_litro", 0) > 0:
        preco_corrigido = payload.get("preco_litro")

    # Cálculo do KM Rodados
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": payload.get("data")}},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and payload.get("km"):
        km_rodados = payload.get("km") - ultimo["km"]
        if km_rodados > 0 and litros_corrigidos > 0:
            media_km_l = km_rodados / litros_corrigidos
        else:
            km_rodados = None

    valor_total = litros_corrigidos * preco_corrigido

    doc = {
        "id": str(uuid.uuid4()),
        "data": payload.get("data"),
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": None,
        "motorista_label": None,
        "litros": litros_corrigidos,
        "preco_litro": preco_corrigido,
        "valor_total": valor_total,
        "posto": payload.get("fornecedor") or "Importado",
        "km": payload.get("km"),
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": "pdf",
        "numero_nf": payload.get("numero_nf"),
        "chave_nfe": payload.get("chave_nfe"),
        "hora": payload.get("hora"),
        "cnpj": payload.get("cnpj"),
        "fornecedor": payload.get("fornecedor"),
        "created_at": now_iso()
    }

    await db.abastecimentos.insert_one(doc)
    return doc

'''

    # Substitui apenas o corpo da função (mantendo o decorador original)
    novas_linhas = linhas[:inicio_func] + [nova_funcao] + linhas[fim_func:]
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    print("✅ Função de importação corrigida com sucesso!")

if __name__ == "__main__":
    corrigir(os.getcwd())