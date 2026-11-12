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

@router.delete("/{id}")
async def excluir_orcamento(id: str, _u: dict = Depends(require("write"))):
    try:
        await db.orcamentos.delete_one({"id": id})
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao excluir orçamento: {str(e)}")

@router.put("/{id}")
async def editar_orcamento(id: str, payload: OrcamentoCreate, _u: dict = Depends(require("write"))):
    try:
        # Limpa duplicatas do payload antes de salvar
        vistos = set()
        ofertas_limpas = []
        for item in payload.ofertas:
            chave = item.fornecedor_nome
            if chave not in vistos:
                vistos.add(chave)
                ofertas_limpas.append(item.model_dump())
        
        resultado = await db.orcamentos.update_one(
            {"id": id},
            {"$set": {
                "produto": payload.produto,
                "observacoes": payload.observacoes,
                "ofertas": ofertas_limpas
            }}
        )
        if resultado.matched_count == 0:
            raise HTTPException(404, "Orçamento não encontrado")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao editar orçamento: {str(e)}")
@router.patch("/{id}/escolher-vencedor")
async def escolher_vencedor(id: str, payload: dict, _u: dict = Depends(require("write"))):
    try:
        fornecedor_id = payload.get("fornecedor_id")
        fornecedor_nome = payload.get("fornecedor_nome")
        
        orcamento = await db.orcamentos.find_one({"id": id})
        if not orcamento:
            raise HTTPException(404, "Orçamento não encontrado")
        
        for oferta in orcamento["ofertas"]:
            oferta["is_vencedor"] = (oferta.get("fornecedor_id") == fornecedor_id or oferta.get("fornecedor_nome") == fornecedor_nome)
        
        await db.orcamentos.update_one(
            {"id": id}, 
            {"$set": {"ofertas": orcamento["ofertas"], "status": "Finalizado"}}
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao escolher vencedor: {str(e)}")

@router.get("/historico-preco")
async def historico_preco(produto: str, fornecedor_id: str, _u: dict = Depends(require("read"))):
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

@router.post("/ia-search")
async def ia_search(payload: dict, _u: dict = Depends(require("read"))):
    produto = payload.get("produto", "").lower()
    cidade = payload.get("cidade", "Contagem")
    raio_km = float(payload.get("raio_km", 100))
    condicao = payload.get("condicao", "Novo")
    
    # Listas fixas para gerar nomes únicos
    nomes = ["Auto Peças Silva", "Distribuidora ABC", "Atacadão Central", "Mercado Livre Auto", "Peças Já", "Oficina do Zé"]
    bairros = ["Centro", "Industrial", "Nossa Senhora", "Riacho", "Eldorado"]
    
    resultados = []
    for i, nome in enumerate(nomes):
        dist = 10 + (i * 15) # Distâncias diferentes (10km, 25km, 40km...)
        if dist <= raio_km:
            resultados.append({
                "fornecedor_nome": nome,
                "cnpj": f"12.345.678/0001-{10+i}",
                "preco": 150.0 + (i * 50.0), # Preços diferentes
                "cidade": cidade,
                "bairro": bairros[i % len(bairros)],
                "condicao": condicao,
                "whatsapp": "5531999999999", # Número de teste válido
                "email": f"contato@fornecedor{i}.com.br",
                "distancia": dist,
                "foto_url": "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=150&h=150&fit=crop", # Foto real
                "classificacao": 4.5,
                "compras_realizadas": 12,
                "prazo_entrega": "5 dias",
                "prazo_pagamento": "30 dias",
                "forma_pagamento": "Boleto"
            })
    return resultados
