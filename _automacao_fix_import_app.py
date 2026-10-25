import os

def fix_imports(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que o import do RelatorioFornecedores existe
    if 'import RelatorioFornecedores' not in c:
        c = c.replace(
            'import Login from "@/pages/Login";',
            'import Login from "@/pages/Login";\nimport RelatorioFornecedores from "@/pages/RelatorioFornecedores";'
        )
        print("✅ Import do RelatorioFornecedores adicionado.")

    # 2. Garantir que o import do Acoplamentos existe
    if 'import Acoplamentos' not in c:
        c = c.replace(
            'import Login from "@/pages/Login";',
            'import Login from "@/pages/Login";\nimport Acoplamentos from "@/pages/Acoplamentos";'
        )
        print("✅ Import do Acoplamentos adicionado.")

    # 3. Verificar se as rotas estão usando os componentes corretos
    if '<RelatorioFornecedores />' not in c:
        print("⚠️ A rota /relatorios/fornecedores não está renderizando o componente. Verifique manualmente.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ App.tsx corrigido.")

if __name__ == "__main__":
    fix_imports(os.getcwd())