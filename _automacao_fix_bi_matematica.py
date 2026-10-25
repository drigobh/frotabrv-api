import os

def fix_matematica(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "RelatorioEstoque.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo RelatorioEstoque.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrige a conta da quantidade (remove a margem de +5)
    c = c.replace(
        "const qtdComprar = p.estoque_minimo - p.quantidade_estoque + 5;",
        "const qtdComprar = p.estoque_minimo - p.quantidade_estoque;"
    )
    
    # 2. Corrige a conta do custo estimado (só calcula se qtdComprar for maior que zero)
    c = c.replace(
        "const custoEstimado = fornecedorBarato ? fornecedorBarato.preco_atual * qtdComprar : 0;",
        "const custoEstimado = fornecedorBarato && qtdComprar > 0 ? fornecedorBarato.preco_atual * qtdComprar : 0;"
    )
    
    # 3. Muda o filtro para não listar peças que estão EXATAMENTE no mínimo (pois não precisam comprar)
    c = c.replace(
        "p.quantidade_estoque <= p.estoque_minimo",
        "p.quantidade_estoque < p.estoque_minimo"
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Relatório corrigido com sucesso! Sugestão de compra agora é exata.")

if __name__ == "__main__":
    fix_matematica(os.getcwd())