import os
import re

# ==========================================
# 1. CORRIGIR O SIDEBAR (Sintaxe e Logout)
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    c = f.read()

# Remove qualquer resquício de scripts anteriores que possam ter quebrado o JSX
c = re.sub(r'\{\s*localStorage\.clear\(\);.*?window\.location.*?\}', '', c, flags=re.DOTALL)
c = re.sub(r'onClick=\{\(\) => \{.*?\}\}', 'onClick={() => {}}', c, flags=re.DOTALL)  # Limpa onClicks malformados
c = re.sub(r'\}\}\}>', '}>', c)  # Corrige fechamento de tags

# Garantir que useNavigate está importado
if "useNavigate" not in c:
    c = c.replace(
        'import { Link, useLocation } from "react-router-dom";',
        'import { Link, useLocation, useNavigate } from "react-router-dom";'
    )

# Adicionar navigate no componente
if "const navigate = useNavigate();" not in c:
    match_comp = re.search(r'(export function Sidebar\(\)\s*\{)', c)
    if match_comp:
        c = c.replace(match_comp.group(1), match_comp.group(1) + "\n  const navigate = useNavigate();")

# Substituir o botão Sair por um onClick seguro
padrao_sair = r'(<Button[^>]*>[\s\S]*?Sair[\s\S]*?</Button>)'
if re.search(padrao_sair, c):
    c = re.sub(padrao_sair, lambda m: re.sub(r'onClick=\{[^}]*\}', 'onClick={() => { localStorage.clear(); sessionStorage.clear(); navigate("/login"); }}', m.group(0)), c)

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Sidebar.tsx corrigido (sintaxe e logout via navigate).")

# ==========================================
# 2. CORRIGIR O USUARIOS.TSX (Campo de Ativação)
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path_usuarios, "r", encoding="utf-8") as f:
    c = f.read()

# Garantir que o campo Ativação apareça no modal
# Vamos inserir logo após o campo "Perfil de Acesso"
if "Ativação (Automático)" not in c:
    c = c.replace(
        '<Label className="text-xs text-slate-400">Perfil de Acesso (RBAC) *</Label>',
        '''<Label className="text-xs text-slate-400">Ativação (Automático)</Label>
                    <Input 
                      value={editando && editando.data_cadastro ? new Date(editando.data_cadastro).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "—"} 
                      disabled 
                      className="bg-slate-900/50 border-slate-800 text-slate-400 font-mono" 
                    />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Perfil de Acesso (RBAC) *</Label>'''
    )
    print("✅ Usuarios.tsx: Campo de Ativação adicionado ao modal de edição.")

with open(path_usuarios, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Tudo pronto! Faça o git push.")