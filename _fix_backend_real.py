import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BACKEND_REAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["app/backend/routers/abastecimentos.py"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    bloco_antigo = '''    litros = body.get("litros") or 0
    preco_litro = body.get("preco_litro") or 0
    data_recebida = body.get("data")
    km_atual = body.get("km") or 0
    produto = body.get("produto", "DIESEL").upper()

    try:
        if "/" in data_recebida:
            data_abast = datetime.strptime(data_recebida, "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            data_abast = data_recebida
    except:
        data_abast = data_recebida

    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    km_rodados, media_km_l = calcular_km(km_atual, litros, produto, ultimo, veiculo)

    try:
        valor_total = float(body.get("valor_total") or 0)
    except:
        valor_total = 0
        
    if valor_total == 0:
        valor_total = float(litros) * float(preco_litro)
    valor_total = round(valor_total, 2)'''

    bloco_novo = '''    def parse_num(val):
        if val is None: return 0.0
        if isinstance(val, (int, float)): return float(val)
        val = str(val).strip()
        if ',' in val:
            val = val.replace('.', '').replace(',', '.')
        try: return float(val)
        except: return 0.0

    litros = parse_num(body.get("litros"))
    preco_litro = parse_num(body.get("preco_litro"))
    data_recebida = body.get("data")
    km_atual = parse_num(body.get("km"))
    produto = str(body.get("produto", "DIESEL")).upper()

    try:
        if "/" in data_recebida:
            data_abast = datetime.strptime(data_recebida, "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            data_abast = data_recebida
    except:
        data_abast = data_recebida

    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": data_abast}},
        {"_id": 0},
        sort=[("data", -1)]
    )

    # Se for Edenred (excel) e a planilha mandou o rodados, usa o da planilha!
    if body.get("origem") == "excel" and body.get("km_rodados") is not None:
        km_rodados = parse_num(body.get("km_rodados"))
        media_km_l = parse_num(body.get("media_km_l"))
    else:
        km_rodados, media_km_l = calcular_km(km_atual, litros, produto, ultimo, veiculo)

    valor_total = parse_num(body.get("valor_total"))
    if valor_total == 0:
        valor_total = litros * preco_litro
    valor_total = round(valor_total, 2)'''

    if bloco_antigo in c:
        c = c.replace(bloco_antigo, bloco_novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend corrigido com sucesso! O Edenred agora aceitará os valores corretos.")
    else:
        print("⚠️ Não foi possível encontrar o bloco exato. O código pode ter mudado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)