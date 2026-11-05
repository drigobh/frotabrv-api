import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Calcular os KPIs antes do return
if "const totalUsuarios" not in c:
    c = c.replace(
        'const filtrados = usuarios.filter((u: any) =>',
        '''const totalUsuarios = usuarios.length;
  const ativos = usuarios.filter((u: any) => u.ativo).length;
  const inativos = usuarios.filter((u: any) => !u.ativo).length;
  const admins = usuarios.filter((u: any) => u.perfil_id === "perfil-admin").length;

  const filtrados = usuarios.filter((u: any) =>'''
    )

# 2. Injetar os cards antes da tabela
if "grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6" not in c:
    cards_jsx = '''
      {/* Cards de KPI */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800 flex items-center justify-between hover:border-sky-500/30 transition-colors">
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">Total de Usuários</p>
            <p className="text-2xl font-bold text-slate-100 mt-1">{totalUsuarios}</p>
          </div>
          <div className="p-2 bg-sky-500/10 rounded-lg"><Users className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800 flex items-center justify-between hover:border-emerald-500/30 transition-colors">
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">Usuários Ativos</p>
            <p className="text-2xl font-bold text-emerald-400 mt-1">{ativos}</p>
          </div>
          <div className="p-2 bg-emerald-500/10 rounded-lg"><Check className="size-5 text-emerald-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800 flex items-center justify-between hover:border-rose-500/30 transition-colors">
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">Inativos</p>
            <p className="text-2xl font-bold text-rose-400 mt-1">{inativos}</p>
          </div>
          <div className="p-2 bg-rose-500/10 rounded-lg"><X className="size-5 text-rose-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800 flex items-center justify-between hover:border-amber-500/30 transition-colors">
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">Administradores</p>
            <p className="text-2xl font-bold text-amber-400 mt-1">{admins}</p>
          </div>
          <div className="p-2 bg-amber-500/10 rounded-lg"><Shield className="size-5 text-amber-400" /></div>
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">'''
    
    # Substitui a div da tabela pela nova estrutura (cards + tabela)
    c = c.replace(
        '<div className="glass rounded-2xl overflow-hidden border border-slate-800">',
        cards_jsx
    )

# 3. Garantir que o ícone Users está importado
if "Users" not in c.split("from \"lucide-react\"")[0]:
    c = c.replace("import {", "import { Users,")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Cards de KPI adicionados à tela de Usuários.")