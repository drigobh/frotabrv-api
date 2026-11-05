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
    import uuid
    import bcrypt
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
        "ativo": True
    }
    await db.usuarios.insert_one(novo)
    novo.pop("_id", None)
    novo.pop("senha", None)
    return novo

@router.put("/{id}")
async def atualizar_usuario(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {"nome": body.get("nome"), "email": body.get("email"), "perfil": body.get("perfil")}
    await db.usuarios.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}


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
