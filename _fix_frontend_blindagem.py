import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "VeiculoDetalhe.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Corrige a exibição dos abastecimentos na Aba "Visão Geral"
c = c.replace(
    '<p className="text-sm text-slate-200">Abastecimento · {num(a.litros, 1)} L</p>',
    '<p className="text-sm text-slate-200">Abastecimento · {num(Number(a.litros) || 0, 1)} L</p>'
)
c = c.replace(
    '<span className="font-mono text-sm text-slate-300">{brl(a.valor_total)}</span>',
    '<span className="font-mono text-sm text-slate-300">{brl(Number(a.valor_total) || 0)}</span>'
)

# 2. Corrige a exibição na Aba "Abastecimentos"
c = c.replace(
    '<td className="px-3 py-3">{num(a.litros, 1)} L</td>',
    '<td className="px-3 py-3">{num(Number(a.litros) || 0, 1)} L</td>'
)
c = c.replace(
    '<td className="px-3 py-3 font-mono">{brl(a.valor_total)}</td>',
    '<td className="px-3 py-3 font-mono">{brl(Number(a.valor_total) || 0)}</td>'
)
c = c.replace(
    '<td className="px-3 py-3 text-right font-mono">{num(a.hodometro_km)} km</td>',
    '<td className="px-3 py-3 text-right font-mono">{num(Number(a.hodometro_km) || 0)} km</td>'
)

# 3. Corrige a exibição na Aba "Manutenção" (valor da OS)
c = c.replace(
    '<td className="px-3 py-3 text-right font-mono">{brl(m.valor)}</td>',
    '<td className="px-3 py-3 text-right font-mono">{brl(Number(m.valor) || 0)}</td>'
)
c = c.replace(
    '<span className="font-mono text-sm text-slate-300">{brl(m.valor)}</span>',
    '<span className="font-mono text-sm text-slate-300">{brl(Number(m.valor) || 0)}</span>'
)

# 4. Corrige os KPIs principais (Custo Total, Consumo, etc)
c = c.replace(
    '{brl(financeiro.custo_total)}',
    '{brl(Number(financeiro.custo_total) || 0)}'
)

# 5. Garante que a data não quebre se vier vazia
c = c.replace(
    'a.data_abastecimento?.split("-").reverse().slice(0,2).join("/")',
    '(a.data_abastecimento || "").split("-").reverse().slice(0,2).join("/") || "—"'
)
c = c.replace(
    'a.data_abastecimento?.split("T")[0].split("-").reverse().join("/") || "—"',
    '(a.data_abastecimento || "").split("T")[0].split("-").reverse().join("/") || "—"'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Frontend blindado contra campos nulos!")
print("✅ A tela não vai mais quebrar se algum dado estiver faltando.")