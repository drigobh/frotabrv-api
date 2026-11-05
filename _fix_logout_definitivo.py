import os
import re

# ==========================================
# 1. BACKEND: ROTA PARA CORRIGIR DATAS E RETORNAR NO /ME
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_usuarios, "r", encoding="utf-8") as f:
    u_c = f.read()

# Adiciona a rota de correção se não existir
if "fix-datas-cadastro" not in u_c:
    rota_fix = '''
@router.post("/fix-datas-cadastro")
async def fix_datas_cadastro(_u: dict = Depends(require("write"))):
    from datetime import datetime
    usuarios = await db.usuarios.find({"data_cadastro": {"$exists": False}}).to_list(1000)
    for u in usuarios:
        await db.usuarios.update_one(
            {"id": u["id"]},
            {"$set": {"data_cadastro": datetime.now().isoformat()}}
        )
    return {"status": "ok", "corrigidos": len(usuarios)}
'''
    u_c += rota_fix
    with open(path_usuarios, "w", encoding="utf-8") as f:
        f.write(u_c)
    print("✅ Backend: Rota para corrigir datas antigas criada.")

# ==========================================
# 2. FRONTEND: LOGOUT DEFINITIVO (SEM LOOP)
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    s_c = f.read()

# Substitui o onClick do botão Sair por uma função que limpa tudo e força o reload
novo_logout = '''
onClick={() => {
  localStorage.clear();
  sessionStorage.clear();
  // Força o reload da página inteira, limpando o cache do React Query
  window.location.replace("/login");
}}
'''

# Procura o botão Sair e substitui o onClick
padrao_logout = r'onClick=\{\(\) => \{ localStorage\.clear\(\); window\.location\.replace\("/login"\); \}\}'
if re.search(padrao_logout, s_c):
    s_c = re.sub(padrao_logout, novo_logout.strip(), s_c)
    print("✅ Frontend: Botão Sair atualizado com limpeza total e reload.")
else:
    # Fallback: tenta encontrar qualquer onClick que tenha localStorage
    s_c = re.sub(r'onClick=\{\(\) => \{.*?localStorage.*?\}\}', novo_logout.strip(), s_c)
    print("✅ Frontend: Botão Sair atualizado (fallback).")

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(s_c)

# ==========================================
# 3. FRONTEND: EXIBIR DATA DE CADASTRO NO MODAL DE EDIÇÃO
# ==========================================
path_usuarios_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path_usuarios_front, "r", encoding="utf-8") as f:
    c = f.read()

# Garantir que o campo de Ativação apareça no modal de edição
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
    print("✅ Frontend: Campo de Ativação adicionado ao modal de edição.")

with open(path_usuarios_front, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Tudo pronto! Faça o git push.")