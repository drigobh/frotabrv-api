import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Verifica se as constantes existem
if "const STATUS_PNEU" not in c and "const TIPOS_PNEU" not in c:
    # Insere as constantes antes da função parseDate
    constantes = '''
const STATUS_PNEU = ["Estoque", "Aplicado", "Recapagem", "Conserto", "Sucateado"];
const TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda", "Liso", "Borrachudo"];

'''
    c = c.replace("const parseDate", constantes + "const parseDate")
    print("✅ Constantes STATUS_PNEU e TIPOS_PNEU reinseridas.")
else:
    print("ℹ️ As constantes já existem no arquivo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Pneus.tsx corrigido! O erro de TIPOS_PNEU sumiu.")