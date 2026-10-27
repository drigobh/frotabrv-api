import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BACKEND_RESTORE_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["app/backend/routers/abastecimentos.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def recriar_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    codigo = '''from fastapi import APIRouter, Depends, HTTPException, Request, Query
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.abastecimentos import Abastecimento, AbastecimentoCreate
import uuid
from datetime import datetime

router = APIRouter(prefix="/abastecimentos", tags=["abastecimentos"])

@router.get("", response_model=None)
async def listar(
    veiculo_id: str = Query(None),
    mes: str = Query(None),
    _u: dict = Depends(require("read"))
):
    query = {}
    if veiculo_id and veiculo_id != "__all__":
        query["veiculo_id"] = veiculo_id
    if mes:
        query["data"] = {"$regex": f"^{mes}"}
        
    docs = await db.abastecimentos.find(query, {"_id": 0}).sort([("data", -1), ("created_at", -1)]).to_list(5000)
    return docs

@router.get("/ultimo-km/{veiculo_id}")
async def ultimo_km(veiculo_id: str, _u: dict = Depends(require("read"))):
    veiculo = await db.veiculos.find_one({"id": veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    ultimo_abast = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo_id}, 
        {"_id": 0},
        sort=[("km", -1)]
    )
    
    km_veiculo = veiculo.get("hodometro_km", 0)
    km_abast = ultimo_abast["km"] if ultimo_abast else 0
    
    return {"ultimo_km": max(km_veiculo, km_abast)}

def limpar_km(val):
    if val is None: return 0
    s = str(val).strip()
    if s.endswith(".0"): s = s[:-2]
    s = "".join(filter(str.isdigit, s))
    return int(s) if s else 0

def calcular_km(km_atual, litros, produto, ultimo, veiculo):
    km_atual = limpar_km(km_atual)
    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km"):
        ultimo_km = limpar_km(ultimo["km"])
        km_rodados = km_atual - ultimo_km
    elif veiculo.get("hodometro_km") is not None:
        veiculo_km = limpar_km(veiculo["hodometro_km"])
        km_rodados = km_atual - veiculo_km

    if km_rodados is not None:
        if km_rodados < 0:
            km_rodados = None
        elif km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
            media_km_l = km_rodados / litros
        elif km_rodados == 0:
            media_km_l = 0

    return km_rodados, media_km_l

@router.post("/importar", response_model=None, status_code=201)
async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    def safe_float(val):
        if val is None: return 0.0
        if isinstance(val, (int, float)): return float(val)
        try: return float(str(val).replace(',', '.'))
        except: return 0.0

    try:
        placa_limpa = body.get("placa", "").strip().upper()
        veiculo = await db.veiculos.find_one({"placa": placa_limpa}, {"_id": 0})
        if not veiculo:
            raise HTTPException(status_code=404, detail=f"Veículo com placa {placa_limpa} não encontrado.")

        litros = safe_float(body.get("litros"))
        preco_litro = safe_float(body.get("preco_litro"))
        km_atual = safe_float(body.get("km"))
        valor_total = safe_float(body.get("valor_total"))
        data_recebida = body.get("data")
        produto = body.get("produto", "DIESEL").upper()

        try:
            if data_recebida and "/" in data_recebida:
                data_abast = datetime.strptime(data_recebida, "%d/%m/%Y").strftime("%Y-%m-%d")
            else:
                data_abast = data_recebida
        except:
            data_abast = data_recebida

        # TRAVA DE DUPLICIDADE
        codigo_transacao_recebido = body.get("codigo_transacao")
        chave_nfe_recebida = body.get("chave_nfe")
        numero_nf_recebido = body.get("numero_nf")
        cnpj_recebido = body.get("cnpj")

        if codigo_transacao_recebido:
            if await db.abastecimentos.find_one({"codigo_transacao": codigo_transacao_recebido}):
                raise HTTPException(409, "Registro duplicado: Código de Transação já importado.")
        elif chave_nfe_recebida:
            if await db.abastecimentos.find_one({"chave_nfe": chave_nfe_recebida}):
                raise HTTPException(409, "Registro duplicado: Chave NF-e já importada.")
        elif numero_nf_recebido and cnpj_recebido:
            if await db.abastecimentos.find_one({"numero_nf": numero_nf_recebido, "cnpj": cnpj_recebido}):
                raise HTTPException(409, "Registro duplicado: Nota Fiscal já importada.")
        else:
            existente_placa = await db.abastecimentos.find_one({
                "veiculo_id": veiculo["id"],
                "data": data_abast,
                "litros": litros
            })
            if existente_placa:
                raise HTTPException(409, "Registro duplicado: Abastecimento com esta placa, data e litros já existe.")

        if valor_total == 0:
            valor_total = litros * preco_litro
        valor_total = round(valor_total, 2)

        ultimo = await db.abastecimentos.find_one(
            {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
            {"_id": 0},
            sort=[("data", -1)]
        )

        if body.get("origem") == "excel" and body.get("km_rodados") is not None:
            km_rodados = safe_float(body.get("km_rodados"))
            media_km_l = safe_float(body.get("media_km_l"))
        else:
            km_rodados, media_km_l = calcular_km(km_atual, litros, produto, ultimo, veiculo)

        acoplamento = await db.acoplamentos.find_one(
            {"veiculo_id": veiculo["id"]},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
            
        motorista_id = acoplamento.get("motorista_id") if acoplamento else None
        motorista_label = None
        if motorista_id:
            mot = await db.motoristas.find_one({"id": motorista_id}, {"_id": 0})
            motorista_label = mot["nome"] if mot else None

        doc = {
            "id": str(uuid.uuid4()),
            "data": data_abast,
            "veiculo_id": veiculo["id"],
            "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
            "motorista_id": motorista_id,
            "motorista_label": motorista_label,
            "litros": litros,
            "preco_litro": preco_litro,
            "valor_total": valor_total,
            "posto": body.get("fornecedor") or "Importado",
            "km": km_atual,
            "km_rodados": km_rodados,
            "media_km_l": media_km_l,
            "origem": body.get("origem", "excel"),
            "produto": produto,
            "numero_nf": body.get("numero_nf"),
            "chave_nfe": body.get("chave_nfe"),
            "codigo_transacao": body.get("codigo_transacao"),
            "hora": body.get("hora"),
            "cnpj": body.get("cnpj"),
            "cidade": body.get("cidade"),
            "estado": body.get("estado"),
            "fornecedor": body.get("fornecedor"),
            "created_by": user.get("id", "sistema"),
            "created_by_name": user.get("nome", user.get("email", "Sistema")),
            "created_at": now_iso()
        }

        await db.abastecimentos.insert_one(doc)
        if km_atual > 0:
            await db.veiculos.update_one({"id": veiculo["id"]}, {"$set": {"hodometro_km": km_atual}})
        doc.pop("_id", None)
        return doc
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERRO NA IMPORTACAO: {e}")
        raise HTTPException(500, f"Erro interno ao importar: {str(e)}")

@router.post("", response_model=Abastecimento, status_code=201)
async def criar(body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "data": {"$lt": body.data}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados, media_km_l = calcular_km(body.km, body.litros, body.produto, ultimo, veiculo)

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["valor_total"] = round(body.litros * body.preco_litro, 2)
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    doc["created_by"] = user["id"]
    doc["created_by_name"] = user.get("nome", user.get("email", "Sistema"))
    doc["created_at"] = now_iso()

    if body.motorista_id:
        mot = await db.motoristas.find_one({"id": body.motorista_id}, {"_id": 0})
        doc["motorista_label"] = mot["nome"] if mot else None
    else:
        doc["motorista_label"] = None
        
    if body.combustivel_id and not body.produto:
        comb = await db.combustiveis.find_one({"id": body.combustivel_id}, {"_id": 0})
        doc["produto"] = comb["nome"] if comb else "Diesel S-10"

    await db.abastecimentos.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/{id}", response_model=Abastecimento)
async def atualizar(id: str, body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
        
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "data": {"$lt": body.data}, "id": {"$ne": id}},
        {"_id": 0},
        sort=[("data", -1)]
    )
    
    km_rodados, media_km_l = calcular_km(body.km, body.litros, body.produto, ultimo, veiculo)

    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["valor_total"] = round(body.litros * body.preco_litro, 2)
    doc["km_rodados"] = km_rodados
    doc["media_km_l"] = media_km_l
    
    if body.motorista_id:
        mot = await db.motoristas.find_one({"id": body.motorista_id}, {"_id": 0})
        doc["motorista_label"] = mot["nome"] if mot else None
    else:
        doc["motorista_label"] = None
        
    if body.combustivel_id and not body.produto:
        comb = await db.combustiveis.find_one({"id": body.combustivel_id}, {"_id": 0})
        doc["produto"] = comb["nome"] if comb else "Diesel S-10"

    await db.abastecimentos.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.abastecimentos.delete_one({"id": id})
    return {"ok": True}
'''
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Backend reescrito do zero, com todas as rotas e trava de duplicidade ativadas.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    recriar_backend(raiz)