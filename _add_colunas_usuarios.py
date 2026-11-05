import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adicionar as novas colunas no <thead>
novo_thead = '''
              <th className="px-5 py-3 font-medium">Usuário</th>
              <th className="px-3 py-3 font-medium">Setor / Cargo</th>
              <th className="px-3 py-3 font-medium">Perfil</th>
              <th className="px-3 py-3 font-medium text-center">2FA</th>
              <th className="px-3 py-3 font-medium">Cadastro</th>
              <th className="px-3 py-3 font-medium">Último Acesso</th>
              <th className="px-3 py-3 font-medium">Status</th>
              <th className="px-3 py-3 text-right font-medium">Ações</th>
'''

padrao_thead = r'<th className="px-5 py-3 font-medium">Usuário</th>[\s\S]*?<th className="px-3 py-3 text-right font-medium">Ações</th>'
if re.search(padrao_thead, c):
    c = re.sub(padrao_thead, novo_thead.strip(), c)
    print("✅ Colunas adicionadas no cabeçalho da tabela.")

# 2. Adicionar as células correspondentes no <tbody>
# Encontra a linha do map e substitui as células
padrao_tbody = r'(<td className="px-5 py-3">[\s\S]*?<td className="px-3 py-3">[\s\S]*?<td className="px-3 py-3">[\s\S]*?)(<td className="px-3 py-3">\s*<Badge tone=)'

novo_tbody = r'''\1
                  <td className="px-3 py-3 text-center">
                    {u.two_factor_enabled ? (
                      <span className="text-emerald-400" title="Ativo"><ShieldCheck className="size-4 mx-auto" /></span>
                    ) : (
                      <span className="text-slate-500" title="Inativo"><ShieldAlert className="size-4 mx-auto" /></span>
                    )}
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-400 font-mono">
                    {u.data_cadastro ? new Date(u.data_cadastro).toLocaleDateString('pt-BR') : "—"}
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-400 font-mono">
                    {u.ultimo_acesso ? new Date(u.ultimo_acesso).toLocaleDateString('pt-BR') : "—"}
                  </td>
                  \2'''

if re.search(padrao_tbody, c):
    c = re.sub(padrao_tbody, novo_tbody, c)
    print("✅ Células de 2FA, Cadastro e Último Acesso adicionadas.")

# 3. Ajustar o colSpan do loading/empty (agora são 8 colunas)
c = c.replace('colSpan={5}', 'colSpan={8}')

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Tabela de Usuários atualizada com as novas colunas!")