import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Garantir que o useNavigate está importado
if "useNavigate" not in c:
    c = c.replace(
        'import { Link, useLocation } from "react-router-dom";',
        'import { Link, useLocation, useNavigate } from "react-router-dom";'
    )
    print("✅ useNavigate importado.")

# 2. Adicionar a função navigate no componente
if "const navigate = useNavigate();" not in c:
    match_comp = re.search(r'(export function Sidebar\(\)\s*\{)', c)
    if match_comp:
        c = c.replace(match_comp.group(1), match_comp.group(1) + "\n  const navigate = useNavigate();")
        print("✅ navigate adicionado ao componente.")

# 3. Encontrar o botão "Sair" e substituir o onClick
# O botão tem o ícone LogOut e o texto "Sair". Vamos procurar por ele.
padrao_sair = r'(<Button[^>]*onClick=\{[^}]*\}[^>]*>[\s\S]*?<LogOut[^>]*/>[\s\S]*?Sair[\s\S]*?</Button>)'

match = re.search(padrao_sair, c)
if match:
    botao_original = match.group(1)
    # Substitui o onClick por uma função que limpa o localStorage e navega
    botao_novo = re.sub(
        r'onClick=\{[^}]*\}',
        'onClick={() => { localStorage.clear(); sessionStorage.clear(); navigate("/login"); }}',
        botao_original
    )
    c = c.replace(botao_original, botao_novo)
    print("✅ Botão Sair atualizado com logout via navigate.")
else:
    # Fallback: procura qualquer Button que tenha "Sair" no texto
    padrao_fallback = r'(<Button[^>]*>[\s\S]*?Sair[\s\S]*?</Button>)'
    match_fb = re.search(padrao_fallback, c)
    if match_fb:
        botao_original = match_fb.group(1)
        botao_novo = re.sub(
            r'onClick=\{[^}]*\}',
            'onClick={() => { localStorage.clear(); sessionStorage.clear(); navigate("/login"); }}',
            botao_original
        )
        c = c.replace(botao_original, botao_novo)
        print("✅ Botão Sair atualizado (fallback).")
    else:
        print("⚠️ Botão Sair ainda não encontrado. Verifique o arquivo Sidebar.tsx.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx corrigido!")