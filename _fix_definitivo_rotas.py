import os
import re
import ast
import datetime
import zipfile

RAIZ = os.getcwd()

ARQ_CHASSI = os.path.join(RAIZ, "app", "backend", "routers", "chassi_templates.py")
ARQ_MOV    = os.path.join(RAIZ, "app", "backend", "routers", "pneu_movimentacoes.py")
ARQ_SERVER = os.path.join(RAIZ, "app", "backend", "server.py")

def backup():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    p = os.path.join(RAIZ, "_automacao", "backups", f"BACKUP_ROTAS_DEFINITIVO_{agora}.zip")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        for a, r in [(ARQ_CHASSI, "chassi_templates.py"),
                     (ARQ_MOV, "pneu_movimentacoes.py"),
                     (ARQ_SERVER, "server.py")]:
            if os.path.exists(a):
                z.write(a, r)
    print(f"✅ Backup: {p}")

def validar(p):
    try:
        ast.parse(open(p, encoding="utf-8").read())
        return True
    except SyntaxError as e:
        print(f"❌ Sintaxe em {p}: {e}")
        return False

# ============================================================
# 1) Recreia chassi_templates.py com ordem correta
# ============================================================
NOVO_CHASSI = '''import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.chassi_templates import ChassiTemplateCreate, ChassiTemplate

router = APIRouter(prefix="/chassi-templates", tags=["Chassi Templates"])


@router.get("", response_model=list[ChassiTemplate])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.chassi_templates.find({}, {"_id": 0}).sort("nome", 1).to_list(200)
    return [ChassiTemplate(**d) for d in docs]


@router.post("", response_model=ChassiTemplate, status_code=201)
async def criar(body: ChassiTemplateCreate, user: dict = Depends(require("write"))):
    existente = await db.chassi_templates.find_one(
        {"nome": {"$regex": f"^{body.nome}$", "$options": "i"}}
    )
    if existente:
        raise HTTPException(409, "Ja existe um template com este nome.")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.chassi_templates.insert_one(dict(doc))
    return ChassiTemplate(**doc)


# ROTA FIXA ANTES DAS ROTAS COM PARAMETRO
@router.post("/seed")
async def seed_templates(_u: dict = Depends(require("write"))):
    templates = [
        {"nome": "Cavalo 4x2 Toco", "categoria": "CAVALO", "qtd_estepes": 1, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "DIRECIONAL", "tem_suspensor": False},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
        ]},
        {"nome": "Cavalo 6x2 Trucado Standard", "categoria": "CAVALO", "qtd_estepes": 1, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "DIRECIONAL", "tem_suspensor": False},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRUCK", "tem_suspensor": True},
        ]},
        {"nome": "Cavalo 6x4 Tracado Pesado", "categoria": "CAVALO", "qtd_estepes": 0, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "DIRECIONAL", "tem_suspensor": False},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "TRACAO", "tem_suspensor": False},
        ]},
        {"nome": "Carreta 2 Eixos", "categoria": "CARRETA", "qtd_estepes": 2, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": True},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
        ]},
        {"nome": "Carreta 3 Eixos Convencional", "categoria": "CARRETA", "qtd_estepes": 2, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": True},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
        ]},
        {"nome": "Carreta 3 Eixos Vanderleia", "categoria": "CARRETA", "qtd_estepes": 2, "eixos": [
            {"numero_eixo": 1, "tipo_rodagem": "SIMPLES", "funcao_mecanica": "LIVRE", "tem_suspensor": True},
            {"numero_eixo": 2, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
            {"numero_eixo": 3, "tipo_rodagem": "DUPLA", "funcao_mecanica": "LIVRE", "tem_suspensor": False},
        ]},
    ]
    inseridos = 0
    for t in templates:
        existente = await db.chassi_templates.find_one(
            {"nome": {"$regex": f"^{t['nome']}$", "$options": "i"}}
        )
        if not existente:
            t["id"] = str(uuid.uuid4())
            t["created_at"] = now_iso()
            await db.chassi_templates.insert_one(dict(t))
            inseridos += 1
    return {"ok": True, "inseridos": inseridos}


# GET POR ID (DEPOIS das rotas fixas)
@router.get("/{template_id}")
async def obter_template(template_id: str, _u: dict = Depends(require("read"))):
    doc = await db.chassi_templates.find_one({"id": template_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Template de chassi nao encontrado.")
    return doc


@router.put("/{template_id}", response_model=ChassiTemplate)
async def atualizar(template_id: str, body: ChassiTemplateCreate, user: dict = Depends(require("write"))):
    await db.chassi_templates.update_one({"id": template_id}, {"$set": body.model_dump()})
    doc = await db.chassi_templates.find_one({"id": template_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Template nao encontrado.")
    return ChassiTemplate(**doc)


@router.delete("/{template_id}")
async def excluir(template_id: str, _u: dict = Depends(require("delete"))):
    await db.chassi_templates.delete_one({"id": template_id})
    return {"ok": True}
'''

