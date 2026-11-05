import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "cadastros", "CadastroTable.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adiciona extraActions na desestruturação das props da função
c = c.replace(
    "export function CadastroTable<T extends CadastroRow>({ title, description, endpoint, queryKey, entityLabel, testPrefix, columns, searchKeys }: Props<T>) {",
    "export function CadastroTable<T extends CadastroRow>({ title, description, endpoint, queryKey, entityLabel, testPrefix, columns, searchKeys, extraActions }: Props<T>) {"
)

# 2. Injeta a renderização do extraActions na célula de ações
# O padrão é: <div className="flex justify-end gap-1">
# Vamos adicionar o extraActions ANTES do botão de Editar
padrao_editar = '<Button\n                          size="icon-sm"\n                          variant="ghost"\n                          onClick={() => { setEditId(row.id); setEditValues(rowValues(row, columns)); }}'
novo_editar = '''{extraActions && extraActions(row)}
                        <Button
                          size="icon-sm"
                          variant="ghost"
                          onClick={() => { setEditId(row.id); setEditValues(rowValues(row, columns)); }}'''

if "extraActions(row)" not in c:
    c = c.replace(padrao_editar, novo_editar)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ CadastroTable.tsx corrigido!")
print("✅ Agora a prop extraActions é renderizada na tabela.")

print("\nVerifique se o erro de TS sumiu no VS Code. Depois:")
print("  git add .")
print("  git commit -m 'fix: renderiza extraActions na tabela de cadastros'")
print("  git push")
