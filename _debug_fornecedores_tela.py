import os

def diag():
    caminho = os.path.join(os.getcwd(), "frontend", "src", "pages", "Fornecedores.tsx")
    if not os.path.exists(caminho):
        print("❌ Arquivo não encontrado.")
        return

    with open(caminho, "r", encoding="utf-8") as f:
        c = f.read()

    out = []
    
    # 1. Filtros (onde começa e termina a div de filtros)
    idx = c.find('Buscar por Nome')
    if idx != -1:
        start = c.rfind('<div', 0, idx)
        end = c.find('<Table', idx)
        out.append("=== 1. FILTROS ===")
        out.append(c[start:end])

    # 2. Tabela (Header e primeira linha de dados)
    idx = c.find('<TableHeader>')
    if idx != -1:
        out.append("\n=== 2. TABELA (Header e Body) ===")
        out.append(c[idx:idx+2500])

    # 3. Formulário/Modal (onde tem o Nome / Razão Social)
    idx = c.find('Nome / Razão Social')
    if idx != -1:
        start = c.rfind('<div', 0, idx)
        end = c.find('</Dialog>', idx)
        out.append("\n=== 3. FORMULÁRIO (Modal) ===")
        out.append(c[start:end])

    with open("debug_fornecedores_tela.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("✅ Diagnóstico salvo em: debug_fornecedores_tela.txt")

if __name__ == "__main__":
    diag()