# ============================================================
# 2) pneu_movimentacoes.py: adiciona /motivos-descarte antes de /{pneu_id}/historico
# ============================================================
ROTA_MOTIVOS = '''
@router.get("/motivos-descarte")
async def motivos_descarte(_u: dict = Depends(require("read"))):
    return [
        {"codigo": "TAL-01", "descricao": "Quebra ou Deformacao do Talao", "responsabilidade": "OFICINA"},
        {"codigo": "TAL-02", "descricao": "Queima / Ressecamento Termico do Talao", "responsabilidade": "MECANICA"},
        {"codigo": "TAL-03", "descricao": "Rasgo / Dilaceracao do Talao", "responsabilidade": "OFICINA"},
        {"codigo": "LAT-01", "descricao": "Bolha Lateral / Rompimento de Carcaca", "responsabilidade": "MOTORISTA"},
        {"codigo": "LAT-02", "descricao": "Corte / Dilaceracao Lateral Transversal", "responsabilidade": "MOTORISTA"},
        {"codigo": "LAT-03", "descricao": "Desgaste por Atrito Lateral (Rocamento)", "responsabilidade": "MECANICA"},
        {"codigo": "LAT-04", "descricao": "Fadiga por Subpressao (Rodar Baixo/Murcho)", "responsabilidade": "MOTORISTA"},
        {"codigo": "BAN-01", "descricao": "Separacao de Lonas / Cintas Metalicas", "responsabilidade": "MANUTENCAO"},
        {"codigo": "BAN-02", "descricao": "Arranque de Blocos (Picotamento Severo)", "responsabilidade": "GESTAO"},
        {"codigo": "BAN-03", "descricao": "Freiada Brusca / Escamamento Plano", "responsabilidade": "MOTORISTA"},
        {"codigo": "BAN-04", "descricao": "Fim de Vida Regular (Desgaste Natural)", "responsabilidade": "NATURAL"},
        {"codigo": "REC-01", "descricao": "Recusa Tecnica na Raspagem (Carcaca Fadigada)", "responsabilidade": "NATURAL"},
        {"codigo": "REC-02", "descricao": "Descolamento de Banda Aplicada", "responsabilidade": "FORNECEDOR"},
        {"codigo": "REC-03", "descricao": "Excesso de Furos / Proximidade de Furos", "responsabilidade": "OPERACAO"},
    ]
'''

def corrigir_mov():
    print("\n🛠️  pneu_movimentacoes.py")
    if not os.path.exists(ARQ_MOV):
        print("❌ nao encontrado"); return False
    c = open(ARQ_MOV, encoding="utf-8").read()

    if "/motivos-descarte" in c:
        print("ℹ️  /motivos-descarte ja existe."); return True

    pos = re.search(r'@router\.(get|post|put|delete)\(\s*["\']/?\{', c)
    if pos:
        c = c[:pos.start()] + ROTA_MOTIVOS.strip() + "\n\n" + c[pos.start():]
        print("✅ /motivos-descarte inserido ANTES das rotas com parametro.")
    else:
        c = c.rstrip() + "\n" + ROTA_MOTIVOS
        print("✅ /motivos-descarte adicionado no final.")

    open(ARQ_MOV, "w", encoding="utf-8").write(c)
    return validar(ARQ_MOV)

def garantir_server():
    print("\n🛠️  server.py")
    if not os.path.exists(ARQ_SERVER):
        print("❌ nao encontrado"); return False
    c = open(ARQ_SERVER, encoding="utf-8").read()
    alt = False
    if "pneu_movimentacoes" not in c:
        c = re.sub(r'(from routers import\s+)([^\n]+)',
                   lambda m: m.group(1) + "pneu_movimentacoes, " + m.group(2)
                             if "pneu_movimentacoes" not in m.group(2) else m.group(0),
                   c, count=1)
        c = c.replace("api_router.include_router(pneus.router)",
                      "api_router.include_router(pneus.router)\napi_router.include_router(pneu_movimentacoes.router)", 1)
        alt = True
        print("✅ pneu_movimentacoes incluido no server.py.")
    else:
        print("ℹ️  pneu_movimentacoes ja presente.")
    if "chassi_templates" not in c:
        print("⚠️  chassi_templates NAO esta no server.py.")
    else:
        print("ℹ️  chassi_templates ja presente.")
    if alt:
        open(ARQ_SERVER, "w", encoding="utf-8").write(c)
        return validar(ARQ_SERVER)
    return True

if __name__ == "__main__":
    print("🔧 Correcao definitiva das rotas de chassi e movimentacoes...\n")
    backup()

    # 1) Reescreve chassi_templates.py inteiro
    open(ARQ_CHASSI, "w", encoding="utf-8").write(NOVO_CHASSI)
    print("✅ chassi_templates.py reescrito (ordem correta, UTF-8, GET /{id} antes de PUT/DELETE).")
    ok1 = validar(ARQ_CHASSI)

    # 2) Corrige pneu_movimentacoes.py
    ok2 = corrigir_mov()

    # 3) Garante router no server.py
    ok3 = garantir_server()

    print("\n===== RESULTADO =====")
    print(f"chassi_templates.py: {'✅ OK' if ok1 else '❌ FALHOU'}")
    print(f"pneu_movimentacoes.py: {'✅ OK' if ok2 else '❌ FALHOU'}")
    print(f"server.py: {'✅ OK' if ok3 else '❌ FALHOU'}")

    if ok1 and ok2 and ok3:
        print("\n✅ Correcao aplicada! REINICIE O BACKEND e depois faca o deploy:")
        print("   (Ctrl+C no uvicorn e subir de novo)")
        print("   git add .")
        print('   git commit -m "fix: rotas chassi-templates/{id} e pneu-movimentacoes/motivos-descarte"')
        print("   git push")