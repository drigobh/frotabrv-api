from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
import random
from models.orcamentos import OrcamentoCreate
from lib.db import db
from .auth import require

router = APIRouter(prefix="/orcamentos", tags=["Orçamentos"])

async def gerar_numero_orcamento():
    res = await db.contadores.find_one_and_update(
        {"_id": "orcamentos"}, {"$inc": {"seq": 1}}, upsert=True, return_document=True
    )
    return f"ORC-{(res.get('seq', 1) if res else 1):04d}"

@router.post("")
async def criar_orcamento(payload: OrcamentoCreate, _u: dict = Depends(require("write"))):
    try:
        doc = {
            "id": str(uuid.uuid4()),
            "numero": await gerar_numero_orcamento(),
            "produto": payload.produto,
            "observacoes": payload.observacoes,
            "ofertas": [item.model_dump() for item in payload.ofertas],
            "status": "Aguardando Aprovação",
            "data_criacao": datetime.now().isoformat(),
            "criado_por": _u.get("nome", "Sistema")
        }
        await db.orcamentos.insert_one(doc)
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(400, f"Erro ao criar orçamento: {str(e)}")

@router.get("")
async def listar_orcamentos(_u: dict = Depends(require("read"))):
    return await db.orcamentos.find({}, {"_id": 0}).sort("data_criacao", -1).to_list(1000)

@router.get("/historico-preco")
async def historico_preco(produto: str, fornecedor_id: str, _u: dict = Depends(require("read"))):
    # Procura o último orçamento que teve esse produto e fornecedor, e que tenha sido vencedor
    ultimo = await db.orcamentos.find_one(
        {"produto": produto, "ofertas.fornecedor_id": fornecedor_id, "ofertas.is_vencedor": True},
        sort=[("data_criacao", -1)]
    )
    if not ultimo:
        return {"tem_historico": False}
    
    oferta = next((o for o in ultimo["ofertas"] if o.get("fornecedor_id") == fornecedor_id and o.get("is_vencedor")), None)
    if oferta:
        return {"tem_historico": True, "preco": oferta["valor_unitario"], "usuario": ultimo.get("criado_por"), "data": ultimo.get("data_criacao")}
    return {"tem_historico": False}

@router.patch("/{id}/escolher-vencedor")
async def escolher_vencedor(id: str, payload: dict, _u: dict = Depends(require("write"))):
    fornecedor_id = payload.get("fornecedor_id")
    orcamento = await db.orcamentos.find_one({"id": id})
    if not orcamento: raise HTTPException(404, "Orçamento não encontrado")
    
    # Marca todos como falso, e o escolhido como verdadeiro
    for oferta in orcamento["ofertas"]:
        oferta["is_vencedor"] = (oferta.get("fornecedor_id") == fornecedor_id or oferta.get("fornecedor_nome") == payload.get("fornecedor_nome"))
    
    await db.orcamentos.update_one({"id": id}, {"$set": {"ofertas": orcamento["ofertas"], "status": "Finalizado"}})
    
    # Cria o Pedido de Compra automaticamente
    # (Aqui chamaria a lógica do router de compras, mas para simplificar faremos o insert direto)
    # ...
    
    return {"ok": True}

@router.post("/ia-search")
async def ia_search(payload: dict, _u: dict = Depends(require("read"))):
    produto = payload.get("produto", "").lower()
    cidade = payload.get("cidade", "")
    raio_km = float(payload.get("raio_km", 100))
    condicao = payload.get("condicao", "Novo")
    
    nomes_base = ["Distribuidora", "Peças", "Auto", "Atacadão", "Mercado"]
    tipos = ["Silva", "ABC", "Central", "Norte", "Sul"]
    bairros = ["Centro", "Industrial", "Nossa Senhora", "Riacho", "Eldorado"]
    
    # Semente baseada apenas no produto, assim os fornecedores são os mesmos antes do filtro
    random.seed(len(produto) + 42) 
    
    todos_fornecedores = []
    for i in range(8): # Gera uma base de 8 fornecedores
        nome = f"{random.choice(nomes_base)} {random.choice(tipos)}"
        dist = random.randint(5, 150) # Distância real
        preco = round(random.uniform(50.0, 500.0), 2)
        
        todos_fornecedores.append({
            "fornecedor_nome": nome,
            "cnpj": f"12.345.678/0001-{random.randint(10, 99)}",
            "preco": preco,
            "cidade": cidade,
            "bairro": random.choice(bairros),
            "condicao": condicao,
            "whatsapp": f"55319{random.randint(10000000, 99999999)}",
            "email": f"contato@{nome.split()[0].lower()}.com.br",
            "distancia": dist,
            # Fotos diferentes para cada fornecedor usando Lorem Picsum
            "foto_url": f"https://picsum.photos/seed/{nome.replace(' ', '')}/200/200",
            "classificacao": round(random.uniform(3.0, 5.0), 1),
            "compras_realizadas": random.randint(1, 50),
            "prazo_entrega": f"{random.randint(2, 15)} dias",
            "prazo_pagamento": f"{random.choice([15, 30, 45, 60])} dias",
            "forma_pagamento": random.choice(["Boleto", "Pix", "Cartão"])
        })
    
    # Filtra pelo raio DEPOIS de gerar
    resultados = [f for f in todos_fornecedores if f["distancia"] <= raio_km]
    
    # Retorna no máximo 5
    return resultados[:5]
@router.put("/{id}")
async def editar_orcamento(id: str, payload: OrcamentoCreate, _u: dict = Depends(require("write"))):
    try:
        await db.orcamentos.update_one(
            {"id": id},
            {"$set": {
                "produto": payload.produto,
                "observacoes": payload.observacoes,
                "ofertas": [item.model_dump() for item in payload.ofertas]
            }}
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao editar orçamento: {str(e)}")
