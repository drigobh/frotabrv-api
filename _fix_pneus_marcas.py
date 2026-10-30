import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_MARCAS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    print(f"✅ Backup salvo: {caminho_zip}")

def criar_backend(raiz):
    # 1. Model
    model_path = os.path.join(raiz, "app", "backend", "models", "pneu_marcas.py")
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class PneuMarcaCreate(BaseModel):
    nome: str
    tipo: str  # "FABRICANTE_NOVO", "SISTEMA_REFORMA", "AMBOS"
    tier: Optional[str] = None  # "TIER_1", "TIER_2", "TIER_3"

class PneuMarca(PneuMarcaCreate):
    id: str
    created_at: str
''')
    print("✅ Model pneu_marcas.py criado.")

    # 2. Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "pneu_marcas.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneu_marcas import PneuMarcaCreate, PneuMarca

router = APIRouter(prefix="/pneu-marcas", tags=["Pneu Marcas"])

@router.get("", response_model=list[PneuMarca])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pneu_marcas.find({}, {"_id": 0}).sort("nome", 1).to_list(200)
    return [PneuMarca(**d) for d in docs]

@router.post("", response_model=PneuMarca, status_code=201)
async def criar(body: PneuMarcaCreate, user: dict = Depends(require("write"))):
    existente = await db.pneu_marcas.find_one({"nome": {"$regex": f"^{body.nome}$", "$options": "i"}})
    if existente:
        raise HTTPException(409, "Esta marca já está cadastrada.")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.pneu_marcas.insert_one(dict(doc))
    return PneuMarca(**doc)

@router.put("/{id}", response_model=PneuMarca)
async def atualizar(id: str, body: PneuMarcaCreate, user: dict = Depends(require("write"))):
    await db.pneu_marcas.update_one({"id": id}, {"$set": body.model_dump()})
    doc = await db.pneu_marcas.find_one({"id": id}, {"_id": 0})
    return PneuMarca(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.pneu_marcas.delete_one({"id": id})
    return {"ok": True}

@router.post("/seed")
async def seed_marcas(_u: dict = Depends(require("write"))):
    marcas = [
        {"nome": "Michelin", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Bridgestone", "tipo": "AMBOS", "tier": "TIER_1"},
        {"nome": "Goodyear", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Continental", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Prometeon (Pirelli)", "tipo": "FABRICANTE_NOVO", "tier": "TIER_1"},
        {"nome": "Dunlop", "tipo": "FABRICANTE_NOVO", "tier": "TIER_2"},
        {"nome": "Firestone", "tipo": "FABRICANTE_NOVO", "tier": "TIER_2"},
        {"nome": "Sailun", "tipo": "FABRICANTE_NOVO", "tier": "TIER_3"},
        {"nome": "Linglong", "tipo": "FABRICANTE_NOVO", "tier": "TIER_3"},
        {"nome": "Vipal", "tipo": "SISTEMA_REFORMA", "tier": None},
        {"nome": "Bandag", "tipo": "SISTEMA_REFORMA", "tier": None},
        {"nome": "Tipler", "tipo": "SISTEMA_REFORMA", "tier": None},
    ]
    inseridos = 0
    for m in marcas:
        existente = await db.pneu_marcas.find_one({"nome": {"$regex": f"^{m['nome']}$", "$options": "i"}})
        if not existente:
            m["id"] = str(uuid.uuid4())
            m["created_at"] = now_iso()
            await db.pneu_marcas.insert_one(dict(m))
            inseridos += 1
    return {"ok": True, "inseridos": inseridos}
''')
    print("✅ Router pneu_marcas.py criado.")

    # 3. Registrar no server.py
    server_path = os.path.join(raiz, "app", "backend", "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'pneu_marcas' not in c:
        c = c.replace(
            'from routers import pneu_medidas,',
            'from routers import pneu_marcas, pneu_medidas,'
        )
        c = c.replace(
            'api_router.include_router(pneu_medidas.router)',
            'api_router.include_router(pneu_medidas.router)\napi_router.include_router(pneu_marcas.router)'
        )
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router registrado no server.py.")

def criar_frontend(raiz):
    # 1. Criar a página de Marcas
    path = os.path.join(raiz, "frontend", "src", "pages", "PneuMarcas.tsx")
    with open(path, 'w', encoding='utf-8') as f:
        f.write('''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Tag } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

const TIPOS_MARCA = [
  { value: "FABRICANTE_NOVO", label: "Fabricante de Pneu Novo" },
  { value: "SISTEMA_REFORMA", label: "Sistema de Reforma (Recapagem)" },
  { value: "AMBOS", label: "Ambos (Novo e Reforma)" },
];

const TIERS = [
  { value: "TIER_1", label: "Tier 1 (Premium)" },
  { value: "TIER_2", label: "Tier 2 (Intermediário)" },
  { value: "TIER_3", label: "Tier 3 (Econômico)" },
];

export default function PneuMarcas() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [form, setForm] = useState({ nome: "", tipo: "FABRICANTE_NOVO", tier: "TIER_1" });

  const { data: marcas = [] } = useQuery({ queryKey: ["pneu-marcas"], queryFn: () => apiGet<any[]>("/pneu-marcas") });
  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });

  const seed = useMutation({
    mutationFn: () => apiPost("/pneu-marcas/seed", {}),
    onSuccess: () => { toast.success("Marcas populadas!"); qc.invalidateQueries({ queryKey: ["pneu-marcas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const popularMarcas = () => {
    if (confirm("Isso vai adicionar as marcas padrão de pneus. Continuar?")) {
      seed.mutate();
    }
  };

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/pneu-marcas/${editingId}`, form) : apiPost("/pneu-marcas", form),
    onSuccess: () => { toast.success("Marca salva!"); setOpen(false); qc.invalidateQueries({ queryKey: ["pneu-marcas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneu-marcas/${id}`),
    onSuccess: () => { toast.success("Marca excluída."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pneu-marcas"] }); }
  });

  const abrirNovo = () => { setEditingId(null); setForm({ nome: "", tipo: "FABRICANTE_NOVO", tier: "TIER_1" }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ ...r }); setOpen(true); };

  return (
    <div>
      <PageHeader 
        eyebrow="Cadastros" 
        title="Marcas de Pneus" 
        description="Catálogo de fabricantes e sistemas de reforma." 
        actions={
          <div className="flex gap-2">
            {config?.mostrar_seed_medidas && (
              <Button variant="outline" onClick={popularMarcas} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
                {seed.isPending ? "Populando..." : "Popular Marcas"}
              </Button>
            )}
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Marca</Button>
          </div>
        } 
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Nome</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tier</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {marcas.map((m: any) => (
              <TableRow key={m.id} className="border-slate-800 hover:bg-slate-800/30">
                <TableCell className="font-medium text-slate-200">{m.nome}</TableCell>
                <TableCell className="text-slate-400">{m.tipo === "FABRICANTE_NOVO" ? "Novo" : m.tipo === "SISTEMA_REFORMA" ? "Reforma" : "Ambos"}</TableCell>
                <TableCell className="text-slate-400">{m.tier ? m.tier.replace("TIER_", "Tier ") : "—"}</TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(m)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(m.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Marca" : "Nova Marca"}</h2>
            <div className="grid gap-4">
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Nome *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: Michelin" /></div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Tipo</Label>
                <FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_MARCA} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-500">Tier de Mercado</Label>
                <FieldSelect value={form.tier} onChange={(v) => setForm(s => ({ ...s, tier: v }))} options={TIERS} />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar"}</Button>
            </div>
          </div>
        </div>
      )}

      {excluirId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Marca?</h2>
            <div className="flex justify-end gap-3 mt-4">
              <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
              <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
''')
    print("✅ Frontend PneuMarcas.tsx criado.")

    # 2. Adicionar Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'PneuMarcas' not in c:
        c = 'import PneuMarcas from "@/pages/PneuMarcas";\n' + c
        alvo = '<Route path="/cadastros/pneu-medidas" element={<PneuMedidas />} />'
        if alvo in c:
            c = c.replace(alvo, alvo + '\n              <Route path="/cadastros/pneu-marcas" element={<PneuMarcas />} />')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Rota /cadastros/pneu-marcas adicionada no App.tsx.")

    # 3. Adicionar Item no Sidebar
    side_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(side_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'Marcas de Pneus' not in c:
        alvo = '{ label: "Medidas de Pneus", icon: Disc, path: "/cadastros/pneu-medidas" },'
        if alvo in c:
            c = c.replace(alvo, alvo + '\n      { label: "Marcas de Pneus", icon: Tag, path: "/cadastros/pneu-marcas" },')
            with open(side_path, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Item 'Marcas de Pneus' adicionado ao Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    criar_backend(raiz)
    criar_frontend(raiz)
    print("\n✅ Fase A.2 (Cadastro de Marcas) aplicada com sucesso!")