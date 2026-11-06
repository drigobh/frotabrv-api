import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "pneus.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Rota de Pareto (Motivos de Sucateamento)
rota_pareto = '''

@router.get("/relatorios/pareto")
async def relatorio_pareto(_u: dict = Depends(require("read"))):
    pipeline = [
        {"$match": {"status": "Sucateado"}},
        {"$group": {
            "_id": {"$ifNull": ["$motivo_descarte", "$observacoes", "Não Informado"]},
            "quantidade": {"$sum": 1}
        }},
        {"$sort": {"quantidade": -1}},
        {"$limit": 10}
    ]
    resultado = await db.pneus.aggregate(pipeline).to_list(100)
    # Formata para o frontend
    return [{"motivo": r["_id"] or "Sem Motivo", "quantidade": r["quantidade"]} for r in resultado]

@router.get("/qrcode/{codigo}")
async def buscar_pneu_qrcode(codigo: str, _u: dict = Depends(require("read"))):
    pneu = await db.pneus.find_one({"numero_fogo": codigo}, {"_id": 0})
    if not pneu:
        pneu = await db.pneus.find_one({"n_serie": codigo}, {"_id": 0})
    if not pneu:
        raise HTTPException(404, "Pneu não encontrado.")
    return pneu

@router.post("/qrcode/{codigo}/atualizar")
async def atualizar_pneu_qrcode(codigo: str, body: dict, _u: dict = Depends(require("write"))):
    update_data = {}
    if "profundidade_atual" in body: update_data["profundidade_atual"] = float(body["profundidade_atual"])
    if "posicao" in body: update_data["posicao"] = body["posicao"]
    if "veiculo_id" in body: update_data["veiculo_id"] = body["veiculo_id"]
    
    if not update_data:
        raise HTTPException(400, "Nenhum dado válido para atualizar.")

    await db.pneus.update_one({"numero_fogo": codigo}, {"$set": update_data})
    return {"status": "ok", "message": "Pneu atualizado via QR Code."}
'''

if "relatorios/pareto" not in c:
    c += rota_pareto
    if "HTTPException" not in c:
        c = "from fastapi import HTTPException\n" + c
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Backend: Rotas de Pareto e QR Code criadas.")

print("✅ Backend pronto! Faça o git push.")