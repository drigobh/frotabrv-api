import os

def fix_model(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "manutencoes.py")
    codigo = '''from pydantic import BaseModel, Field
from typing import Optional

class ManutencaoCreate(BaseModel):
    veiculo_id: str
    tipo: str
    status: str
    descricao: str
    data: str = Field(pattern=r"^\\d{4}-\\d{2}-\\d{2}$")
    custo: float = 0.0
    oficina: Optional[str] = None
    fornecedor_id: Optional[str] = None
    km_manutencao: Optional[float] = None
    proxima_revisao_km: Optional[float] = None
    pecas_substituidas: Optional[str] = None

class Manutencao(ManutencaoCreate):
    id: str
    veiculo_label: str
    criado_por: str
    created_at: str
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Modelo de Manutenção atualizado com fornecedor_id e criado_por.")

def fix_router(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    codigo = '''from fastapi import APIRouter, Depends, HTTPException, Request
from lib.dates import now_iso
from lib.db import db
from lib.security import require
from models.manutencoes import Manutencao, ManutencaoCreate
import uuid

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])

@router.get("", response_model=None)
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.manutencoes.find({}, {"_id": 0}).sort("data", -1).to_list(2000)
    return docs

@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    
    # Grava o nome do usuário logado (não pode ser alterado depois)
    doc["criado_por"] = user.get("nome", user.get("email", "Sistema"))
    doc["created_at"] = now_iso()

    await db.manutencoes.insert_one(doc)
    doc.pop("_id", None)
    return doc

@router.put("/{id}", response_model=Manutencao)
async def atualizar(id: str, body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    existe = await db.manutencoes.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Manutenção não encontrada")

    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    
    # MANTÉM O CRIADO_POR ORIGINAL
    doc["criado_por"] = existe.get("criado_por", user.get("nome", "Sistema"))
    doc["created_at"] = existe.get("created_at", now_iso())

    await db.manutencoes.update_one({"id": id}, {"$set": doc})
    
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.manutencoes.delete_one({"id": id})
    return {"ok": True}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Router de Manutenções atualizado para salvar e manter o criado_por.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que o form tenha fornecedor_id e que o abrirNovo o limpe
    if 'fornecedor_id: "",' not in c:
        c = c.replace('oficina: "",', 'oficina: "",\n  fornecedor_id: "",')

    # 2. Garantir que o abrirEdicao carregue o fornecedor_id
    if 'fornecedor_id: (r as any).fornecedor_id || "",' not in c:
        c = c.replace('oficina: r.oficina || "",', 'oficina: r.oficina || "",\n      fornecedor_id: (r as any).fornecedor_id || "",')

    # 3. Garantir que o campo de fornecedor no form está correto e visível
    if 'manutencao-form-fornecedor' not in c:
        c = c.replace(
            '<div className="grid gap-1.5"><Label>Oficina / prestador</Label><Input value={form.oficina} onChange={(e) => set("oficina")(e.target.value)} /></div>',
            '''<div className="col-span-2 grid gap-1.5">
              <Label>Fornecedor / Oficina *</Label>
              <FieldSelect value={form.fornecedor_id} onChange={set("fornecedor_id")} options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} placeholder="Selecione o prestador" testId="manutencao-form-fornecedor" />
            </div>'''
        )

    # 4. Corrigir o Tooltip do "i" na tabela
    if 'created_by' not in c and 'criado_por' in c:
        # Se o campo criado_por já existe no backend, só precisamos forçar a exibição correta
        old_i = '''<Button size="icon-sm" variant="ghost" className="cursor-help" title={`Criado por: ${(r as any).criado_por || 'Sistema'}`}>
                      <Info className="size-4 text-slate-400" />
                    </Button>'''
        new_i = '''<Button size="icon-sm" variant="ghost" className="cursor-help" title={`Criado por: ${r.criado_por || 'Sistema'}`}>
                      <Info className="size-4 text-slate-400" />
                    </Button>'''
        if old_i in c:
            c = c.replace(old_i, new_i)

    # 5. Garantir que o usuário logado apareça no topo do modal e o campo não seja editável
    if 'Criado por:' not in c:
        c = c.replace(
            '<DialogTitle className="flex items-center gap-2"><Wrench className="size-5 text-sky-400" /> {editingId ? "Editar" : "Nova"} manutenção</DialogTitle>',
            '''<div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2"><Wrench className="size-5 text-sky-400" /> {editingId ? "Editar" : "Nova"} manutenção</DialogTitle>
              <span className="text-xs text-slate-500 flex items-center gap-1"><UserCircle className="size-3"/> {me?.nome || "Usuário"}</span>
            </div>'''
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend de Manutenções atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_model(raiz)
    fix_router(raiz)
    fix_frontend(raiz)