import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "AppLayout.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove todas as importações do useMe
c = re.sub(r'import\s+\{\s*useMe\s*\}\s+from\s+"@/hooks/useSession";\n?', '', c)

# Adiciona apenas uma importação no topo (após os imports do React)
c = 'import { useMe } from "@/hooks/useSession";\n' + c

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ AppLayout.tsx corrigido: import do useMe duplicado removido.")