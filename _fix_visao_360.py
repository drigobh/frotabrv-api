import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "VeiculoDetalhe.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Muda o título para Visão 360º sempre
c = c.replace(
    'title={veiculo ? `${veiculo.placa} · ${veiculo.modelo}` : "Carregando..."}',
    'title={veiculo ? `${veiculo.placa} · ${veiculo.modelo}` : "Visão 360º do Veículo"}'
)

# 2. Se o veículo não carregar, coloca um subtítulo amigável
c = c.replace(
    'description="Visão 360º do veículo: custo, consumo, manutenção e pneus."',
    'description={veiculo ? `Placa: ${veiculo.placa} · Ano: ${veiculo.ano || "—"} · Chassi: ${veiculo.template_chassi_id || "—"}` : "Buscando histórico completo no banco de dados..."}'
)

# 3. Para o cabeçalho não ficar com a cara de "erro", adicionamos um esqueleto de loading bonito
# Mas como isso exige reescrever a estrutura, vamos apenas garantir que o Título seja Visão 360.
with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Frontend: Título mudado para 'Visão 360º do Veículo'.")