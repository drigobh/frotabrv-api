import os
import re

# ==========================================
# 1. BACKEND: ROTA DE MIGRAÇÃO FORÇADA
# ==========================================
path_perfis = os.path.join(os.getcwd(), "app", "backend", "routers", "perfis.py")

with open(path_perfis, "r", encoding="utf-8") as f:
    p_c = f.read()

rota_migracao = '''

@router.post("/migrar-seguranca")
async def migrar_seguranca():
    """Força todos os perfis a terem os campos de segurança. Admin fica com 2 min."""
    perfis = await db.perfis.find({}).to_list(100)
    for p in perfis:
        update = {}
        if "timeout_minutos" not in p:
            update["timeout_minutos"] = 30
        if "tentativas_login" not in p:
            update["tentativas_login"] = "5"
        
        # Força o admin para 2 minutos e 3 tentativas (para teste)
        if p.get("id") == "perfil-admin":
            update["timeout_minutos"] = 2
            update["tentativas_login"] = "3"
            
        if update:
            await db.perfis.update_one({"id": p["id"]}, {"$set": update})
    
    return {"status": "ok", "message": "Perfis migrados com sucesso. Admin com 2min/3tentativas."}
'''

if "migrar-seguranca" not in p_c:
    p_c += rota_migracao
    with open(path_perfis, "w", encoding="utf-8") as f:
        f.write(p_c)
    print("✅ Backend: Rota de migração criada.")

# ==========================================
# 2. FRONTEND: REESCREVER A TELA DE PERFIS (CARDS + MODAL)
# ==========================================
path_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path_front, "r", encoding="utf-8") as f:
    c = f.read()

# 2.1 Atualizar o Card para mostrar Timeout e Tentativas
c = c.replace(
    '''<div className="flex flex-wrap gap-1 mt-auto">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 font-medium">
                  {p.permissoes?.length || 0} permissões
                </span>
              </div>''',
    '''<div className="flex flex-wrap gap-1 mt-auto">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 font-medium">
                  {p.permissoes?.length || 0} permissões
                </span>
                <span className="px-2 py-0.5 rounded bg-sky-500/10 text-[10px] text-sky-400 font-medium">
                  ⏱️ {p.timeout_minutos === 0 ? "Sem timer" : `${p.timeout_minutos} min`}
                </span>
                <span className="px-2 py-0.5 rounded bg-amber-500/10 text-[10px] text-amber-400 font-medium">
                  🔒 {p.tentativas_login === "liberado" ? "Liberado" : `${p.tentativas_login} tent.`}
                </span>
              </div>'''
)

# 2.2 Garantir que o Modal carregue os valores exatos
c = c.replace(
    'setForm({ nome: p.nome, descricao: p.descricao || "", permissoes: p.permissoes || [], timeout_minutos: p.timeout_minutos, tentativas_login: p.tentativas_login || "5" })',
    '''setForm({ 
      nome: p.nome, 
      descricao: p.descricao || "", 
      permissoes: p.permissoes || [], 
      timeout_minutos: p.timeout_minutos !== undefined ? p.timeout_minutos : 30, 
      tentativas_login: p.tentativas_login || "5" 
    })'''
)

# 2.3 No input do timeout, permitir o 0
c = c.replace(
    'value={form.timeout_minutos || 30}',
    'value={form.timeout_minutos === 0 ? 0 : (form.timeout_minutos || 30)}'
)

with open(path_front, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Frontend: Cards de perfil agora mostram Timeout e Tentativas.")

# ==========================================
# 3. GARANTIR QUE O TIMER RECARREGUE AO LOGAR
# ==========================================
path_layout = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "AppLayout.tsx")

with open(path_layout, "r", encoding="utf-8") as f:
    l_c = f.read()

# Adicionar um "key" no SessionTimer para forçar a remontagem se o timeout mudar
l_c = l_c.replace(
    '<SessionTimer timeoutMinutos={user.timeout_minutos || 30} onTimeout={realizarLogoff} />',
    '<SessionTimer key={user.timeout_minutos} timeoutMinutos={user.timeout_minutos || 30} onTimeout={realizarLogoff} />'
)

with open(path_layout, "w", encoding="utf-8") as f:
    f.write(l_c)
print("✅ Frontend: AppLayout força a remontagem do Timer.")

print("✅ Tudo pronto! Faça o git push.")