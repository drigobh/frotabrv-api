from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import uuid
from models.compras import PedidoCompraCreate, AprovacaoPayload
from lib.db import db
from .auth import require

router = APIRouter(prefix="/compras", tags=["Compras"])

async def gerar_numero_pedido():
    res = await db.contadores.find_one_and_update(
        {"_id": "compras"},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True
    )
    seq = res.get("seq", 1) if res else 1
    return f"OC-{seq:04d}"

@router.post("")
async def criar_pedido(payload: PedidoCompraCreate, _u: dict = Depends(require("write"))):
    try:
        doc = {
            "id": str(uuid.uuid4()),
            "numero": await gerar_numero_pedido(),
            "fornecedor_id": payload.fornecedor_id,
            "veiculo_id": payload.veiculo_id,
            "itens": [item.model_dump() for item in payload.itens],
            "observacoes": payload.observacoes,
            "valor_total": payload.valor_total,
            "status": "Pendente",  # Pendente, Aprovado, Reprovado, Comprado
            "data_criacao": datetime.now().isoformat(),
            "criado_por": _u.get("nome", "Sistema")
        }
        await db.compras.insert_one(doc)
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(400, f"Erro ao criar pedido: {str(e)}")

@router.get("")
async def listar_pedidos(status: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if status:
        filtro["status"] = status
    return await db.compras.find(filtro, {"_id": 0}).sort("data_criacao", -1).to_list(1000)

@router.patch("/{id}/aprovar")
async def aprovar_pedido(id: str, payload: AprovacaoPayload, _u: dict = Depends(require("write"))):
    pedido = await db.compras.find_one({"id": id})
    if not pedido:
        raise HTTPException(404, "Pedido não encontrado")
    
    if payload.status not in ["Aprovado", "Reprovado"]:
        raise HTTPException(400, "Status inválido")

    await db.compras.update_one(
        {"id": id},
        {"$set": {
            "status": payload.status,
            "aprovado_por": _u.get("nome", "Sistema"),
            "data_aprovacao": datetime.now().isoformat(),
            "motivo_reprovacao": payload.motivo
        }}
    )
    return {"ok": True}

@router.delete("/{id}")
async def excluir_pedido(id: str, _u: dict = Depends(require("write"))):
    await db.compras.delete_one({"id": id})
    return {"ok": True}


@router.get("/alcada")
async def verificar_alcada(_u: dict = Depends(require("read"))):
    """Retorna a alçada do usuário logado para aprovação de compras."""
    # Puxa os dados frescos do usuário no banco
    user = await db.usuarios.find_one({"id": _u["id"]}, {"_id": 0})
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    
    return {
        "pode_aprovar": user.get("pode_aprovar_compras", False),
        "alcada": user.get("alcada_aprovacao", 0.0),
        "nome": user.get("nome", "")
    }


@router.get("/usuarios")
async def listar_usuarios_compras(_u: dict = Depends(require("read"))):
    """Lista todos os usuários com suas permissões e alçadas de compras."""
    usuarios = await db.usuarios.find({}, {"_id": 0, "senha": 0}).to_list(1000)
    return usuarios

@router.put("/usuarios/{id}")
async def atualizar_permissoes_compras(id: str, payload: dict, _u: dict = Depends(require("write"))):
    """Atualiza as permissões de compras de um usuário e registra o histórico."""
    try:
        user_antigo = await db.usuarios.find_one({"id": id})
        if not user_antigo:
            raise HTTPException(404, "Usuário não encontrado")
        
        # Pega os valores antigos
        antigos = {
            "pode_comprar": user_antigo.get("pode_comprar", False),
            "limite_compra": user_antigo.get("limite_compra", 0),
            "pode_aprovar_compras": user_antigo.get("pode_aprovar_compras", False),
            "limite_aprovacao": user_antigo.get("limite_aprovacao", 0)
        }
        
        novos = {
            "pode_comprar": payload.get("pode_comprar", False),
            "limite_compra": float(payload.get("limite_compra", 0)),
            "pode_aprovar_compras": payload.get("pode_aprovar_compras", False),
            "limite_aprovacao": float(payload.get("limite_aprovacao", 0))
        }
        
        # Cria o registro de histórico
        mudancas = []
        if antigos["pode_comprar"] != novos["pode_comprar"]:
            mudancas.append(f"Comprador: {antigos['pode_comprar']} -> {novos['pode_comprar']}")
        if antigos["limite_compra"] != novos["limite_compra"]:
            mudancas.append(f"Limite de Compra: R$ {antigos['limite_compra']} -> R$ {novos['limite_compra']}")
        if antigos["pode_aprovar_compras"] != novos["pode_aprovar_compras"]:
            mudancas.append(f"Aprovador: {antigos['pode_aprovar_compras']} -> {novos['pode_aprovar_compras']}")
        if antigos["limite_aprovacao"] != novos["limite_aprovacao"]:
            mudancas.append(f"Limite de Aprovação: R$ {antigos['limite_aprovacao']} -> R$ {novos['limite_aprovacao']}")

        if mudancas:
            await db.historico_compras.insert_one({
                "usuario_id": id,
                "usuario_nome": user_antigo.get("nome", "Desconhecido"),
                "alterado_por": _u.get("nome", "Sistema"),
                "data": __import__("datetime").datetime.now().isoformat(),
                "mudancas": mudancas
            })
        
        await db.usuarios.update_one({"id": id}, {"$set": novos})
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, f"Erro ao atualizar permissões: {str(e)}")

@router.get("/historico/{id}")
async def obter_historico_compras(id: str, _u: dict = Depends(require("read"))):
    """Retorna o histórico de alterações de compras de um usuário."""
    return await db.historico_compras.find({"usuario_id": id}, {"_id": 0}).sort("data", -1).to_list(100)
