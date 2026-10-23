import os

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adiciona a busca do motorista e corrige a origem
    if "async def importar_pdf" in conteudo:
        # Busca o acoplamento ativo
        busca_motorista = '''
    # Busca o acoplamento ativo para pegar o motorista
    acoplamento = await db.acoplamentos.find_one(
        {"veiculo_id": veiculo["id"], "ativo": True},
        {"_id": 0}
    )
    motorista_id = acoplamento.get("motorista_id") if acoplamento else None
    motorista_label = None
    if motorista_id:
        mot = await db.motoristas.find_one({"id": motorista_id}, {"_id": 0})
        motorista_label = mot["nome"] if mot else None

    doc = {
        "id": str(uuid.uuid4()),'''
        
        conteudo = conteudo.replace('doc = {\n        "id": str(uuid.uuid4()),', busca_motorista)
        
        # Substitui os campos do motorista no doc
        conteudo = conteudo.replace(
            '"motorista_id": None,\n        "motorista_label": None,',
            '"motorista_id": motorista_id,\n        "motorista_label": motorista_label,'
        )
        
        # Muda a origem para 'excel' se vier da planilha
        conteudo = conteudo.replace(
            '"origem": "pdf",',
            '"origem": body.get("origem", "excel"),'
        )
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Backend: Motorista e Origem corrigidos.")
    else:
        print("❌ Backend: Função importar_pdf não encontrada.")

if __name__ == "__main__":
    corrigir(os.getcwd())