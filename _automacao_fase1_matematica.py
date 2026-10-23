import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"backup_fase1_math_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta = os.path.join(raiz, "app", "backend")
        for root, dirs, files in os.walk(pasta):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'backups']]
            for file in files:
                c = os.path.join(root, file)
                r = os.path.relpath(c, raiz)
                try: zipf.write(c, r)
                except: pass
    print("📦 Backup criado.")

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontra a função de importar (independente de nome exato)
    padrao = re.compile(r'(@router\.post\("/importar"\)[\s\S]*?)(?=@router|$)', re.DOTALL)
    
    if not padrao.search(conteudo):
        print("❌ Rota de importar não encontrada.")
        return

    # A nova função com a matemática correta (dividindo litros por 1000, preço por 100, calculando km_rodados)
    nova_funcao = '''@router.post("/importar")
async def importar_abastecimento(payload: dict, user: dict = Depends(require("write"))):
    placa = payload.get("placa")
    if not placa:
        raise HTTPException(status_code=400, detail="Placa não informada.")
        
    veiculo = await db.veiculos.find_one({"placa": placa})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {placa} não encontrado.")

    # 1. Correção dos valores da planilha (Litros vem em milésimos, Preço em centavos)
    litros_corrigidos = (payload.get("litros") or 0) / 1000
    preco_corrigido = (payload.get("preco_litro") or 0) / 100
    
    # Se o valor de PDF vier em reais, não divide (fallback simples)
    if litros_corrigidos == 0 and payload.get("litros", 0) > 0:
        litros_corrigidos = payload.get("litros")
    if preco_corrigido == 0 and payload.get("preco_litro", 0) > 0:
        preco_corrigido = payload.get("preco_litro")

    # 2. Cálculo do KM Rodados (Hodômetro Atual - Anterior)
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

    # 3. Valor Total
    valor_total = litros_corrigidos * preco_corrigido

    # 4. Monta o documento
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
    conteudo = padrao.sub(nova_funcao, conteudo)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Função de importação corrigida (matemática ajustada).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    corrigir(raiz)
    print("\n🚀 Faça o commit e push para o Render.")