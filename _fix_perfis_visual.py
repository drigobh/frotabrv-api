import os
import re

# ==========================================
# 1. FRONTEND: CORRIGIR A LEITURA DAS PERMISSÕES
# ==========================================
path_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path_front, "r", encoding="utf-8") as f:
    c = f.read()

# A função abrirEdicao precisa garantir que permissoes seja um array válido
c = c.replace(
    'permissoes: p.permissoes || []',
    'permissoes: Array.isArray(p.permissoes) ? p.permissoes : []'
)

# A função togglePermissao precisa funcionar mesmo se permissoes for undefined
c = c.replace(
    'permissoes: s.permissoes.includes(chave)',
    'permissoes: (Array.isArray(s.permissoes) ? s.permissoes : []).includes(chave)'
)

with open(path_front, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Frontend: Leitura de permissões corrigida.")

# ==========================================
# 2. BACKEND: FORÇAR ATUALIZAÇÃO DOS PERFIS COM OS DADOS CORRETOS
# ==========================================
path_usuarios = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_usuarios, "r", encoding="utf-8") as f:
    u_c = f.read()

# Substitui a rota de seed por uma versão que sobrescreve os dados existentes (upsert)
nova_rota = '''
@router.post("/seed-perfis-padrao")
async def seed_perfis_padrao():
    """Cria ou atualiza os perfis base do sistema."""
    perfis = [
        {
            "id": "perfil-admin",
            "nome": "Administrador",
            "descricao": "Acesso total ao sistema, sem restrições.",
            "permissoes": ["Dashboard:Ver", "Abastecimentos:Ver", "Abastecimentos:Criar", "Abastecimentos:Editar", "Abastecimentos:Excluir", "Pneus:Ver", "Pneus:Criar", "Pneus:Editar", "Pneus:Excluir", "Manutenção:Ver", "Manutenção:Criar", "Manutenção:Editar", "Manutenção:Aprovar", "Frota:Ver", "Frota:Criar", "Frota:Editar", "Frota:Excluir", "Financeiro:Ver", "Financeiro:Criar", "Financeiro:Editar", "Financeiro:Aprovar", "Relatórios:Ver", "Relatórios:Exportar", "Cadastros:Ver", "Cadastros:Criar", "Cadastros:Editar", "Cadastros:Excluir", "Administração:Ver", "Administração:Criar", "Administração:Editar", "Administração:Excluir"]
        },
        {
            "id": "perfil-gestor",
            "nome": "Gestor",
            "descricao": "Gestão de frotas, aprovações e relatórios.",
            "permissoes": ["Dashboard:Ver", "Frota:Ver", "Frota:Criar", "Frota:Editar", "Manutenção:Ver", "Manutenção:Aprovar", "Relatórios:Ver", "Relatórios:Exportar", "Financeiro:Ver"]
        },
        {
            "id": "perfil-operador",
            "nome": "Operador",
            "descricao": "Operação diária de abastecimento e pneus.",
            "permissoes": ["Dashboard:Ver", "Abastecimentos:Ver", "Abastecimentos:Criar", "Pneus:Ver", "Pneus:Criar"]
        },
        {
            "id": "perfil-manutencao",
            "nome": "Manutenção",
            "descricao": "Acesso à oficina e checklist de pneus.",
            "permissoes": ["Dashboard:Ver", "Pneus:Ver", "Pneus:Editar", "Manutenção:Ver", "Manutenção:Criar", "Manutenção:Editar"]
        },
        {
            "id": "perfil-financeiro",
            "nome": "Financeiro",
            "descricao": "Controle de custos, abastecimentos e aprovações.",
            "permissoes": ["Dashboard:Ver", "Financeiro:Ver", "Financeiro:Editar", "Financeiro:Aprovar", "Abastecimentos:Ver", "Relatórios:Ver"]
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
    return {"status": "ok", "message": "Perfis padrão atualizados."}
'''

# Substitui a rota antiga
padrao = r'@router\.post\("/seed-perfis-padrao"\)[\s\S]*?return\s*\{[^}]*\}'
u_c = re.sub(padrao, nova_rota.strip(), u_c)

with open(path_usuarios, "w", encoding="utf-8") as f:
    f.write(u_c)
print("✅ Backend: Rota de seed atualizada para sobrescrever os dados.")