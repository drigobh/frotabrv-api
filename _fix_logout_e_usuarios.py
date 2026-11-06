import os
import re

# ==========================================
# 1. CORRIGIR O LOGOUT (Função à Prova de Loop)
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    s_c = f.read()

# Substituir o onClick do botão Sair por uma função que força o reload da página
# Vamos usar uma abordagem que limpa o localStorage, sessionStorage e força o reload
novo_logout = '''
onClick={() => {
  localStorage.clear();
  sessionStorage.clear();
  // Força o reload completo da página
  window.location.href = window.location.origin + "/login";
  window.location.reload();
}}
'''

# Procura o botão Sair (que tem o ícone LogOut)
padrao_logout = r'onClick=\{[^}]*localStorage[^}]*\}'
if re.search(padrao_logout, s_c):
    s_c = re.sub(padrao_logout, novo_logout.strip(), s_c)
    print("✅ Sidebar: Botão Sair atualizado com reload forçado.")
else:
    print("⚠️ Botão Sair não encontrado. Verifique o arquivo Sidebar.tsx.")

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(s_c)

# ==========================================
# 2. ATUALIZAR A TABELA DE USUÁRIOS (Colunas de Data e Hora)
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path_usuarios, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adicionar as colunas no <thead> se não existirem
if "<th className=\"px-3 py-3 font-medium\">Cadastro</th>" not in c:
    c = c.replace(
        '<th className="px-3 py-3 text-right font-medium">Ações</th>',
        '<th className="px-3 py-3 font-medium">Cadastro</th>\n              <th className="px-3 py-3 font-medium">Último Acesso</th>\n              <th className="px-3 py-3 text-right font-medium">Ações</th>'
    )

# 2. Adicionar as células correspondentes no <tbody> se não existirem
if "u.data_cadastro" not in c:
    c = c.replace(
        '<td className="px-3 py-3 text-right flex justify-end gap-1">',
        '''<td className="px-3 py-3 text-xs text-slate-400 font-mono">
                    {u.data_cadastro ? new Date(u.data_cadastro).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "—"}
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-400 font-mono">
                    {u.ultimo_acesso ? new Date(u.ultimo_acesso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "—"}
                  </td>
                  <td className="px-3 py-3 text-right flex justify-end gap-1">'''
    )

# 3. Ajustar o colSpan do loading/empty (agora são 9 colunas)
c = c.replace('colSpan={5}', 'colSpan={9}')

with open(path_usuarios, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Frontend: Colunas de Cadastro e Último Acesso adicionadas à tabela.")

print("✅ Tudo pronto! Faça o git push.")