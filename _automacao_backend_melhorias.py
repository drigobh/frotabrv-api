import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_backend_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    print("📦 Criando Backup Rápido do Backend...")
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

def atualizar_backend(raiz):
    pasta_routers = os.path.join(raiz, "app", "backend", "routers")
    caminho_abast = os.path.join(pasta_routers, "abastecimentos.py")

    if not os.path.exists(caminho_abast):
        print("❌ Arquivo routers/abastecimentos.py não encontrado.")
        return

    with open(caminho_abast, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar validação de duplicidade na importação
    if "# Verifica duplicidade" not in conteudo:
        conteudo = conteudo.replace(
            "novo = Abastecimento(**data)",
            """# Verifica duplicidade (mesma data, veiculo e litros)
    existe = await db.abastecimentos.find_one({
        "data": data["data"], 
        "veiculo_id": veiculo["id"],
        "litros": data["litros"]
    })
    if existe:
        raise HTTPException(status_code=400, detail=f"Abastecimento duplicado na linha (Data: {data['data']}, Litros: {data['litros']})")
        
    novo = Abastecimento(**data)"""
        )
        print("✅ Validação de duplicidade adicionada.")

    # 2. Criar a rota de Hodômetro Atual
    if "/hodometro-atual" not in conteudo:
        rota_hodometro = '''
@router.get("/hodometro-atual")
async def get_hodometro_atual(user: dict = Depends(require("read"))):
    from datetime import datetime, timedelta
    
    veiculos = await db.veiculos.find({"ativo": True}, {"_id": 0}).to_list(None)
    resultado = []
    
    agora = datetime.now()
    mes_atual = agora.strftime("%Y-%m")
    
    primeiro_dia_mes = agora.replace(day=1)
    ultimo_dia_mes_anterior = primeiro_dia_mes - timedelta(days=1)
    mes_anterior = ultimo_dia_mes_anterior.strftime("%Y-%m")

    for v in veiculos:
        abast = await db.abastecimentos.find({"veiculo_id": v["id"]}).sort("data", 1).to_list(None)
        
        if not abast:
            resultado.append({
                "veiculo_id": v["id"], "placa": v["placa"], "modelo": v["modelo"],
                "ultimo_km": 0, "qtd_geral": 0, "qtd_mes": 0, "qtd_mes_anterior": 0,
                "media_ultimo": 0, "media_mes": 0, "media_mes_anterior": 0,
                "total_mes": 0, "total_mes_anterior": 0, "media_preco_mes": 0
            })
            continue

        ultimo = abast[-1]
        
        abast_mes = [a for a in abast if a["data"].startswith(mes_atual)]
        abast_anterior = [a for a in abast if a["data"].startswith(mes_anterior)]
        
        def calc_media(lista):
            validos = [a for a in lista if a.get("km_rodados") and a.get("km_rodados") > 0]
            if not validos: return 0
            km = sum(a["km_rodados"] for a in validos)
            l = sum(a["litros"] for a in validos)
            return km / l if l > 0 else 0
            
        def calc_total(lista): return sum(a["valor_total"] for a in lista)
        def calc_preco_medio(lista):
            l = sum(a["litros"] for a in lista)
            v = sum(a["valor_total"] for a in lista)
            return v / l if l > 0 else 0

        resultado.append({
            "veiculo_id": v["id"], "placa": v["placa"], "modelo": v["modelo"],
            "ultimo_km": ultimo["km"],
            "qtd_geral": len(abast), "qtd_mes": len(abast_mes), "qtd_mes_anterior": len(abast_anterior),
            "media_ultimo": ultimo.get("media_km_l") or 0,
            "media_mes": calc_media(abast_mes), "media_mes_anterior": calc_media(abast_anterior),
            "total_mes": calc_total(abast_mes), "total_mes_anterior": calc_total(abast_anterior),
            "media_preco_mes": calc_preco_medio(abast_mes)
        })
    return resultado
'''
        conteudo += "\n" + rota_hodometro
        print("✅ Rota '/hodometro-atual' criada.")

    with open(caminho_abast, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Backend atualizado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backup_rapido(raiz)
    atualizar_backend(raiz)
    print("\n🚀 Faça o commit e push para o Render para aplicar as mudanças no backend.")