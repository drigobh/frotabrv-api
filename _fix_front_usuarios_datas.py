import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Ícone do 2FA: Verde se ativo, Vermelho se inativo
c = c.replace(
    '{u.two_factor_enabled ? (\n                      <span className="text-emerald-400" title="Ativo"><ShieldCheck className="size-4 mx-auto" /></span>\n                    ) : (\n                      <span className="text-slate-500" title="Inativo"><ShieldAlert className="size-4 mx-auto" /></span>\n                    )}',
    '''{u.two_factor_enabled ? (
                      <span className="text-emerald-500" title="Ativo"><ShieldCheck className="size-4 mx-auto" /></span>
                    ) : (
                      <span className="text-rose-500" title="Inativo"><ShieldAlert className="size-4 mx-auto" /></span>
                    )}'''
)

# 2. Adicionar o campo "Ativação" no modal (somente leitura, data/hora do cadastro)
# Vamos inserir após o campo "Senha Inicial" (que só aparece no novo usuário)
if "Ativação" not in c:
    c = c.replace(
        '''{!editando && (
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Senha Inicial *</Label>
                      <Input type="password" value={form.senha} onChange={(e) => setForm((s: any) => ({ ...s, senha: e.target.value }))} />
                    </div>
                  )}''',
        '''{!editando && (
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Senha Inicial *</Label>
                      <Input type="password" value={form.senha} onChange={(e) => setForm((s: any) => ({ ...s, senha: e.target.value }))} />
                    </div>
                  )}
                  {!editando && (
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Ativação (Automático)</Label>
                      <Input 
                        value={new Date().toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })} 
                        disabled 
                        className="bg-slate-900/50 border-slate-800 text-slate-400 font-mono" 
                      />
                    </div>
                  )}'''
    )

# 3. Ajustar a exibição da coluna "Cadastro" para mostrar Data e Hora (DD/MM/YYYY HH:MM:SS)
c = c.replace(
    '{u.data_cadastro ? new Date(u.data_cadastro).toLocaleDateString(\'pt-BR\') : "—"}',
    '{u.data_cadastro ? new Date(u.data_cadastro).toLocaleString(\'pt-BR\', { day: \'2-digit\', month: \'2-digit\', year: \'numeric\', hour: \'2-digit\', minute: \'2-digit\', second: \'2-digit\' }) : "—"}'
)

# 4. Ajustar a exibição da coluna "Último Acesso" para mostrar Data e Hora
c = c.replace(
    '{u.ultimo_acesso ? new Date(u.ultimo_acesso).toLocaleDateString(\'pt-BR\') : "—"}',
    '{u.ultimo_acesso ? new Date(u.ultimo_acesso).toLocaleString(\'pt-BR\', { day: \'2-digit\', month: \'2-digit\', year: \'numeric\', hour: \'2-digit\', minute: \'2-digit\', second: \'2-digit\' }) : "—"}'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Frontend: Ícone 2FA colorido, campo de ativação e datas formatadas.")