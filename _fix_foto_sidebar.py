import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Localizar o bloco do usuário no rodapé
padrao = r'<div className="size-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300 shrink-0">[\s\S]*?</div>'
novo_bloco = '''<div className="size-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300 shrink-0 overflow-hidden">
            {me?.foto_url ? (
              <img src={me.foto_url} alt={me.nome} className="size-full object-cover" />
            ) : (
              me?.nome?.charAt(0).toUpperCase() || "U"
            )}
          </div>'''

if re.search(padrao, c):
    c = re.sub(padrao, novo_bloco, c)
    print("✅ Sidebar: Foto do usuário adicionada ao rodapé.")

# 2. Garantir que o link para o perfil está lá (para o clique funcionar)
if "to=\"/perfil\"" not in c:
    # Envolve o bloco com o Link
    padrao_bloco = r'(<div className=\{cn\("flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-900/50 mb-2", isCollapsed && "justify-center"\)\}>)([\s\S]*?)(</div>)'
    c = re.sub(padrao_bloco, r'<Link to="/perfil" \1\2</Link>', c)
    print("✅ Sidebar: Rodapé do usuário agora é clicável.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar atualizado! A foto aparece no rodapé.")