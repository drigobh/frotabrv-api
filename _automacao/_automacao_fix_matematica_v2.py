import os
import datetime
import zipfile
import re

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_math_v2_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    print("📦 Criando Backup Rápido...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_backend = os.path.join(raiz, "app", "backend")
        if os.path.exists(pasta_backend):
            for root, dirs, files in os.walk(pasta_backend):
                dirs[:] = [d for d in dirs if d not in ['__pycache__', 'backups']]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try: zipf.write(caminho_completo, caminho_relativo)
                    except: pass

def corrigir_backend(raiz):
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    caminho_abast = os.path.join(pasta_routers, "abastecimentos.py")

    if not os.path.exists(caminho_abast):
        print("❌ Arquivo abastecimentos.py não encontrado.")
        return

    with open(caminho_abast, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Regex para encontrar a rota de importar, independente do nome exato ou parâmetros
    # Ele busca por @router.post("/importar") e vai até o próximo @router
    padrao = re.compile(r'@router\.post\("/importar"\)[\s\S]*?(?=@router|$)', re.DOTALL)
    
    nova_funcao = '''@router.post("/importar")
async def importar_abastecimento(
    payload: dict, 
    user: dict = Depends(require("write"))
):
    # 1. Busca o veículo pela placa
    veiculo = await db.veiculos.find_one({"placa": payload.get("placa")})
    if not veiculo:
        raise HTTPException(status_code=404, detail=f"Veículo com placa {payload.get('placa')} não encontrado.")

    # 2. Verifica duplicidade
    existe = await db.abastecimentos.find_one({
        "data": payload.get("data"),
        "veiculo_id": veiculo["id"],
        "litros": payload.get("litros")
    })
    if existe:
        raise HTTPException(status_code=400, detail=f"Abastecimento duplicado (Data: {payload.get('data')}, Litros: {payload.get('litros')})")

    # 3. Busca o último abastecimento ANTES da data atual
    ultimo = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "data": {"$lt": payload.get("data")}},
        sort=[("data", -1)]
    )

    km_rodados = None
    media_km_l = None

    if ultimo and ultimo.get("km") and payload.get("km"):
        km_rodados = payload.get("km") - ultimo["km"]
        if km_rodados > 0 and payload.get("litros") > 0:
            media_km_l = km_rodados / payload.get("litros")
        else:
            km_rodados = None

    valor_total = (payload.get("litros") or 0) * (payload.get("preco_litro") or 0)

    novo = {
        "id": str(uuid.uuid4()),
        "data": payload.get("data"),
        "veiculo_id": veiculo["id"],
        "veiculo_label": f"{veiculo['placa']} · {veiculo['modelo']}",
        "motorista_id": None,
        "motorista_label": None,
        "litros": payload.get("litros"),
        "preco_litro": payload.get("preco_litro"),
        "valor_total": valor_total,
        "posto": payload.get("fornecedor") or "Importado",
        "km": payload.get("km"),
        "km_rodados": km_rodados,
        "media_km_l": media_km_l,
        "origem": "pdf",
        "numero_nf": payload.get("numero_nf"),
        "chave_nfe": payload.get("chave_nfe"),
        "hora": payload.get("hora"),
        "cnpj": payload.get("cnpj"),
        "fornecedor": payload.get("fornecedor"),
        "created_at": now_iso()
    }

    await db.abastecimentos.insert_one(novo)
    return novo

'''
    
    if padrao.search(conteudo):
        conteudo = padrao.sub(nova_funcao, conteudo)
        print("✅ Função de importar substituída com sucesso!")
    else:
        # Se não achar a rota, tenta achar a função solta
        inicio = conteudo.find("async def importar_abastecimento")
        if inicio != -1:
            prox_rota = conteudo.find("@router", inicio + 10)
            if prox_rota == -1: prox_rota = len(conteudo)
            conteudo = conteudo[:inicio] + nova_funcao.replace('@router.post("/importar")\n', '') + conteudo[prox_rota:]
            print("✅ Função encontrada e substituída (sem decorator).")
        else:
            print("❌ Não foi possível encontrar a rota ou função de importar. O arquivo pode ter sido alterado.")

    # Garante que os imports necessários existam
    if "import uuid" not in conteudo:
        conteudo = "import uuid\n" + conteudo
    if "from lib.time import now_iso" not in conteudo:
        conteudo = conteudo.replace("from lib.db import db", "from lib.db import db\nfrom lib.time import now_iso")

    with open(caminho_abast, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Backend atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    corrigir_backend(raiz)
    print("\n🚀 Concluído! Faça o commit e push para o Render.")