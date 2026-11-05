import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "pneu_movimentacoes.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Atualiza a rota POST principal para aceitar e salvar os novos campos do checklist
if "@router.post(\"\")" in c and "avaliacao_carcaca" not in c:
    novo_post = '''@router.post("")
async def criar_movimentacao(body: dict, _u: dict = Depends(require("write"))):
    # Salva todos os dados do checklist borracheiro no histórico
    doc = {
        "id": str(uuid.uuid4()),
        "pneu_id": body.get("pneu_id"),
        "tipo": body.get("tipo"),
        "motivo": body.get("motivo", ""),
        "borracheiro": body.get("borracheiro", ""),
        "avaliacao_carcaca": body.get("avaliacao_carcaca", "APROVADA"),
        "observacoes": body.get("observacoes", ""),
        "km_manutencao": body.get("km_manutencao", 0),
        "data_movimentacao": datetime.datetime.now().isoformat(),
        "usuario": _u.get("nome", "Sistema")
    }
    await db.pneu_movimentacoes.insert_one(doc)
    
    # Atualiza o status do pneu
    novo_status = "Recapagem" if body.get("tipo") == "RECAPAGEM" else ("Conserto" if body.get("tipo") == "CONSERTO" else "Sucateado")
    await db.pneus.update_one({"id": body.get("pneu_id")}, {"$set": {"status": novo_status}})
    
    doc.pop("_id", None)
    return doc
'''
    # Substitui a rota POST antiga pela nova
    c = re.sub(r'@router\.post\(""\)[\s\S]*?(?=@router\.)', lambda m: novo_post + "\n\n", c)
    
    # Garante imports
    if "import uuid" not in c:
        c = "import uuid\nimport datetime\n" + c

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Backend: Rota de movimentação atualizada para o Checklist.")
else:
    print("ℹ️ Backend já atualizado ou rota não encontrada.")