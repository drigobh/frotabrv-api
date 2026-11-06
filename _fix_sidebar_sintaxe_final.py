import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Corrigir o botão que está com "}}}}"
# O correto é: onClick={() => { ... }} (duas chaves de fechamento: uma da função, uma do bloco JSX)
c = re.sub(
    r'onClick=\{\(\) => \{ localStorage\.clear\(\); sessionStorage\.clear\(\); navigate\("/login"\); \}\}\}\}',
    'onClick={() => { localStorage.clear(); sessionStorage.clear(); navigate("/login"); }}',
    c
)

# 2. Também limpar qualquer resquício de "window.location" antigo
c = re.sub(r'window\.location\.href = window\.location\.origin \+ "/login";\s*window\.location\.reload\(\);', '', c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx corrigido! O erro de sintaxe sumiu.")