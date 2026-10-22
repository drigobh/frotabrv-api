import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_rota_import_{agora}.zip"
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

def adicionar_rota_importar(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    rota = '''
@router.post("/importar", response_model=Abastecimento, status_code=201)
async def importar_pdf(body: dict, request: Request, user: dict = Depends(require("write"))):
    """Recebe os dados extraídos do PDF e cria o abastecimento."""
    
    # 1. Verifica se o veículo existe pela placa
    veiculo = await db.veiculos.find_one({"placa": body.get("placa")})
    if not veiculo:
        raise HTTPException(404, f"Veículo com placa {body.get('placa')} não encontrado.")
    
    # 2. Verifica o acoplamento ativo para pegar o motorista e carreta
    acoplamento = await db.acoplamentos.find_one({"veiculo_id": veiculo["id"], "status": "ativo"})
    motorista_label = None
    if acoplamento and acoplamento.get("motorista_id"):
        motorista = await db.motoristas.find_one({"id": acoplamento["motorista_id"]})
        if motorista:
            motorista_label = motorista["nome"]

    # 3. Calcula os KM rodados
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": veiculo["id"], "km": {"$lt": body["km"]}},
        sort=[("km", -1)]
    )
    km_anterior = anterior["km"] if anterior else veiculo.get("hodometro_km", 0)
    km_rodados = body["km"] - km_anterior if km_anterior > 0 else None
    media_km_l = km_rodados / body["litros"] if km_rodados and body["litros"] > 0 else None
    valor_total = body["litros"] * body["preco_litro"]

    # 4. Cria o documento
    doc = {
        "id": str(uuid.uuid4()),
        "data": body["data"],
        "hora": body.get("hora"),
        "veiculo_id": veiculo["id"],
        "motorista_id": acoplamento.get("motorista_id") if acoplamento else None,
        "motorista_label": motorista_label,
        "litros": body["litros"],
        "preco_litro": body["preco_litro"],
        "posto": body.get("fornecedor", "Importado via PDF"),
        "km": body["km"],
        "observacoes": body.get("observacoes", ""),
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

    if "@router.post(\"/importar\"" not in conteudo:
        # Insere a rota antes do último @router.post (que é o de criar manual)
        alvo = '@router.post("", response_model=Abastecimento, status_code=201)'
        conteudo = conteudo.replace(alvo, rota + "\n" + alvo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Backend: Rota de importação de PDF criada.")
    else:
        print("ℹ️ A rota de importação já existe no backend.")

def atualizar_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui a função handleImportPDF para chamar a nova rota
    funcao_antiga = '''      // Preenche o formulário
      setForm(prev => ({
        ...prev,
        numero_nf: nfMatch ? nfMatch[1] : prev.numero_nf,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\\s/g, "") : prev.chave_nfe,
        cnpj: cnpjMatch ? cnpjMatch[1] : prev.cnpj,
        fornecedor: fornecedorMatch ? fornecedorMatch[1].trim() : prev.fornecedor,
        litros: litrosMatch ? litrosMatch[1].replace(",", ".") : prev.litros,
        preco_litro: litrosMatch ? litrosMatch[2].replace(".", "").replace(",", ".") : prev.preco_litro,
        km: kmMatch ? kmMatch[1] : prev.km,
        hora: horaMatch ? horaMatch[1] : prev.hora,
        origem: "pdf"
      }));

      toast.success("Nota Fiscal importada com sucesso!");
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler o PDF. Verifique se é uma NF-e válida.");
    }'''

    funcao_nova = '''      // Monta o payload para enviar ao backend
      const payload = {
        data: new Date().toISOString().split('T')[0], // Data de hoje se não achar no PDF
        hora: horaMatch ? horaMatch[1] : null,
        numero_nf: nfMatch ? nfMatch[1] : null,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\\s/g, "") : null,
        cnpj: cnpjMatch ? cnpjMatch[1] : null,
        fornecedor: fornecedorMatch ? fornecedorMatch[1].trim() : null,
        placa: placaMatch ? placaMatch[1] : null, // Placa extraída da nota
        litros: litrosMatch ? Number(litrosMatch[1].replace(",", ".")) : 0,
        preco_litro: litrosMatch ? Number(litrosMatch[2].replace(".", "").replace(",", ".")) : 0,
        km: kmMatch ? Number(kmMatch[1]) : 0,
      };

      // Envia para o backend
      await apiPost("/abastecimentos/importar", payload);
      
      toast.success("Nota Fiscal importada e registrada com sucesso!");
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao importar o PDF. Verifique se o veículo está cadastrado.");
    }'''

    if funcao_antiga in conteudo:
        conteudo = conteudo.replace(funcao_antiga, funcao_nova)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Frontend: Função de importação atualizada para chamar a rota do backend.")
    else:
        print("⚠️ A função de importação original não foi encontrada. O arquivo pode ter sido alterado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Rota de Importação de PDF...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    adicionar_rota_importar(raiz)
    atualizar_frontend(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'feat: rota de importacao de PDF'")
    print("git push")

if __name__ == "__main__":
    executar()