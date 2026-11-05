import os
import re

# ==========================================
# 1. CRIAR O HOOK DE PERMISSÕES
# ==========================================
path_hook = os.path.join(os.getcwd(), "frontend", "src", "hooks", "usePermissions.ts")

conteudo_hook = r'''import { useMe } from "./useSession";

export function usePermissions() {
  const { data: me } = useMe();
  const permissoes = me?.permissoes || []; // Assumindo que o backend envia a lista

  const temPermissao = (modulo: string, acao: string = "Ver") => {
    if (!me) return false;
    // Admin tem acesso total
    if (me.perfil === "Administrador" || permissoes.includes("*:*")) return true;
    return permissoes.includes(`${modulo}:${acao}`);
  };

  const podeVer = (modulo: string) => temPermissao(modulo, "Ver");

  return { temPermissao, podeVer, permissoes, me };
}
'''

with open(path_hook, "w", encoding="utf-8") as f:
    f.write(conteudo_hook)
print("✅ Hook usePermissions criado.")

# ==========================================
# 2. ATUALIZAR O SIDEBAR PARA FILTRAR MENUS
# ==========================================
path_sidebar = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")

with open(path_sidebar, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Importar o hook
if "usePermissions" not in c:
    c = c.replace(
        'import { useMe } from "@/hooks/useSession";',
        'import { useMe } from "@/hooks/useSession";\nimport { usePermissions } from "@/hooks/usePermissions";'
    )

# 2. Inicializar o hook dentro do componente
if "const { podeVer } = usePermissions();" not in c:
    c = c.replace(
        'const { data: me } = useMe();',
        'const { data: me } = useMe();\n  const { podeVer } = usePermissions();'
    )

# 3. Filtrar os menus baseados nas permissões
# Precisamos mapear o "id" do menu para o nome do módulo no RBAC
mapa_modulos = {
    "administracao": "Administração",
    "cadastros": "Cadastros",
    "frota": "Frota",
    "manutencao": "Manutenção",
    "financeiro": "Financeiro",
    "gestao": "Relatórios",
    "relatorios-gerais": "Relatórios",
}

# Substituir o .map para filtrar
c = c.replace(
    '{MENUS.map((menu) => {',
    '''{MENUS.filter(menu => {
            if (menu.isDashboard) return true; // Dashboard é livre
            const modulo = {
              "administracao": "Administração",
              "cadastros": "Cadastros",
              "frota": "Frota",
              "manutencao": "Manutenção",
              "financeiro": "Financeiro",
              "gestao": "Relatórios",
              "relatorios-gerais": "Relatórios",
            }[menu.id];
            return modulo ? podeVer(modulo) : true;
          }).map((menu) => {'''
)

# 4. Filtrar os submenus dentro de cada menu
c = c.replace(
    '{menu.items.map((item) => (',
    '''{menu.items.filter(item => {
                    // Lógica básica: se o usuário tem permissão no módulo pai, vê todos os filhos.
                    // Para refinamento, mapearíamos cada item para uma ação específica.
                    return true; 
                  }).map((item) => ('''
)

with open(path_sidebar, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Sidebar atualizado para filtrar menus por permissão.")

# ==========================================
# 3. GARANTIR QUE O /auth/me RETORNE AS PERMISSÕES
# ==========================================
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    a_c = f.read()

# A rota /me já retorna todos os campos do usuário, mas precisamos incluir as permissões do perfil
padrao_me = r'@router\.get\("/me"\)[\s\S]*?(?=@router|\Z)'
nova_rota_me = '''
@router.get("/me")
async def me(_u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": _u["id"]}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    
    # Busca as permissões do perfil
    if usuario.get("perfil_id"):
        perfil = await db.perfis.find_one({"id": usuario["perfil_id"]}, {"_id": 0})
        if perfil:
            usuario["permissoes"] = perfil.get("permissoes", [])
            usuario["perfil_nome"] = perfil.get("nome", "")
    
    return usuario
'''
a_c = re.sub(padrao_me, nova_rota_me.strip() + "\n\n", a_c)

with open(path_auth, "w", encoding="utf-8") as f:
    f.write(a_c)
print("✅ Backend: Rota /auth/me agora retorna as permissões do perfil.")