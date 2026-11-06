import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Garantir que o abrirEdicao carregue o timeout e tentativas
c = c.replace(
    'setForm({ nome: p.nome, descricao: p.descricao || "", permissoes: p.permissoes || [] })',
    'setForm({ nome: p.nome, descricao: p.descricao || "", permissoes: p.permissoes || [], timeout_minutos: p.timeout_minutos, tentativas_login: p.tentativas_login || "5" })'
)

# Garantir que o salvar envie os campos
c = c.replace(
    'salvar.mutate(form)',
    '''salvar.mutate({
                    nome: form.nome,
                    descricao: form.descricao,
                    permissoes: form.permissoes,
                    timeout_minutos: Number(form.timeout_minutos) || 0,
                    tentativas_login: form.tentativas_login || "5"
                  })'''
)

# Ajustar o input para aceitar 0
c = c.replace(
    'value={form.timeout_minutos || 30}',
    'value={form.timeout_minutos === 0 ? 0 : (form.timeout_minutos || 30)}'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Perfis.tsx corrigido para salvar timeout e tentativas.")