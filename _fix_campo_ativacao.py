import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remover o campo de Ativação de dentro do bloco {!editando && (...) }
# e adicioná-lo fora, para aparecer em ambos os casos.

# Primeiro, remove qualquer versão atual do campo (tanto no bloco novo quanto no editar)
c = re.sub(r'\{!editando && \(\s*<div className="grid gap-1\.5">\s*<Label[^>]*>Ativação.*?</div>\s*\)\}', '', c, flags=re.DOTALL)

# Agora insere o campo de Ativação fora do bloco condicional, logo após o campo de Perfil RBAC
c = c.replace(
    '<Label className="text-xs text-slate-400">Perfil de Acesso (RBAC) *</Label>',
    '''<Label className="text-xs text-slate-400">Perfil de Acesso (RBAC) *</Label>
                    <select value={form.perfil_id} onChange={(e) => setForm((s: any) => ({ ...s, perfil_id: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="">Selecione um perfil...</option>
                      {perfis.map((p: any) => (
                        <option key={p.id} value={p.id}>{p.nome}</option>
                      ))}
                    </select>
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Ativação (Automático)</Label>
                    <Input 
                      value={editando && editando.data_cadastro ? new Date(editando.data_cadastro).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : (new Date().toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }))} 
                      disabled 
                      className="bg-slate-900/50 border-slate-800 text-slate-400 font-mono" 
                    />
                  </div>
                  <div className="grid gap-1.5">'''
)

# Remover o select antigo que ficou duplicado (o original)
c = re.sub(r'<select value=\{form\.perfil_id\}.*?</select>', '', c, count=1, flags=re.DOTALL)

# Remover o campo de senha do bloco {!editando && (...)} se ele tiver ficado duplicado
# (Não é necessário, mas garante que o layout não fique bagunçado)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Campo de Ativação agora aparece em Novo e Editar.")