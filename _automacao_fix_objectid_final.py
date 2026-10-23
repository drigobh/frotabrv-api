import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontra o bloco do insert_one seguido do return doc na função importar_pdf
    padrao = re.compile(
        r'(await db\.abastecimentos\.insert_one\(doc\)\s*\n\s*)return doc',
        re.DOTALL
    )

    if not padrao.search(conteudo):
        print("❌ Não foi possível encontrar o bloco 'insert_one(doc) ... return doc'.")
        return

    # Substitui por: inserir, remover o _id e retornar
    novo = r'\1doc.pop("_id", None)\n    return doc'
    conteudo = padrao.sub(novo, conteudo)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Correção aplicada: o _id é removido antes de retornar.")

if __name__ == "__main__":
    corrigir(os.getcwd())