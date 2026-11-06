import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove qualquer resquício do script de logout malformado
# Procura o trecho quebrado "}}}" e o bloco do onClick antigo
c = re.sub(r'window\.location\.href = window\.location\.origin \+ "/login";\s*window\.location\.reload\(\);\s*\}\}', '', c)
c = re.sub(r'onClick=\{\(\) => \{\s*localStorage\.clear\(\);\s*sessionStorage\.clear\(\);\s*\}', 'onClick={() => { localStorage.clear(); sessionStorage.clear(); navigate("/login"); }}', c)
c = re.sub(r'\}\}\}>', '}>', c)  # Corrige o fechamento errado da tag

# 2. Garantir que o useNavigate está importado
if "useNavigate" not in c:
    c = c.replace(
        'import { Link, useLocation } from "react-router-dom";',
        'import { Link, useLocation, useNavigate } from "react-router-dom";'
    )

# 3. Adicionar o useNavigate dentro do componente
if "const navigate = useNavigate();" not in c:
    # Procura a função do componente
    match_comp = re.search(r'(export function Sidebar\(\)\s*\{)', c)
    if match_comp:
        c = c.replace(match_comp.group(1), match_comp.group(1) + "\n  const navigate = useNavigate();")

# 4. Substituir o onClick do botão Sair para usar o navigate
# Procura o botão que tem o texto "Sair" ou o ícone LogOut
padrao_sair = r'onClick=\{\(\) => \{.*?localStorage.*?\}\}'
if re.search(padrao_sair, c):
    c = re.sub(padrao_sair, 'onClick={() => { localStorage.clear(); sessionStorage.clear(); navigate("/login"); }}', c)
    print("✅ Sidebar: Botão Sair corrigido para usar navigate (sem loop).")
else:
    print("⚠️ Botão Sair não encontrado. Verifique o arquivo Sidebar.tsx.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx corrigido! O erro de sintaxe sumiu.")