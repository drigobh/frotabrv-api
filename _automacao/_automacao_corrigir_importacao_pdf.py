import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_corrigir_pdf_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def corrigir_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Garante que a rota /importar existe e está correta
    if "@router.post(\"/importar\"" not in conteudo:
        print("⚠️ A rota de importação não existe no backend. Vamos criá-la.")
        rota = '''
@router.post("/importar", response_model=Abastecimento, status_code=201)
async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    """Recebe os dados extraídos do PDF e cria o abastecimento."""
    placa_limpa = body.get("placa", "").strip().upper()
    veiculo = await db.veiculos.find_one({"placa": placa_limpa})
    
    if not veiculo:
        raise HTTPException(404, f"Veículo com placa '{placa_limpa}' não encontrado.")

    acoplamento = await db.acoplamentos.find_one({"veiculo_id": veiculo["id"], "status": "ativo"})
    motorista_label = None
    if acoplamento and acoplamento.get("motorista_id"):
        motorista = await db.motoristas.find_one({"id": acoplamento["motorista_id"]})
        if motorista:
            motorista_label = motorista["nome"]

    km = body.get("km", 0)
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "km": {"$lt": km}},
        sort=[("km", -1)]
    )
    km_anterior = anterior["km"] if anterior else veiculo.get("hodometro_km", 0)
    km_rodados = km - km_anterior if km_anterior > 0 else None
    
    litros = body.get("litros", 0)
    preco_litro = body.get("preco_litro", 0)
    media_km_l = km_rodados / litros if km_rodados and litros > 0 else None
    valor_total = litros * preco_litro

    doc = {
        "id": str(uuid.uuid4()),
        "data": body.get("data", now_iso()),
        "hora": body.get("hora"),
        "veiculo_id": veiculo["id"],
        "motorista_id": acoplamento.get("motorista_id") if acoplamento else None,
        "motorista_label": motorista_label,
        "litros": litros,
        "preco_litro": preco_litro,
        "posto": body.get("fornecedor", "Importado via PDF"),
        "km": km,
        "observacoes": "",
        "numero_nf": body.get("numero_nf"),
        "chave_nfe": body.get("chave_nfe"),
        "cnpj": body.get("cnpj"),
        "fornecedor": body.get("fornecedor"),
        "origem": "pdf",
        "valor_total": round(valor_total, 2),
        "km_rodados": km_rodados,
        "media_km_l": round(media_km_l, 2) if media_km_l else None,
        "veiculo_label": f"{veiculo['placa']} - {veiculo.get('modelo', '')}",
        "created_by": user["nome"],
        "created_at": now_iso()
    }
    
    await db.abastecimentos.insert_one(dict(doc))
    await audit(user, "importar", "abastecimentos", doc["id"], f"NF: {doc['numero_nf']}", request)
    return Abastecimento(**doc)
'''
        # Insere antes do POST manual
        alvo = '@router.post("", response_model=Abastecimento, status_code=201)'
        conteudo = conteudo.replace(alvo, rota + "\n" + alvo)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Rota de importação recriada no backend.")
    else:
        print("✅ Rota de importação já existe no backend.")

def corrigir_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Corrige as Regex de extração
    regex_antiga = '''      const nfMatch = text.match(/Nº\\s*(\\d+)/);
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/);
      const cnpjMatch = text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/);
      const fornecedorMatch = text.match(/RECEBEMOS DE\\s*(.*?)\\s*OS PRODUTOS/);
      const litrosMatch = text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/);
      const kmMatch = text.match(/KM\\s*(\\d+)/);
      const placaMatch = text.match(/PLACA DO VEÍCULO\\s*([A-Z0-9]+)/);
      const horaMatch = text.match(/(\\d{2}:\\d{2}:\\d{2})/);'''

    regex_nova = '''      const nfMatch = text.match(/Nº\\s*(\\d+)/);
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/);
      const cnpjMatch = text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/);
      const fornecedorMatch = text.match(/RECEBEMOS DE\\s*(.*?)\\s*OS PRODUTOS/);
      
      // Regex de Litros e Preço (ignorando espaços)
      const litrosMatch = text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/);
      
      // Regex de KM (procura por "KM: 616416" ou similar)
      const kmMatch = text.match(/KM:\\s*(\\d+)/);
      
      // Regex de Placa (procura por "PLACA: QPR3736" ou similar)
      const placaMatch = text.match(/PLACA:\\s*([A-Z0-9]{7})/);
      
      const horaMatch = text.match(/(\\d{2}:\\d{2}:\\d{2})/);'''

    if regex_antiga in conteudo:
        conteudo = conteudo.replace(regex_antiga, regex_nova)
        print("⚙️ Regex de extração de PDF atualizadas (Placa e KM).")
    else:
        print("⚠️ Regex original não encontrada. O arquivo pode estar diferente.")

    # Garante que a placa é enviada em maiúscula
    if "placa: placaMatch ? placaMatch[1] : null" in conteudo:
        conteudo = conteudo.replace(
            "placa: placaMatch ? placaMatch[1] : null",
            "placa: placaMatch ? placaMatch[1].toUpperCase() : null"
        )
        print("⚙️ Placa convertida para maiúscula na importação.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção de Importação de PDF...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_backend(raiz)
    corrigir_frontend(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'fix: corrigindo regex de placa e rota de importacao'")
    print("git push")

if __name__ == "__main__":
    executar()