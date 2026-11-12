from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
import random
from models.orcamentos import OrcamentoCreate
from lib.db import db
from .auth import require
from services.email_orcamento import gerar_html, enviar_email, gerar_texto_whatsapp, enviar_whatsapp

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
        raise HTTPException(400, f"Erro ao excluir: {str(e)}")

@router.put("/{id}")
async def editar_orcamento(id: str, payload: OrcamentoCreate, _u: dict = Depends(require("write"))):
    try:
        orc = await db.orcamentos.find_one({"id": id})
        if orc.get("status") == "Finalizado":
            raise HTTPException(400, "Não é possível editar um orçamento finalizado.")
            
        vistos = set()
        ofertas_limpas = []
        for item in payload.ofertas:
            chave = item.fornecedor_nome
            if chave not in vistos:
                vistos.add(chave)
                ofertas_limpas.append(item.model_dump())
        
        await db.orcamentos.update_one(
            {"id": id},
            {"$set": {
                "produto": payload.produto,
                "observacoes": payload.observacoes,
                "ofertas": ofertas_limpas
            }}
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao editar: {str(e)}")

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
            {"$set": {
                "ofertas": orcamento["ofertas"], 
                "status": "Finalizado",
                "aprovado_por": _u.get("nome", "Sistema"),
                "data_aprovacao": datetime.now().isoformat()
            }}
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao aprovar: {str(e)}")

@router.patch("/{id}/reprovar")
async def reprovar_orcamento(id: str, _u: dict = Depends(require("write"))):
    try:
        await db.orcamentos.update_one(
            {"id": id}, 
            {"$set": {
                "status": "Reprovado",
                "aprovado_por": _u.get("nome", "Sistema"),
                "data_aprovacao": datetime.now().isoformat()
            }}
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao reprovar: {str(e)}")

@router.post("/ia-search")
async def ia_search(payload: dict, _u: dict = Depends(require("read"))):
    produto = payload.get("produto", "").lower()
    cidade = payload.get("cidade", "Contagem")
    raio_km = float(payload.get("raio_km", 100))
    condicao = payload.get("condicao", "Novo")
    
    nomes = ["Auto Peças Silva", "Distribuidora ABC", "Atacadão Central", "Mercado Livre Auto", "Peças Já"]
    bairros = ["Centro", "Industrial", "Nossa Senhora", "Riacho", "Eldorado"]
    
    resultados = []
    for i, nome in enumerate(nomes):
        dist = 10 + (i * 15)
        if dist <= raio_km:
            resultados.append({
                "fornecedor_nome": nome,
                "cnpj": f"12.345.678/0001-{10+i}",
                "preco": 150.0 + (i * 50.0),
                "cidade": cidade,
                "bairro": bairros[i % len(bairros)],
                "condicao": condicao,
                "whatsapp": "5531999999999",
                "email": f"contato@fornecedor{i}.com.br",
                "distancia": dist,
                "foto_url": "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=150&h=150&fit=crop",
                "classificacao": 4.5,
                "compras_realizadas": 12,
                "prazo_entrega": "5 dias",
                "prazo_pagamento": "30 dias",
                "forma_pagamento": "Boleto"
            })
    return resultados


@router.post("/{id}/enviar")
async def enviar_orcamento(id: str, _u: dict = Depends(require("write"))):
    try:
        orcamento = await db.orcamentos.find_one({"id": id})
        if not orcamento:
            raise HTTPException(404, "Orçamento não encontrado")
        
        # 1. Buscar comprador
        comprador = await db.usuarios.find_one({"nome": orcamento.get("criado_por")}, {"_id": 0})
        
        # 2. Calcular valor total para encontrar aprovador compatível
        valor_total = sum((of.get("valor_unitario", 0) * of.get("quantidade", 0)) for of in orcamento.get("ofertas", []))
        
        aprovador_escolhido = None
        aprovadores = await db.usuarios.find({"pode_aprovar_compras": True}, {"_id": 0}).to_list(100)
        for ap in aprovadores:
            if ap.get("limite_aprovacao", 0) >= valor_total:
                if not aprovador_escolhido or ap.get("limite_aprovacao") < aprovador_escolhido.get("limite_aprovacao"):
                    aprovador_escolhido = ap
        
        if not aprovador_escolhido and aprovadores:
            aprovador_escolhido = aprovadores[0]
        
        links_whatsapp = []
        
        # 3. Enviar para comprador
        if comprador and comprador.get("email"):
            html_comp = gerar_html(orcamento, "comprador", comprador.get("nome", "Comprador"))
            enviar_email(comprador["email"], f"Orçamento {orcamento['numero']} criado com sucesso", html_comp)
            link = enviar_whatsapp(comprador.get("whatsapp", ""), gerar_texto_whatsapp(orcamento, "comprador", comprador.get("nome", "")))
            if link: links_whatsapp.append(link)
        
        # 4. Enviar para aprovador
        if aprovador_escolhido and aprovador_escolhido.get("email"):
            html_apr = gerar_html(orcamento, "aprovador", aprovador_escolhido.get("nome", "Aprovador"))
            enviar_email(aprovador_escolhido["email"], f"Ação Necessária: Aprovar Orçamento {orcamento['numero']}", html_apr)
            link = enviar_whatsapp(aprovador_escolhido.get("whatsapp", ""), gerar_texto_whatsapp(orcamento, "aprovador", aprovador_escolhido.get("nome", "")))
            if link: links_whatsapp.append(link)
        
        return {
            "ok": True,
            "comprador_notificado": bool(comprador and comprador.get("email")),
            "aprovador_notificado": bool(aprovador_escolhido and aprovador_escolhido.get("email")),
            "links_whatsapp": links_whatsapp
        }
    except Exception as e:
        raise HTTPException(400, f"Erro ao enviar notificações: {str(e)}")
