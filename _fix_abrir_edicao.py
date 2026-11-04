import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Força a substituição da função abrirEdicao inteira
nova_abrir = '''const abrirEdicao = (r: any) => { 
    setEditingId(r.id); 
    setForm({ 
      ...r, 
      custo_aquisicao: String(r.custo_aquisicao || ""),
      equipamento: r.equipamento || "",
      posicao: r.posicao || "",
      banda_rod: r.banda_rod || "",
      estrutura: r.estrutura || "",
      n_serie: r.n_serie || "",
      n_recap: r.n_recap || "",
      data_compra: parseDate(r.data_compra),
      data_descarte: parseDate(r.data_descarte),
      custo_total_atual: r.custo_total_atual || "",
      profundidade_atual: r.profundidade_atual || "",
      uso_atual: r.uso_atual || "",
      custo_por_km: r.custo_por_km || "",
      km_posicao: r.km_posicao || ""
    }); 
    setOpen(true); 
  };'''

c = re.sub(r'const abrirEdicao = \(r: any\) => \{[\s\S]*?setOpen\(true\);\s*\};', nova_abrir, c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Função abrirEdicao atualizada forçadamente com o parseDate!")