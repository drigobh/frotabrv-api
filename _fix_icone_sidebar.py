import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Verifica se o BellRing está importado (no bloco de importação do lucide-react)
if "BellRing" not in c.split("from \"lucide-react\"")[0]:
    # Procura o bloco de importação do lucide-react e adiciona o BellRing lá dentro
    c = re.sub(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', r'import {\1, BellRing } from "lucide-react";', c, count=1)
    print("✅ BellRing adicionado ao bloco de importação do lucide-react.")
else:
    print("ℹ️ BellRing já estava importado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar.tsx corrigido! Salve e o Vite vai recarregar na hora.")