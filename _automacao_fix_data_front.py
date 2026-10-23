import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Corrige a conversão de data no handleImportXLS
    padrao = re.compile(
        r'let dataStr = String\(row\[idxData\]\)\.trim\(\);\s*\n\s*if \(dataStr\.includes\("/"\)\) \{\s*\n\s*const \[d, m, y\] = dataStr\.split\("/"\);\s*\n\s*dataStr = `\$\{y\}-\$\{m\}-\$\{d\}`;\s*\n\s*\}',
        re.DOTALL
    )

    novo_bloco = '''let dataStr = String(row[idxData]).trim();
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }'''

    if padrao.search(conteudo):
        conteudo = padrao.sub(novo_bloco, conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Conversão de data corrigida no Frontend.")
    else:
        print("⚠️ Bloco de conversão de data não encontrado (pode já estar correto).")

if __name__ == "__main__":
    corrigir(os.getcwd())