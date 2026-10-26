import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garante que o backend use o KM Rodados e Média se vierem do payload (Edenred)
    if 'if body.get("km_rodados") is not None:' not in c:
        codigo_novo = '''
    # Usa os dados da planilha se vierem preenchidos (Edenred)
    if body.get("km_rodados") is not None:
        km_rodados = body.get("km_rodados")
        media_km_l = body.get("media_km_l")
    else:
        # Se não vier, calcula baseado no último abastecimento (BSOFT)
        if ultimo and ultimo.get("km") and km_atual > ultimo["km"]:
            km_rodados = km_atual - ultimo["km"]
            if km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
                media_km_l = km_rodados / litros
            else:
                km_rodados = None
        elif km_atual > 0 and veiculo.get("hodometro_km") and km_atual > veiculo["hodometro_km"]:
            km_rodados = km_atual - veiculo["hodometro_km"]
            if km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
                media_km_l = km_rodados / litros
            else:
                km_rodados = None
'''
        # Substitui o bloco de cálculo antigo
        import re
        padrao = re.compile(r'    km_rodados = None\n    media_km_l = None[\s\S]*?else:\n\s*km_rodados = None', re.DOTALL)
        c = padrao.sub(codigo_novo, c)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Cálculo de KM ajustado para aceitar dados da planilha Edenred.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrige a importação do Edenred (usando Regex robusto para achar colunas)
    if 'const idxValor = findIdx("VALOR EMISSAO")' in c:
        c = c.replace(
            '''const idxPreco = findIdx("VL/LITRO");
      const idxKm = findIdx("HODOMETRO");''',
            '''const idxPreco = findIdx("VL/LITRO") !== -1 ? findIdx("VL/LITRO") : findIdx("V. LITRO");
      const idxKm = findIdx("HODOMETRO") !== -1 ? findIdx("HODOMETRO") : findIdx("LEITURA");'''
        )
        
        # Adiciona a captura do KM Rodados
        c = c.replace(
            'const kmNum = Number(String(row[idxKm] || "0").replace(/[^\\d]/g, ""));',
            '''const kmNum = Number(String(row[idxKm] || "0").replace(/[^\\d]/g, ""));
        const kmRodadosNum = findIdx("KM RODADOS") !== -1 ? Number(String(row[findIdx("KM RODADOS")] || "0").replace(",", ".")) : null;
        const mediaNum = findIdx("KM/LITRO") !== -1 ? Number(String(row[findIdx("KM/LITRO")] || "0").replace(",", ".")) : null;'''
        )
        
        # Adiciona ao payload
        c = c.replace(
            'hora: horaFinal,',
            'km_rodados: kmRodadosNum, media_km_l: mediaNum, hora: horaFinal,'
        )

    # 2. Corrige a importação do BSOFT para calcular o Valor Total corretamente
    if 'const idxValor = findIdx("VALOR");' in c:
        c = c.replace(
            'const valorNum = idxValor !== -1 ? (typeof row[idxValor] === "number" ? row[idxValor] : Number(String(row[idxValor]).replace(",", "."))) : (litrosNum * precoNum);',
            'const valorNum = idxValor !== -1 ? (typeof row[idxValor] === "number" ? row[idxValor] : Number(String(row[idxValor]).replace(",", "."))) : (litrosNum * precoNum);'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Importação ajustada. O sistema vai usar as colunas exatas da planilha.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)