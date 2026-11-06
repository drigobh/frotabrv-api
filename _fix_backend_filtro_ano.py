import os
import re

path = os.path.join(os.getcwd(), "app", "backend", "routers", "financeiro.py")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Atualizar a rota de listar contas
nova_listar = '''
@router.get("/contas")
async def listar_contas(tipo: str = None, mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if tipo:
        filtro["tipo"] = tipo
    if ano and ano != "0":
        if mes and mes != "0":
            # Mês específico
            prefixo = f"{ano}-{str(mes).zfill(2)}"
            filtro["vencimento"] = {"$regex": f"^{prefixo}"}
        else:
            # Todos os meses do ano
            filtro["vencimento"] = {"$regex": f"^{ano}"}
    
    return await db.contas.find(filtro, {"_id": 0}).sort("vencimento", 1).to_list(1000)
'''

padrao = r'@router\.get\("/contas"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao, c):
    c = re.sub(padrao, nova_listar.strip() + "\n\n", c)

# 2. Atualizar a rota de resumo (cards)
novo_resumo = '''
@router.get("/resumo")
async def resumo_financeiro(mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if ano and ano != "0":
        if mes and mes != "0":
            prefixo = f"{ano}-{str(mes).zfill(2)}"
            filtro["vencimento"] = {"$regex": f"^{prefixo}"}
        else:
            filtro["vencimento"] = {"$regex": f"^{ano}"}

    contas = await db.contas.find(filtro, {"_id": 0}).to_list(1000)
    
    a_pagar = sum(c["valor"] for c in contas if c.get("tipo") == "Pagar" and c.get("status") == "Pendente")
    a_receber = sum(c["valor"] for c in contas if c.get("tipo") == "Receber" and c.get("status") == "Pendente")
    vencido = sum(c["valor"] for c in contas if c.get("status") == "Atrasado")
    total_pago = sum(c["valor"] for c in contas if c.get("status") == "Pago")
    
    return {
        "a_pagar": a_pagar,
        "a_receber": a_receber,
        "vencido": vencido,
        "total_pago": total_pago,
        "saldo": a_receber - a_pagar
    }
'''

padrao_resumo = r'@router\.get\("/resumo"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao_resumo, c):
    c = re.sub(padrao_resumo, novo_resumo.strip() + "\n\n", c)

# 3. Atualizar a rota de conciliação
nova_conc = '''
@router.get("/conciliacao")
async def conciliacao(mes: str = None, ano: str = None, _u: dict = Depends(require("read"))):
    filtro = {}
    if ano and ano != "0":
        if mes and mes != "0":
            prefixo = f"{ano}-{str(mes).zfill(2)}"
            filtro["vencimento"] = {"$regex": f"^{prefixo}"}
        else:
            filtro["vencimento"] = {"$regex": f"^{ano}"}

    contas = await db.contas.find(filtro, {"_id": 0}).to_list(1000)
    
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

padrao_conc = r'@router\.get\("/conciliacao"\)[\s\S]*?(?=@router|\Z)'
if re.search(padrao_conc, c):
    c = re.sub(padrao_conc, nova_conc.strip() + "\n\n", c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Backend: Filtro 'Todos os Meses' adicionado nas rotas de contas, resumo e conciliação.")