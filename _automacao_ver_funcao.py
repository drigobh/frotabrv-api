import os

def ver(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Mostra da linha 30 até o final da função importar_pdf
    inicio = -1
    for i, linha in enumerate(linhas):
        if "async def importar_pdf" in linha:
            inicio = i
            break

    if inicio == -1:
        print("❌ Função importar_pdf não encontrada.")
        return

    fim = -1
    for i in range(inicio + 1, len(linhas)):
        if linhas[i].strip().startswith("@router"):
            fim = i
            break
    if fim == -1:
        fim = len(linhas)

    for i in range(inicio, fim):
        print(f"{i+1}: {linhas[i].rstrip()}")

if __name__ == "__main__":
    ver(os.getcwd())