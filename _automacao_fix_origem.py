import os
import re

def fix_models(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Libera o campo origem para aceitar qualquer string, evitando erros 422 futuros
    c = c.replace('origem: Literal["manual", "pdf", "excel"] = "manual"', 'origem: str = "manual"')
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Validação rígida do campo 'origem' removida.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que o formulário manual inicie como "manual"
    # O script anterior trocou para "bsoft" no estado inicial. Vamos reverter.
    c = c.replace('fornecedor: "", origem: "bsoft", produto: "DIESEL"', 'fornecedor: "", origem: "manual", produto: "DIESEL"')
    c = c.replace('fornecedor: "", origem: "excel", produto: "DIESEL"', 'fornecedor: "", origem: "manual", produto: "DIESEL"')
    
    # 2. Garantir que o salvar envie o que está no form (que agora será "manual" por padrão)
    if 'const payload = { ...form,' not in c:
        # Se por algum motivo o payload estava hardcoded, corrige
        c = c.replace('origem: "bsoft"', 'origem: form.origem || "manual"')

    # 3. Corrigir as importações para enviarem o valor exato
    # BSoft
    c = re.sub(r'(const handleImportXLS[\s\S]*?)origem:\s*"manual"', r'\1origem: "bsoft"', c)
    c = re.sub(r'(const handleImportXLS[\s\S]*?)origem:\s*"excel"', r'\1origem: "bsoft"', c)
    
    # Edenred
    c = re.sub(r'(const handleImportEdenred[\s\S]*?)origem:\s*"manual"', r'\1origem: "edenred"', c)
    c = re.sub(r'(const handleImportEdenred[\s\S]*?)origem:\s*"excel"', r'\1origem: "edenred"', c)
    c = re.sub(r'(const handleImportEdenred[\s\S]*?)origem:\s*"bsoft"', r'\1origem: "edenred"', c)

    # PDF
    c = re.sub(r'(const handleImportPDF[\s\S]*?)origem:\s*"manual"', r'\1origem: "pdf"', c)
    c = re.sub(r'(const handleImportPDF[\s\S]*?)origem:\s*"excel"', r'\1origem: "pdf"', c)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Origens corrigidas (Manual=manual, BSoft=bsoft, Edenred=edenred, PDF=pdf).")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_models(raiz)
    fix_frontend(raiz)