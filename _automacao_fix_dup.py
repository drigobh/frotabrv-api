import os

def corrigir(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        linhas = f.readlines()

    # Procura a primeira ocorrência de "const ranking = useMemo"
    primeira_ocorrencia = -1
    for i, linha in enumerate(linhas):
        if "const ranking = useMemo" in linha:
            primeira_ocorrencia = i
            break

    if primeira_ocorrencia == -1:
        print("❌ 'ranking' não encontrado.")
        return

    # Procura a segunda ocorrência
    segunda_ocorrencia = -1
    for i in range(primeira_ocorrencia + 1, len(linhas)):
        if "const ranking = useMemo" in linha:
            segunda_ocorrencia = i
            break

    if segunda_ocorrencia == -1:
        print("ℹ️ Não há duplicata. O arquivo já está correto.")
        return

    # Remove a segunda ocorrência (e o bloco dela até o próximo "}, [rowsComCalculo]);")
    inicio_bloco = segunda_ocorrencia
    fim_bloco = -1
    for i in range(inicio_bloco, len(linhas)):
        if "}, [rowsComCalculo]);" in linhas[i]:
            fim_bloco = i
            break

    if fim_bloco == -1:
        print("⚠️ Não foi possível encontrar o fim do bloco duplicado.")
        return

    # Remove as linhas do bloco duplicado
    novas_linhas = linhas[:inicio_bloco] + linhas[fim_bloco+1:]

    with open(caminho, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    print("✅ Declaração duplicada de 'ranking' removida.")

if __name__ == "__main__":
    corrigir(os.getcwd())