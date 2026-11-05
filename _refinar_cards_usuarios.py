import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Encontrar e substituir o bloco de cards
padrao_cards = r'\{/\* Cards de KPI \*/\}[\s\S]*?(?=\{/\* Tabela \*/\}|<div className="glass rounded-2xl overflow-hidden border border-slate-800">)'

novo_bloco = '''{/* Cards de KPI */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Total</p>
            <p className="text-lg font-bold text-slate-100">{total}</p>
          </div>
          <Users className="size-5 text-sky-400" />
        </div>
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Ativos</p>
            <p className="text-lg font-bold text-emerald-400">{ativos}</p>
          </div>
          <UserCheck className="size-5 text-emerald-400" />
        </div>
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Inativos</p>
            <p className="text-lg font-bold text-rose-400">{inativos}</p>
          </div>
          <UserX className="size-5 text-rose-400" />
        </div>
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Administradores</p>
            <p className="text-lg font-bold text-amber-400">{admins}</p>
          </div>
          <ShieldAlert className="size-5 text-amber-400" />
        </div>
      </div>

      '''

# Executa a substituição
if re.search(padrao_cards, c):
    c = re.sub(padrao_cards, novo_bloco, c)
    print("✅ Cards de KPI refinados (compactos e relevantes).")
else:
    print("⚠️ Bloco de cards não encontrado. Verifique a estrutura do arquivo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Tela de Usuários atualizada com o novo design de cards.")