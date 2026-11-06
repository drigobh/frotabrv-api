import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "financeiro.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Adiciona os campos fornecedor_id, veiculo_id e documento_vinculo na criação da conta
nova_rota = '''
@router.post("/contas")
async def criar_conta(body: dict, _u: dict = Depends(require("write"))):
    novo = {
        "id": str(uuid.uuid4()),
        "tipo": body.get("tipo", "Pagar"),
        "descricao": body.get("descricao", ""),
        "categoria": body.get("categoria", "Outros"),
        "valor": float(body.get("valor", 0)),
        "vencimento": body.get("vencimento"),
        "status": body.get("status", "Pendente"),
        "fornecedor_id": body.get("fornecedor_id"),
        "veiculo_id": body.get("veiculo_id"),
        "documento_vinculo": body.get("documento_vinculo", ""),
        "observacoes": body.get("observacoes", ""),
        "created_at": datetime.now().isoformat()
    }
    await db.contas.insert_one(novo)
    novo.pop("_id", None)
    return novo
'''

padrao = r'@router\.post\("/contas"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao, c):
    c = re.sub(padrao, nova_rota.strip() + "\n\n", c)
    with open(path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Backend: Rota de contas atualizada com vínculos (fornecedor, veículo, documento).")
else:
    print("⚠️ Rota /contas não encontrada.")