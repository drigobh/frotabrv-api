import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_regex_pdf_{agora}.zip"
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

def melhorar_regex_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui a função handleImportPDF inteira por uma versão com Regex mais flexível
    inicio = conteudo.find("const handleImportPDF = async")
    fim = conteudo.find("};", inicio) + 2
    
    if inicio != -1 and fim != -1:
        funcao_nova = '''const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let text = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map((item: any) => item.str).join(" ") + "\\n";
      }

      // Regex flexíveis para encontrar Placa e KM em qualquer lugar do texto
      // Procura por "PLACA:" seguido de qualquer coisa, e depois uma placa (3 letras + 4 números ou padrão Mercosul)
      const placaMatch = text.match(/PLACA[^A-Z0-9]*([A-Z]{3}[0-9][A-Z0-9][0-9]{2})/i) || text.match(/PLACA:\\s*([A-Z0-9]{7})/i);
      // Procura por "KM:" seguido de números
      const kmMatch = text.match(/KM[^0-9]*(\\d+)/i);

      const payload = {
        data: new Date().toISOString().split('T')[0],
        hora: null,
        numero_nf: text.match(/Nº\\s*(\\d+)/)?.[1] || null,
        chave_nfe: text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/)?.[1]?.replace(/\\s/g, "") || null,
        cnpj: text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/)?.[1] || null,
        fornecedor: text.match(/RECEBEMOS DE\\s*(.*?)\\s*OS PRODUTOS/)?.[1]?.trim() || null,
        placa: placaMatch ? placaMatch[1].toUpperCase() : null,
        litros: text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/)?.[1] ? Number(text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/)[1].replace(",", ".")) : 0,
        preco_litro: text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/)?.[2] ? Number(text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/)[2].replace(".", "").replace(",", ".")) : 0,
        km: kmMatch ? Number(kmMatch[1]) : 0,
      };

      await apiPost("/abastecimentos/importar", payload);
      
      toast.success("Nota Fiscal importada e registrada com sucesso!");
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao importar o PDF. Verifique se o veículo está cadastrado.");
    }
  }'''
        
        conteudo = conteudo[:inicio] + funcao_nova + conteudo[fim:]
        print("⚙️ Função handleImportPDF substituída com Regex mais robusta.")

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
    else:
        print("⚠️ Função handleImportPDF não encontrada no arquivo.")

def garantir_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    if "@router.post(\"/importar\"" not in conteudo:
        print("⚠️ A rota de importação não existe no backend. Criando...")
        rota = '''
@router.post("/importar", response_model=Abastecimento, status_code=201)
async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
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
        alvo = '@router.post("", response_model=Abastecimento, status_code=201)'
        conteudo = conteudo.replace(alvo, rota + "\n" + alvo)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Rota de importação criada no backend.")
    else:
        print("✅ Rota de importação já existe no backend.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Melhoria da Regex de PDF...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    melhorar_regex_frontend(raiz)
    garantir_backend(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'fix: melhorando regex de placa e km no pdf'")
    print("git push")

if __name__ == "__main__":
    executar()