import os
import re

# ==========================================
# 1. CORRIGIR O LOGOUT (Limpar Token e Redirecionar)
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    s_c = f.read()

# Substituir o onClick do botão Sair para limpar o token e redirecionar sem loop
s_c = s_c.replace(
    'onClick={() => { localStorage.removeItem("token"); window.location.href = "/login"; }}',
    'onClick={() => { localStorage.clear(); window.location.href = "/login"; }}'
)

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(s_c)
print("✅ Frontend: Botão Sair agora limpa o localStorage e redireciona.")

# ==========================================
# 2. CORRIGIR A TABELA (Exibir Data de Cadastro e Último Acesso)
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path_usuarios, "r", encoding="utf-8") as f:
    c = f.read()

# Garantir que a coluna Cadastro use data_cadastro
c = c.replace(
    "{u.data_cadastro ? new Date(u.data_cadastro).toLocaleDateString('pt-BR') : \"—\"}",
    "{u.data_cadastro ? new Date(u.data_cadastro).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : \"—\"}"
)

# Garantir que a coluna Último Acesso use ultimo_acesso
c = c.replace(
    "{u.ultimo_acesso ? new Date(u.ultimo_acesso).toLocaleDateString('pt-BR') : \"—\"}",
    "{u.ultimo_acesso ? new Date(u.ultimo_acesso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : \"—\"}"
)

with open(path_usuarios, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Frontend: Colunas de Cadastro e Último Acesso formatadas com data e hora.")

print("✅ Tudo corrigido! Faça o git push.")