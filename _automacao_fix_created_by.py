import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontra a função importar_pdf e adiciona o created_by no doc
    padrao = re.compile(
        r'("created_at": now_iso\(\)\s*\n\s*\})',
        re.DOTALL
    )
    
    if not padrao.search(conteudo):
        print("❌ Não foi possível encontrar o bloco 'created_at' para adicionar o created_by.")
        return

    # Adiciona o created_by antes do created_at
    novo = '"created_by": user.get("id", "sistema"),\n        "created_at": now_iso()\n    }'
    conteudo = padrao.sub(novo, conteudo)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Campo 'created_by' adicionado com sucesso!")

if __name__ == "__main__":
    corrigir(os.getcwd())