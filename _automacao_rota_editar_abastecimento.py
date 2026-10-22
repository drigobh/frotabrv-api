import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_rota_edit_abast_{agora}.zip"
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

def adicionar_rotas(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Adiciona a rota PUT (Editar)
    rota_put = '''
@router.put("/{abastecimento_id}", response_model=Abastecimento)
async def editar(abastecimento_id: str, body: AbastecimentoCreate, request: Request, user: dict = Depends(require("write"))):
    atual = await db.abastecimentos.find_one({"id": abastecimento_id})
    if not atual:
        raise HTTPException(404, "Abastecimento não encontrado")

    veiculo = await db.veiculos.find_one({"id": body.veiculo_id})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    motorista_label = None
    if body.motorista_id:
        motorista = await db.motoristas.find_one({"id": body.motorista_id})
        if motorista:
            motorista_label = motorista["nome"]

    # Recalcula o KM rodados (considerando o abastecimento anterior, excluindo o atual)
    anterior = await db.abastecimentos.find_one(
        {"veiculo_id": body.veiculo_id, "km": {"$lt": body.km}, "id": {"$ne": abastecimento_id}},
        sort=[("km", -1)]
    )
    km_anterior = anterior["km"] if anterior else veiculo.get("hodometro_km", 0)
    km_rodados = body.km - km_anterior if km_anterior > 0 else None
    media_km_l = km_rodados / body.litros if km_rodados and body.litros > 0 else None
    valor_total = body.litros * body.preco_litro

    dados_atualizados = {
        **body.model_dump(),
        "valor_total": round(valor_total, 2),
        "km_rodados": km_rodados,
        "media_km_l": round(media_km_l, 2) if media_km_l else None,
        "veiculo_label": f"{veiculo['placa']} - {veiculo.get('modelo', '')}",
        "motorista_label": motorista_label,
    }

    await db.abastecimentos.update_one({"id": abastecimento_id}, {"$set": dados_atualizados})
    await audit(user, "editar", "abastecimentos", abastecimento_id, f"Veículo: {dados_atualizados['veiculo_label']}", request)
    
    # Busca o documento atualizado para retornar
    doc_atualizado = await db.abastecimentos.find_one({"id": abastecimento_id}, {"_id": 0})
    return Abastecimento(**doc_atualizado)

@router.delete("/{abastecimento_id}", status_code=204)
async def excluir(abastecimento_id: str, request: Request, user: dict = Depends(require("write"))):
    atual = await db.abastecimentos.find_one({"id": abastecimento_id})
    if not atual:
        raise HTTPException(404, "Abastecimento não encontrado")
    
    await db.abastecimentos.delete_one({"id": abastecimento_id})
    await audit(user, "excluir", "abastecimentos", abastecimento_id, f"Veículo: {atual.get('veiculo_label')}", request)
    return None
'''

    # Insere as rotas antes do último "return" (ou no final do arquivo)
    if "@router.put" not in conteudo:
        # Adiciona no final do arquivo
        conteudo += rota_put
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Rotas PUT (Editar) e DELETE (Excluir) adicionadas ao backend.")
    else:
        print("ℹ️ As rotas de edição já existem no backend.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Rotas de Edição...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    adicionar_rotas(raiz)

    print("\n🚀 Automação concluída! Faça o push para o Render:")
    print("1. git add .")
    print("2. git commit -m 'feat: rotas de editar e excluir abastecimento'")
    print("3. git push")

if __name__ == "__main__":
    executar()