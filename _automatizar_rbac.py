import os
import re

# ==========================================
# 1. BACKEND: POVOAR PERFIS E AJUSTAR USUÁRIOS
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_usuarios, "r", encoding="utf-8") as f:
    u_c = f.read()

# Garante a importação do UUID
if "import uuid" not in u_c:
    u_c = "import uuid\n" + u_c

# Adiciona a rota de inicialização (semente) dos perfis padrão
rota_seed = '''

@router.post("/seed-perfis-padrao")
async def seed_perfis_padrao():
    """Cria os perfis base do sistema se ainda não existirem."""
    perfis = [
        {
            "id": "perfil-admin",
            "nome": "Administrador",
            "descricao": "Acesso total ao sistema, sem restrições.",
            "permissoes": ["*:*"]
        },
        {
            "id": "perfil-gestor",
            "nome": "Gestor",
            "descricao": "Gestão de frotas, aprovações e relatórios.",
            "permissoes": ["Frota:Ver", "Frota:Criar", "Frota:Editar", "Manutenção:Aprovar", "Relatórios:Ver"]
        },
        {
            "id": "perfil-operador",
            "nome": "Operador",
            "descricao": "Operação diária de abastecimento e pneus.",
            "permissoes": ["Abastecimentos:Ver", "Abastecimentos:Criar", "Pneus:Ver", "Pneus:Criar"]
        },
        {
            "id": "perfil-manutencao",
            "nome": "Manutenção",
            "descricao": "Acesso à oficina e checklist de pneus.",
            "permissoes": ["Pneus:Ver", "Pneus:Editar", "Manutenção:Ver", "Manutenção:Criar"]
        },
        {
            "id": "perfil-financeiro",
            "nome": "Financeiro",
            "descricao": "Controle de custos, abastecimentos e aprovações.",
            "permissoes": ["Financeiro:Ver", "Financeiro:Editar", "Abastecimentos:Ver", "Relatórios:Ver"]
        },
        {
            "id": "perfil-motorista",
            "nome": "Motorista",
            "descricao": "Acesso apenas ao painel e lançamento de abastecimento.",
            "permissoes": ["Dashboard:Ver", "Abastecimentos:Criar"]
        }
    ]
    for p in perfis:
        await db.perfis.update_one({"id": p["id"]}, {"$set": p}, upsert=True)
    return {"status": "ok", "message": "Perfis padrão criados."}
'''
if "seed-perfis-padrao" not in u_c:
    u_c += rota_seed
    with open(path_usuarios, "w", encoding="utf-8") as f:
        f.write(u_c)
    print("✅ Backend: Rota de criação dos 6 perfis padrão injetada.")

# ==========================================
# 2. FRONTEND: ATUALIZAR O MODAL DE USUÁRIO
# ==========================================
path_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path_front, "r", encoding="utf-8") as f:
    front_c = f.read()

# 1. Adicionar a busca de perfis no topo do componente
if "useQuery({ queryKey: [\"perfis\"]" not in front_c:
    front_c = front_c.replace(
        'const { data: usuarios = [], isLoading } = useQuery({',
        'const { data: perfis = [] } = useQuery({ queryKey: ["perfis"], queryFn: () => apiGet<any[]>("/perfis") });\n  const { data: usuarios = [], isLoading } = useQuery({'
    )

# 2. Substituir o <select> fixo pelo select dinâmico de perfis do RBAC
padrao_select = r'<select value=\{form\.perfil\}.*?</select>'
novo_select = '''<select value={form.perfil_id || ""} onChange={(e) => setForm(s => ({ ...s, perfil_id: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="">Selecione um perfil...</option>
                      {perfis.map((p: any) => (
                        <option key={p.id} value={p.id}>{p.nome}</option>
                      ))}
                    </select>'''
front_c = re.sub(padrao_select, novo_select, front_c, flags=re.DOTALL)

# 3. Ajustar o estado do form para usar perfil_id e buscar os perfis
front_c = front_c.replace('perfil: "Operador"', 'perfil_id: ""')
front_c = front_c.replace('perfil: u.perfil || "Operador"', 'perfil_id: u.perfil_id || ""')
front_c = front_c.replace('{ nome: "", email: "", perfil: "Operador", senha: "" }', '{ nome: "", email: "", perfil_id: "", senha: "" }')
front_c = front_c.replace('{ nome: u.nome, email: u.email, perfil: u.perfil || "Operador", senha: "" }', '{ nome: u.nome, email: u.email, perfil_id: u.perfil_id || "", senha: "" }')

# 4. Exibir o nome do perfil na tabela (não o ID)
front_c = front_c.replace(
    '<Shield className="size-3" /> {u.perfil || "Operador"}',
    '<Shield className="size-3" /> {perfis.find((p: any) => p.id === u.perfil_id)?.nome || "Sem perfil"}'
)

with open(path_front, "w", encoding="utf-8") as f:
    f.write(front_c)
print("✅ Frontend: Modal de usuário conectado aos perfis do RBAC.")

print("\n✅ Tudo pronto! Faça o git push.")