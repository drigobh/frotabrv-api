import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "LeitorQRCode.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Substituir a chamada da rota errada pela rota de detalhes 360º
c = c.replace(
    'const v = await apiGet<any>(`/veiculos/${res.veiculo_id}`);',
    'const v = await apiGet<any>(`/veiculos/detalhes/${res.veiculo_id}`);'
)

# A rota de detalhes retorna um objeto com { veiculo, ... }, então precisamos extrair
c = c.replace(
    'setVeiculo(v);',
    'setVeiculo(v.veiculo || v);'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ LeitorQRCode.tsx: Rota de veículo corrigida para /veiculos/detalhes/{id}.")