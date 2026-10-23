import os

def verificar(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Procura a função importar_pdf e verifica se tem o "_id": 0
    if '"placa": placa_limpa}, {"_id": 0}' in conteudo:
        print("✅ A correção do _id JÁ ESTÁ no arquivo local.")
    else:
        print("❌ A correção do _id NÃO está no arquivo local. O script anterior falhou.")

if __name__ == "__main__":
    verificar(os.getcwd())