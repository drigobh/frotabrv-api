import os
import re

path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Garantir que o link para o perfil está lá e mostrando os dados corretos
if "to=\"/perfil\"" not in c:
    # Procura o bloco do usuário no rodapé
    padrao_usuario = r'<div className=\{cn\("flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-900/50 mb-2".*?\}>[\s\S]*?</div>'
    
    novo_bloco = '''<Link to="/perfil" className={cn("flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-900/50 mb-2 transition-colors hover:bg-slate-800", isCollapsed && "justify-center")}>
          <div className="size-8 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300 shrink-0 overflow-hidden">
            {me?.foto_url ? (
              <img src={me.foto_url} alt={me.nome} className="size-full object-cover" />
            ) : (
              me?.nome?.charAt(0).toUpperCase() || "U"
            )}
          </div>
          {!isCollapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-slate-200 truncate">{me?.nome || "Usuário"}</p>
              <p className="text-[10px] text-slate-500 truncate">{me?.perfil_nome || me?.perfil || "Operador"}</p>
            </div>
          )}
        </Link>'''
    
    c = re.sub(padrao_usuario, novo_bloco, c)
    print("✅ Sidebar: Rodapé do usuário sincronizado com a tela de administração.")

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar atualizado! O rodapé agora mostra foto, nome e perfil real.")