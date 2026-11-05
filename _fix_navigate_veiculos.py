import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Veiculos.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Garantir que o import do useNavigate está lá
if "useNavigate" not in c:
    c = c.replace('import { useQuery } from "@tanstack/react-query";', 'import { useNavigate } from "react-router-dom";\nimport { useQuery } from "@tanstack/react-query";')
    print("✅ Import de useNavigate adicionado.")

# 2. Garantir que o import do Eye (do lucide) e do Button estão lá
if "Eye" not in c:
    c = c.replace('import { num } from "@/lib/format";', 'import { Eye } from "lucide-react";\nimport { Button } from "@/components/ui/button";\nimport { num } from "@/lib/format";')
    print("✅ Imports do Eye e Button adicionados.")

# 3. Injetar a declaração 'const navigate = useNavigate();' logo no início do componente
# Procura a função 'export default function Veiculos() {'
match_func = re.search(r'(export default function Veiculos\(\)\s*\{)', c)
if match_func:
    if "const navigate = useNavigate();" not in c:
        c = c.replace(match_func.group(1), match_func.group(1) + "\n  const navigate = useNavigate();")
        print("✅ Declaração 'const navigate = useNavigate();' injetada.")
    else:
        print("ℹ️ A variável navigate já estava declarada.")
else:
    print("⚠️ Não foi possível encontrar a função Veiculos(). Verifique se o nome do componente é diferente.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Script finalizado! O erro deve sumir no VS Code.")