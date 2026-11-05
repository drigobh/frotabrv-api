import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Renomeia os botões das abas no topo
c = c.replace('Wrench className="size-4 inline mr-2" /> Manutenção', 'Wrench className="size-4 inline mr-2" /> Borracharia')
c = c.replace('RefreshCw className="size-4 inline mr-2" /> Estoque / Sucata', 'RefreshCw className="size-4 inline mr-2" /> Estoque x Envio')

# 2. Renomeia os títulos internos das telas
c = c.replace('Pneus na Oficina (Manutenção)', 'Pneus na Borracharia')
c = c.replace('Pneus Disponíveis (Estoque)', 'Pneus Disponíveis (Estoque x Envio)')

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Abas renomeadas para 'Borracharia' e 'Estoque x Envio'!")