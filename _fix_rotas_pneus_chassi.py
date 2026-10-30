import os, re, ast, datetime, zipfile

RAIZ = os.getcwd()
ARQ_CHASSI = os.path.join(RAIZ, "app", "backend", "routers", "chassi_templates.py")
ARQ_MOV    = os.path.join(RAIZ, "app", "backend", "routers", "pneu_movimentacoes.py")
ARQ_SERVER = os.path.join(RAIZ, "app", "backend", "server.py")

def backup():
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    p = os.path.join(RAIZ, "_automacao", "backups", f"BACKUP_ROTAS_PNEUS_{agora}.zip")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        for a, r in [(ARQ_CHASSI, "chassi_templates.py"), (ARQ_MOV, "pneu_movimentacoes.py"), (ARQ_SERVER, "server.py")]:
            if os.path.exists(a): z.write(a, r)
    print(f"✅ Backup: {p}")

def ler(p):
    with open(p, "r", encoding="utf-8") as f: return f.read()

def salvar(p, c):
    with open(p, "w", encoding="utf-8") as f: f.write(c)

def validar(p):
    try:
        ast.parse(ler(p)); return True
    except SyntaxError as e:
        print(f"❌ Sintaxe em {p}: {e}"); return False

def listar_rotas(p, nome):
    print(f"\n===== ROTAS EM {nome} =====")
    if not os.path.exists(p):
        print("❌ não encontrado"); return
    for l in ler(p).split("\n"):
        s = l.strip()
        if s.startswith("@router.") or (s.startswith("async def") and "(" in s):
            print(" ", s)

def corrigir_chassi():
    print("\n🛠️  chassi_templates.py")
    if not os.path.exists(ARQ_CHASSI):
        print("❌ não encontrado"); return False
    c = ler(ARQ_CHASSI)

    if re.search(r'@router\.get\(\s*["\']/?\{[^}]+\}', c):
        print("ℹ️  GET /{id} já existe."); return True

    m = re.search(r'from\s+models\.chassi_templates\s+import\s+([^\n]+)', c)
    model = next((n.strip() for n in (m.group(1).split(",") if m else []) if n.strip() and n.strip()[0].isupper()), "ChassiTemplate")

    m2 = re.search(r'db\.([a-zA-Z_][a-zA-Z0-9_]*)\.', c)
    coll = m2.group(1) if m2 else "chassi_templates"

    rota = f'''
@router.get("/{{template_id}}", response_model={model})
async def obter_template(template_id: str, _u: dict = Depends(require("read"))):
    doc = await db.{coll}.find_one({{"id": template_id}}, {{"_id": 0}})
    if not doc:
        raise HTTPException(404, "Template não encontrado.")
    return {model}(**doc)
'''

    pos = re.search(r'@router\.(put|delete)\(\s*["\']/?\{', c)
    if pos:
        c = c[:pos.start()] + rota.strip() + "\n\n" + c[pos.start():]
        print("✅ GET /{id} inserido antes de PUT/DELETE.")
    else:
        c = c.rstrip() + "\n" + rota
        print("✅ GET /{id} adicionado no final.")

    if "HTTPException" not in c.split("router =")[0]:
        c = c.replace("from fastapi import APIRouter, Depends",
                      "from fastapi import APIRouter, Depends, HTTPException", 1)
        print("✅ HTTPException importado.")

    salvar(ARQ_CHASSI, c)
    return validar(ARQ_CHASSI)

