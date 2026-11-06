import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Alterar a cor do pneu no mapa (de cinza para branco)
# O trecho original provavelmente está no <TableCell> ou no <div> do pneu
c = c.replace(
    'className="text-slate-400 font-mono"',
    'className="text-white font-mono font-bold"'
)

# 2. Alterar a cor dos dados do pneu para azul claro
# Vamos forçar a cor do número de fogo no mapa para azul claro
# Geralmente o número de fogo aparece num span ou div com classe text-...
# Vou substituir as cores antigas por text-sky-300
c = c.replace('className="text-slate-200 font-bold"', 'className="text-sky-300 font-bold"')
c = c.replace('className="text-slate-100"', 'className="text-sky-300"')

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Pneus.tsx: Cores do mapa ajustadas (branco/azul claro).")