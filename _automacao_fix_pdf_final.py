import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Remove a trava de 5000 km para permitir o cálculo e mostrar que os dados entraram
    c = c.replace('if km_rodados < 0 or km_rodados > 5000:', 'if km_rodados < 0:')
    c = c.replace('elif km_rodados == 0:', 'elif km_rodados == 0:')
    
    # Atualiza a validação de Arla
    c = c.replace('if km_rodados is not None:\n        if km_rodados < 0:\n            km_rodados = None # Ignora valores absurdos ou negativos\n        elif km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():', 
                  'if km_rodados is not None:\n        if km_rodados < 0:\n            km_rodados = None\n        elif km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend atualizado (trava de 5000km removida).")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Ajuste do Regex do Posto (para na vírgula) e Produto (para no primeiro número)
    c = c.replace(
        'const postoMatch = text.match(/RECEBEMOS DE\\s+([A-Z0-9\\s\\-.]+)\\s*\\(/i) || text.match(/RECEBEMOS DE\\s+([A-Z0-9\\s\\-.]+)/i);',
        'const postoMatch = text.match(/RECEBEMOS DE\\s+([^,]+)/i);'
    )
    c = c.replace(
        'const produtoMatch = text.match(/(OLEO DIESEL[A-Z0-9\\s]*|DIESEL[A-Z0-9\\s]*|ARLA[A-Z0-9\\s]*)/i);',
        'const produtoMatch = text.match(/(OLEO DIESEL[^\\d]*|DIESEL[^\\d]*|ARLA[^\\d]*)/i);'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado (Regex de Posto e Produto corrigidos).")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)