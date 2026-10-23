import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui a forma como o Frontend lê os números
    padrao = re.compile(
        r'const litrosRaw = Number\(row\[idxLitros\]\.replace\(/\\\./g, ""\)\.replace\(",", "."\)\) / 1000;\s*\n\s*const valorLitroRaw = Number\(row\[idxPreco\]\.replace\(/\\\./g, ""\)\.replace\(",", "."\)\) / 100;',
        re.DOTALL
    )

    novo_bloco = '''const litrosRaw = Number(String(row[idxLitros]).replace(/[^\\d]/g, "")) / 1000;
        const valorLitroRaw = Number(String(row[idxPreco]).replace(/[^\\d]/g, "")) / 100;'''

    if padrao.search(conteudo):
        conteudo = padrao.sub(novo_bloco, conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Leitura de números corrigida! Agora remove tudo que não for dígito.")
    else:
        print("⚠️ Não foi possível encontrar o bloco exato. Tentando substituição direta...")
        conteudo = conteudo.replace(
            'Number(row[idxLitros].replace(/\\./g, "").replace(",", ".")) / 1000',
            'Number(String(row[idxLitros]).replace(/[^\\d]/g, "")) / 1000'
        ).replace(
            'Number(row[idxPreco].replace(/\\./g, "").replace(",", ".")) / 100',
            'Number(String(row[idxPreco]).replace(/[^\\d]/g, "")) / 100'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Substituição direta aplicada.")

if __name__ == "__main__":
    corrigir(os.getcwd())