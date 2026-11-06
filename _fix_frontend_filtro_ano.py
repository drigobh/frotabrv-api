import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Financeiro.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adicionar a opção "Todos os Meses" no select
c = c.replace(
    '{MESES.map((m, i) => <option key={m} value={i+1}>{m}</option>)}',
    '<option value={0}>Todos os Meses</option>\n          {MESES.map((m, i) => <option key={m} value={i+1}>{m}</option>)}'
)

# 2. Ajustar o estado inicial para "Todos os Meses" (0)
c = c.replace(
    'const [mesFiltro, setMesFiltro] = useState(new Date().getMonth() + 1);',
    'const [mesFiltro, setMesFiltro] = useState(0);'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Frontend: Opção 'Todos os Meses' adicionada ao filtro.")