import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "pneus.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Atualiza a rota de QR Code para salvar a não conformidade e criar um alerta
nova_rota = '''
@router.post("/qrcode/{codigo}/atualizar")
async def atualizar_pneu_qrcode(codigo: str, body: dict, _u: dict = Depends(require("write"))):
    from datetime import datetime
    import uuid
    
    update_data = {}
    if "profundidade_atual" in body: update_data["profundidade_atual"] = float(body["profundidade_atual"])
    
    if not update_data:
        raise HTTPException(400, "Nenhum dado válido para atualizar.")

    await db.pneus.update_one({"numero_fogo": codigo}, {"$set": update_data})
    
    # Se marcou não conformidade, gera alerta
    if body.get("nao_conformidade"):
        pneu = await db.pneus.find_one({"numero_fogo": codigo})
        alerta = {
            "id": str(uuid.uuid4()),
            "tipo": "Pneu",
            "severidade": "Crítico",
            "titulo": f"Pneu {codigo} em Não Conformidade",
            "detalhe": f"O pneu foi marcado como não pertencente ou fora de posição no veículo.",
            "data": datetime.now().isoformat(),
            "resolvido": False
        }
        await db.alertas.insert_one(alerta)
    
    return {"status": "ok", "message": "Pneu atualizado."}
'''

padrao = r'@router\.post\("/qrcode/\{codigo\}/atualizar"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao, c):
    c = re.sub(padrao, nova_rota.strip() + "\n\n", c)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Backend: Rota de QR Code atualizada para gerar alerta de não conformidade.")