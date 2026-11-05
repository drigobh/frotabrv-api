from fastapi import HTTPException
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db

router = APIRouter()
from lib.security import require

@router.get("")
async def listar_usuarios():
    usuarios = await db.usuarios.find({}, {"_id": 0, "senha": 0}).to_list(1000)
    return usuarios

@router.get("/{id}")
async def obter_usuario(id: str):
    usuario = await db.usuarios.find_one({"id": id}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    return usuario

@router.patch("/{id}/status")
async def alterar_status(id: str, body: dict):
    ativo = body.get("ativo", True)
    await db.usuarios.update_one({"id": id}, {"$set": {"ativo": ativo}})
    return {"status": "ok"}


@router.post("")
async def criar_usuario(body: dict, _u: dict = Depends(require("write"))):
    import bcrypt
    import uuid
    from datetime import datetime
    
    senha_hash = bcrypt.hashpw(body.get("senha", "").encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "email": body.get("email"),
        "perfil_id": body.get("perfil_id"),
        "setor": body.get("setor", ""),
        "cargo": body.get("cargo", ""),
        "telefone": body.get("telefone", ""),
        "whatsapp": body.get("whatsapp", ""),
        "foto_url": body.get("foto_url", ""),
        "senha": senha_hash,
        "ativo": True,
        "data_cadastro": datetime.now().isoformat(),
        "ultimo_acesso": None,
        "two_factor_enabled": False,
        "two_factor_secret": None,
        "notificacoes": body.get("notificacoes", {"manutencao": True, "documentos": True, "pneus": True, "resumo_semanal": False}),
    }
    await db.usuarios.insert_one(novo)
    novo.pop("_id", None)
    novo.pop("senha", None)
    return novo

@router.put("/{id}")
async def atualizar_usuario(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {}
    for campo in ["nome", "email", "perfil_id", "setor", "cargo", "telefone", "whatsapp", "foto_url"]:
        if campo in body:
            update[campo] = body[campo]
    
    if update:
        await db.usuarios.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

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


@router.patch("/{id}/senha")
async def alterar_senha(id: str, body: dict, _u: dict = Depends(require("write"))):
    import bcrypt
    nova_senha = body.get("nova_senha", "")
    if len(nova_senha) < 6:
        raise HTTPException(400, "Senha muito curta.")
    senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    await db.usuarios.update_one({"id": id}, {"$set": {"senha": senha_hash}})
    return {"status": "ok", "message": "Senha atualizada."}

@router.patch("/{id}/2fa")
async def alternar_2fa(id: str, body: dict, _u: dict = Depends(require("write"))):
    ativo = body.get("ativo", False)
    await db.usuarios.update_one({"id": id}, {"$set": {"two_factor_enabled": ativo}})
    return {"status": "ok", "two_factor_enabled": ativo}
