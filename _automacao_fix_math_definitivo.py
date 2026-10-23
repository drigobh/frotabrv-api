import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Remove a divisão por 1000 e por 100, pois o Frontend já faz isso
    padrao = re.compile(
        r'litros_corrigidos = \(body\.get\("litros"\) or 0\) / 1000\s*\n\s*preco_corrigido = \(body\.get\("preco_litro"\) or 0\) / 100',
        re.DOTALL
    )

    if padrao.search(conteudo):
        novo_bloco = '''litros_corrigidos = body.get("litros") or 0
    preco_corrigido = body.get("preco_litro") or 0'''
        
        conteudo = padrao.sub(novo_bloco, conteudo)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Divisão dupla removida! A matemática agora usará os valores exatos do Frontend.")
    else:
        print("⚠️ Não foi possível encontrar o bloco de divisão exata. Tentando substituição direta...")
        
        # Fallback mais agressivo caso o Regex falhe
        conteudo = conteudo.replace(
            '(body.get("litros") or 0) / 1000',
            'body.get("litros") or 0'
        ).replace(
            '(body.get("preco_litro") or 0) / 100',
            'body.get("preco_litro") or 0'
        )
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Substituição direta aplicada.")

if __name__ == "__main__":
    corrigir(os.getcwd())