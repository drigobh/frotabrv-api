import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Procura a função importar_pdf e substitui a busca do veículo para ignorar o _id
    # O erro está na linha: veiculo = await db.veiculos.find_one({"placa": placa_limpa})
    # Precisamos adicionar {"_id": 0}
    
    padrao = re.compile(
        r'veiculo = await db\.veiculos\.find_one\(\{"placa": placa_limpa\}\)',
        re.DOTALL
    )
    
    novo = 'veiculo = await db.veiculos.find_one({"placa": placa_limpa}, {"_id": 0})'
    
    if padrao.search(conteudo):
        conteudo = padrao.sub(novo, conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Erro corrigido: a busca do veículo agora ignora o _id.")
    else:
        # Tenta uma alternativa (caso o padrão exato não bata)
        if 'find_one({"placa": placa_limpa})' in conteudo:
            conteudo = conteudo.replace(
                'find_one({"placa": placa_limpa})',
                'find_one({"placa": placa_limpa}, {"_id": 0})'
            )
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print("✅ Erro corrigido (fallback).")
        else:
            print("⚠️ Não foi possível encontrar a linha exata. Verifique se a função importar_pdf existe.")

if __name__ == "__main__":
    corrigir(os.getcwd())