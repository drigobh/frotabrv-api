import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Verifica se o Eye está importado
if "Eye" not in c.split("from \"lucide-react\"")[0]:
    # Adiciona o Eye na lista de importações do lucide-react
    c = re.sub(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', r'import {\1, Eye } from "lucide-react";', c, count=1)
    print("✅ Eye adicionado à importação do lucide-react.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx corrigido! O erro do Eye sumiu.")