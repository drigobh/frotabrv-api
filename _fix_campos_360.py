import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "VeiculoDetalhe.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Função auxiliar para pegar o valor independente do nome do campo
funcao_aux = '''
  // Função para pegar o valor independente do nome do campo (compatibilidade)
  const getVal = (item: any, ...keys: string[]) => {
    for (const k of keys) {
      if (item[k] !== undefined && item[k] !== null) return Number(item[k]) || 0;
    }
    return 0;
  };

  const getStr = (item: any, ...keys: string[]) => {
    for (const k of keys) {
      if (item[k] !== undefined && item[k] !== null && item[k] !== "") return String(item[k]);
    }
    return "";
  };
'''

# Injeta a função logo após a desestruturação de dados
c = c.replace(
    'const financeiro = detalhes?.financeiro || { custo_total: 0, consumo_medio: 0 };',
    'const financeiro = detalhes?.financeiro || { custo_total: 0, consumo_medio: 0 };\n' + funcao_aux
)

# 2. Corrige os KPIs principais para usar a função
c = c.replace('brl(Number(financeiro.custo_total) || 0)', 'brl(financeiro.custo_total || 0)')

# 3. Corrige a exibição da timeline (Abastecimentos)
c = c.replace(
    'Abastecimento · {num(Number(a.litros) || 0, 1)} L',
    'Abastecimento · {num(getVal(a, "litros", "quantidade", "volume"), 1)} L'
)
c = c.replace(
    '{brl(Number(a.valor_total) || 0)}',
    '{brl(getVal(a, "valor_total", "valor", "total", "custo"))}'
)

# 4. Corrige a tabela de abastecimentos
c = c.replace(
    'a.data_abastecimento?.split("-").reverse().slice(0,2).join("/")',
    'getStr(a, "data", "data_abastecimento", "data_emissao").split("-").reverse().slice(0,2).join("/")'
)
c = c.replace(
    'a.data_abastecimento?.split("T")[0].split("-").reverse().join("/") || "—"',
    'getStr(a, "data", "data_abastecimento", "data_emissao").split("T")[0].split("-").reverse().join("/") || "—"'
)
c = c.replace(
    '<td className="px-3 py-3">{num(Number(a.litros) || 0, 1)} L</td>',
    '<td className="px-3 py-3">{num(getVal(a, "litros", "quantidade", "volume"), 1)} L</td>'
)
c = c.replace(
    '<td className="px-3 py-3 font-mono">{brl(Number(a.valor_total) || 0)}</td>',
    '<td className="px-3 py-3 font-mono">{brl(getVal(a, "valor_total", "valor", "total", "custo"))}</td>'
)
c = c.replace(
    '<td className="px-3 py-3 text-right font-mono">{num(Number(a.hodometro_km) || 0)} km</td>',
    '<td className="px-3 py-3 text-right font-mono">{num(getVal(a, "hodometro_km", "km", "hodometro", "odometro"))} km</td>'
)

# 5. Corrige a aba de manutenção
c = c.replace(
    '<td className="px-3 py-3 text-right font-mono">{brl(Number(m.valor) || 0)}</td>',
    '<td className="px-3 py-3 text-right font-mono">{brl(getVal(m, "valor", "valor_total", "custo"))}</td>'
)
c = c.replace(
    '<span className="font-mono text-sm text-slate-300">{brl(Number(m.valor) || 0)}</span>',
    '<span className="font-mono text-sm text-slate-300">{brl(getVal(m, "valor", "valor_total", "custo"))}</span>'
)

# 6. Corrige os pneus (Sulco e Posição)
c = c.replace(
    'Sulco: {p.profundidade_atual || "—"} mm',
    'Sulco: {getVal(p, "profundidade_atual", "sulco_atual", "sulco") || "—"} mm'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Frontend ajustado! Agora ele lê os campos reais do banco (data, valor, etc).")