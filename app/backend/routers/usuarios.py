from fastapi import HTTPException
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db

router = APIRouter()
from lib.security import USER_RESPONSE_FIELDS, USER_RESPONSE_PROJECTION, hash_user_password, require

@router.get("", dependencies=[Depends(require("admin"))])
async def listar_usuarios():
    usuarios = await db.usuarios.find({}, USER_RESPONSE_PROJECTION).to_list(1000)
    return usuarios

@router.get("/{id}", dependencies=[Depends(require("admin"))])
async def obter_usuario(id: str):
    usuario = await db.usuarios.find_one({"id": id}, USER_RESPONSE_PROJECTION)
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    return usuario

@router.patch("/{id}/status", dependencies=[Depends(require("admin"))])
async def alterar_status(id: str, body: dict):
    ativo = body.get("ativo", True)
    await db.usuarios.update_one({"id": id}, {"$set": {"ativo": ativo}})
    return {"status": "ok"}


@router.post("", dependencies=[Depends(require("admin"))])
async def criar_usuario(body: dict):
    import uuid
    from datetime import datetime
    
    email = body.get("email")
    nome = body.get("nome")
    if not isinstance(email, str) or not email.strip() or not isinstance(nome, str) or not nome.strip():
        raise HTTPException(400, "Nome e e-mail são obrigatórios.")
    senha_hash = hash_user_password(body.get("senha"))
    data_cadastro = datetime.now().isoformat()
    novo = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "email": email.lower().strip(),
        "perfil": "operador",
        "perfil_id": body.get("perfil_id"),
        "setor": body.get("setor", ""),
        "cargo": body.get("cargo", ""),
        "telefone": body.get("telefone", ""),
        "whatsapp": body.get("whatsapp", ""),
        "foto_url": body.get("foto_url", ""),
        "senha_hash": senha_hash,
        "ativo": True,
        "created_at": data_cadastro,
        "data_cadastro": data_cadastro,
        "ultimo_acesso": None,
        "two_factor_enabled": False,
        "two_factor_secret": None,
        "notificacoes": body.get("notificacoes", {"manutencao": True, "documentos": True, "pneus": True, "resumo_semanal": False}),
    }
    await db.usuarios.insert_one(novo)
    return {campo: novo[campo] for campo in USER_RESPONSE_FIELDS if campo in novo}

@router.put("/{id}", dependencies=[Depends(require("admin"))])
async def atualizar_usuario(id: str, body: dict):
    update = {}
    for campo in ["nome", "email", "perfil_id", "setor", "cargo", "telefone", "whatsapp", "foto_url", "notificacoes"]:
        if campo in body:
            update[campo] = body[campo]
    
    if "email" in update:
        email = update["email"]
        if not isinstance(email, str) or not email.strip():
            raise HTTPException(400, "E-mail é obrigatório.")
        update["email"] = email.lower().strip()
    if update:
        await db.usuarios.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}

@router.post("/seed-perfis-padrao", dependencies=[Depends(require("admin"))])
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


@router.patch("/{id}/senha", dependencies=[Depends(require("admin"))])
async def alterar_senha(id: str, body: dict):
    senha_hash = hash_user_password(body.get("nova_senha"))
    resultado = await db.usuarios.update_one(
        {"id": id}, {"$set": {"senha_hash": senha_hash}, "$unset": {"senha": ""}}
    )
    if not resultado.matched_count:
        raise HTTPException(404, "Usuário não encontrado.")
    return {"status": "ok", "message": "Senha atualizada."}

@router.patch("/{id}/2fa", dependencies=[Depends(require("admin"))])
async def alternar_2fa(id: str, body: dict):
    ativo = body.get("ativo", False)
    await db.usuarios.update_one({"id": id}, {"$set": {"two_factor_enabled": ativo}})
    return {"status": "ok", "two_factor_enabled": ativo}

@router.post("/fix-datas-cadastro", dependencies=[Depends(require("admin"))])
async def fix_datas_cadastro():
    from datetime import datetime
    usuarios = await db.usuarios.find({"data_cadastro": {"$exists": False}}).to_list(1000)
    for u in usuarios:
        await db.usuarios.update_one(
            {"id": u["id"]},
            {"$set": {"data_cadastro": datetime.now().isoformat()}}
        )
    return {"status": "ok", "corrigidos": len(usuarios)}

@router.patch("/{id}/destravar", dependencies=[Depends(require("admin"))])
async def destravar_usuario(id: str):
    await db.usuarios.update_one({"id": id}, {"$set": {"login_tentativas": 0}})
    return {"status": "ok", "message": "Usuário destravado."}
