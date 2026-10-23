import os

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Procura a função importar_pdf e adiciona a busca do motorista
    if "async def importar_pdf" in conteudo:
        # Encontra onde o doc é criado e insere a busca do motorista
        padrao = 'doc = {\n        "id": str(uuid.uuid4()),'
        
        # Busca o acoplamento ativo para o veículo
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
        
        if padrao in conteudo:
            conteudo = conteudo.replace(padrao, busca_motorista)
            
            # Adiciona os campos do motorista no doc
            conteudo = conteudo.replace(
                '"motorista_id": None,\n        "motorista_label": None,',
                f'"motorista_id": motorista_id,\n        "motorista_label": motorista_label,'
            )
            
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print("✅ Backend: Busca de motorista adicionada.")
        else:
            print("⚠️ Backend: Bloco 'doc = {' não encontrado.")
    else:
        print("❌ Backend: Função importar_pdf não encontrada.")

if __name__ == "__main__":
    corrigir(os.getcwd())