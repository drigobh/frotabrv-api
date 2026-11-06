import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "CadastrosFinanceiros.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Corrige os títulos da tabela de categorias (th)
c = c.replace(
    '<th className="px-5 py-3 font-medium">Nome</th>\n                  <th className="px-3 py-3 font-medium">Tipo</th>',
    '<th className="px-5 py-3 font-medium text-slate-200">Nome</th>\n                  <th className="px-3 py-3 font-medium text-slate-200">Tipo</th>'
)

# 2. Corrige o texto do nome da categoria
c = c.replace(
    '<td className="px-5 py-3 text-slate-200 font-medium">{c.nome}</td>',
    '<td className="px-5 py-3 text-slate-200 font-medium">{c.nome}</td>'
)

# 3. Corrige a mensagem de "Nenhuma categoria encontrada"
c = c.replace(
    '<tr><td colSpan={3} className="p-8 text-center text-slate-400">Nenhuma categoria encontrada.</td></tr>',
    '<tr><td colSpan={3} className="p-8 text-center text-slate-300">Nenhuma categoria encontrada.</td></tr>'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Cores da aba Categorias corrigidas para o padrão da aba Bancos.")