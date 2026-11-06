import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "ChassiMapa.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Alterar a cor do texto do pneu (de cinza para branco)
c = c.replace('text-slate-400', 'text-white')
c = c.replace('text-slate-500', 'text-white/70')

# 2. Alterar a cor dos dados do pneu (de cinza para azul claro)
c = c.replace('text-slate-300', 'text-sky-300')
c = c.replace('text-slate-200', 'text-sky-300 font-bold')

# 3. Garantir que o número de fogo tenha destaque
c = re.sub(r'className="text-xs text-white"', 'className="text-xs text-sky-300 font-bold"', c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ ChassiMapa.tsx: Cores ajustadas (branco/azul claro).")