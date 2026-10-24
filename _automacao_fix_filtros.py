import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que o Query está importado do FastAPI
    if "Query" not in c:
        c = c.replace("from fastapi import APIRouter, Depends, HTTPException, Request", "from fastapi import APIRouter, Depends, HTTPException, Request, Query")

    # 2. Substituir a função listar inteira
    padrao = re.compile(r'@router.get\("", response_model=None\)\s*async def listar\([\s\S]*?return docs', re.DOTALL)
    
    nova_funcao = '''@router.get("", response_model=None)
async def listar(
    veiculo_id: str = Query(None),
    mes: str = Query(None),
    _u: dict = Depends(require("read"))
):
    # Monta a query do MongoDB dinamicamente
    query = {}
    
    # Filtro por Veículo (ignora o valor "__all__" da tela)
    if veiculo_id and veiculo_id != "__all__":
        query["veiculo_id"] = veiculo_id
        
    # Filtro por Mês (formato YYYY-MM)
    if mes:
        query["data"] = {"$regex": f"^{mes}"}
        
    docs = await db.abastecimentos.find(query, {"_id": 0}).sort("data", -1).to_list(5000)
    return docs'''

    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
    else:
        # Fallback de segurança caso o regex não encontre
        c = c.replace('''@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.abastecimentos.find({}, {"_id": 0}).sort("data", -1).to_list(5000)
    return docs''', nova_funcao)
        
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend atualizado! A rota de listagem agora processa os filtros de Veículo e Mês.")

if __name__ == "__main__":
    fix_backend(os.getcwd())