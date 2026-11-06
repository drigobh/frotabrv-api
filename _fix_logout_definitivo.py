import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove qualquer lógica de logout antiga
c = re.sub(r'onClick=\{\(\) => \{.*?localStorage.*?\}\}', 'onClick={() => {}}', c)

# 2. Adiciona a função de logout no início do componente
if "const handleLogout" not in c:
    match_comp = re.search(r'(export function Sidebar\(\)\s*\{)', c)
    if match_comp:
        c = c.replace(match_comp.group(1), match_comp.group(1) + """
  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/login";
  };
""")

# 3. Substitui o onClick do botão Sair para usar a função handleLogout
c = re.sub(
    r'(<Button[^>]*>[\s\S]*?Sair[\s\S]*?</Button>)',
    lambda m: re.sub(r'onClick=\{[^}]*\}', 'onClick={handleLogout}', m.group(0)),
    c
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Botão Sair refeito com handleLogout (limpa tudo e recarrega).")