def corrigir_mov():
    print("\n🛠️  pneu_movimentacoes.py")
    if not os.path.exists(ARQ_MOV):
        print("❌ não encontrado"); return False
    c = ler(ARQ_MOV)

    if "/motivos-descarte" in c:
        print("ℹ️  /motivos-descarte já existe."); return True

    rota = '''
@router.get("/motivos-descarte")
async def motivos_descarte(_u: dict = Depends(require("read"))):
    return [
        {"codigo": "TAL-01", "descricao": "Quebra/Deformação do Talão", "responsabilidade": "OFICINA"},
        {"codigo": "TAL-02", "descricao": "Queima Térmica do Talão", "responsabilidade": "MECANICA"},
        {"codigo": "TAL-03", "descricao": "Rasgo/Dilaceração do Talão", "responsabilidade": "OFICINA"},
        {"codigo": "LAT-01", "descricao": "Bolha Lateral / Rompimento de Carcaça", "responsabilidade": "MOTORISTA"},
        {"codigo": "LAT-02", "descricao": "Corte Lateral Transversal", "responsabilidade": "MOTORISTA"},
        {"codigo": "LAT-03", "descricao": "Desgaste por Atrito Lateral", "responsabilidade": "MECANICA"},
        {"codigo": "LAT-04", "descricao": "Fadiga por Subpressão", "responsabilidade": "MOTORISTA"},
        {"codigo": "BAN-01", "descricao": "Separação de Lonas/Cintas", "responsabilidade": "MANUTENCAO"},
        {"codigo": "BAN-02", "descricao": "Arranque de Blocos", "responsabilidade": "GESTAO"},
        {"codigo": "BAN-03", "descricao": "Freiada Brusca / Escamamento", "responsabilidade": "MOTORISTA"},
        {"codigo": "BAN-04", "descricao": "Fim de Vida Regular", "responsabilidade": "NATURAL"},
        {"codigo": "REC-01", "descricao": "Recusa Técnica na Raspagem", "responsabilidade": "NATURAL"},
        {"codigo": "REC-02", "descricao": "Descolamento de Banda Aplicada", "responsabilidade": "FORNECEDOR"},
        {"codigo": "REC-03", "descricao": "Excesso/Proximidade de Furos", "responsabilidade": "OPERACAO"},
    ]
'''

    pos = re.search(r'@router\.(get|post|put|delete)\(\s*["\']/?\{', c)
    if pos:
        c = c[:pos.start()] + rota.strip() + "\n\n" + c[pos.start():]
        print("✅ /motivos-descarte inserido antes de rotas com parâmetro.")
    else:
        c = c.rstrip() + "\n" + rota
        print("✅ /motivos-descarte adicionado no final.")

    salvar(ARQ_MOV, c)
    return validar(ARQ_MOV)

def garantir_server():
    print("\n🛠️  server.py")
    if not os.path.exists(ARQ_SERVER):
        print("❌ não encontrado"); return False
    c = ler(ARQ_SERVER)
    alt = False

    if "pneu_movimentacoes" not in c:
        c = re.sub(r'(from routers import\s+)([^\n]+)',
                   lambda m: m.group(1) + "pneu_movimentacoes, " + m.group(2)
                             if "pneu_movimentacoes" not in m.group(2) else m.group(0),
                   c, count=1)
        c = c.replace("api_router.include_router(pneus.router)",
                      "api_router.include_router(pneus.router)\napi_router.include_router(pneu_movimentacoes.router)", 1)
        alt = True
        print("✅ pneu_movimentacoes incluído no server.py.")
    else:
        print("ℹ️  pneu_movimentacoes já presente.")

    if "chassi_templates" not in c:
        print("⚠️  chassi_templates NÃO está no server.py. Verifique manualmente.")
    else:
        print("ℹ️  chassi_templates já presente.")

    if alt:
        salvar(ARQ_SERVER, c)
        return validar(ARQ_SERVER)
    return True

if __name__ == "__main__":
    print("🔧 Corrigindo rotas de chassi e movimentações de pneus...\n")
    backup()
    listar_rotas(ARQ_CHASSI, "chassi_templates.py")
    listar_rotas(ARQ_MOV, "pneu_movimentacoes.py")
    ok1 = corrigir_chassi()
    ok2 = corrigir_mov()
    ok3 = garantir_server()
    print("\n===== RESULTADO =====")
    print(f"chassi_templates.py: {'✅ OK' if ok1 else '❌ FALHOU'}")
    print(f"pneu_movimentacoes.py: {'✅ OK' if ok2 else '❌ FALHOU'}")
    print(f"server.py: {'✅ OK' if ok3 else '❌ FALHOU'}")