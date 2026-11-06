import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "financeiro.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Atualizar a rota de listar contas para aceitar filtro de mês/ano
nova_listar = '''
@router.get("/contas")
async def listar_contas(tipo: str = None, mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    if mes and ano and mes != "0" and ano != "0":
        # Filtra pelo campo vencimento (YYYY-MM-DD)
        prefixo = f"{ano}-{str(mes).zfill(2)}"
        filtro["vencimento"] = {"$regex": f"^{prefixo}"}
    
    return await db.contas.find(filtro, {"_id": 0}).sort("vencimento", 1).to_list(1000)
'''

padrao = r'@router\.get\("/contas"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao, c):
    c = re.sub(padrao, nova_listar.strip() + "\n\n", c)

# 2. Adicionar rota de conciliação (comparativo mensal)
rota_conciliacao = '''

@router.get("/conciliacao")
async def conciliacao(mes: str, ano: str, _u: dict = Depends(require("read"))):
    prefixo = f"{ano}-{str(mes).zfill(2)}"
    contas = await db.contas.find(
        {"vencimento": {"$regex": f"^{prefixo}"}}, {"_id": 0}
    ).to_list(1000)
    
    total_pagar = sum(c["valor"] for c in contas if c.get("tipo") == "Pagar")
    total_receber = sum(c["valor"] for c in contas if c.get("tipo") == "Receber")
    pago = sum(c["valor"] for c in contas if c.get("status") == "Pago")
    pendente = sum(c["valor"] for c in contas if c.get("status") == "Pendente")
    atrasado = sum(c["valor"] for c in contas if c.get("status") == "Atrasado")

    return {
        "total_pagar": total_pagar,
        "total_receber": total_receber,
        "pago": pago,
        "pendente": pendente,
        "atrasado": atrasado,
        "saldo": total_receber - total_pagar,
        "contas": contas
    }
'''
if "conciliacao" not in c:
    c += rota_conciliacao

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Backend: Rotas de filtro de data e conciliação criadas.")