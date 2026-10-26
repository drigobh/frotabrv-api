import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Encontra a rota de criação manual e substitui pelo bloco correto
    padrao = re.compile(r'@router\.post\("", response_model=None, status_code=201\)\s*async def criar\([\s\S]*?return doc', re.DOTALL)
    
    nova_rota = '''@router.post("", response_model=None, status_code=201)
async def criar(body: dict, request: Request, user: dict = Depends(require("write"))):
    veiculo_id = body.get("veiculo_id")
    if not veiculo_id:
        raise HTTPException(400, "Veículo é obrigatório")
    
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    # Busca o último abastecimento para calcular KM
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id, "data": {"$lt": body.get("data")}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    litros = float(body.get("litros") or 0)
    preco_litro = float(body.get("preco_litro") or 0)
    km_atual = float(body.get("km") or 0)

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and km_atual > ultimo["km"]:
        km_rodados = km_atual - ultimo["km"]
        if litros > 0:
            media_km_l = km_rodados / litros

    # Monta o documento
    doc = {k: v for k, v in body.items() if v is not None}
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo.get('modelo', '')}"
    doc["valor_total"] = round(litros * preco_litro, 2)
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    doc["created_by"] = user.get("id", "sistema")
    doc["created_at"] = now_iso()
    doc["origem"] = doc.get("origem", "manual")

    if body.get("motorista_id"):
        mot = await db.motoristas.find_one({"id": body["motorista_id"]}, {"_id": 0})
        doc["motorista_label"] = mot["nome"] if mot else None
    else:
        doc["motorista_label"] = None

    await db.abastecimentos.insert_one(doc)
    doc.pop("_id", None)
    return doc'''

    if padrao.search(c):
        c = padrao.sub(lambda m: nova_rota, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Função de criação manual reescrita (sem erros de variável).")
    else:
        print("⚠️ Não foi possível encontrar a função de criação.")

if __name__ == "__main__":
    fix_backend(os.getcwd())