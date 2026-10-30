import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PNEUS_FASE1_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/models/pneus.py",
        "app/backend/routers/pneus.py",
        "app/backend/models/veiculos.py",
        "app/backend/models/carretas.py",
        "app/backend/server.py",
        "frontend/src/pages/Pneus.tsx",
        "frontend/src/App.tsx",
        "frontend/src/components/layout/Sidebar.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def criar_backend(raiz):
    # 1. Model de Pneus
    model_path = os.path.join(raiz, "app", "backend", "models", "pneus.py")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class PneuCreate(BaseModel):
    numero_fogo: str
    marca: str
    modelo: Optional[str] = None
    medida: str  # Ex: 295/80 R22.5
    dot: Optional[str] = None  # Ex: 4523 (semana 45 de 2023)
    tipo: str = "Tração"  # Direcional, Tração, Misto
    status: str = "Estoque"  # Estoque, Aplicado, Recapagem, Sucateado, Conserto
    custo_aquisicao: float = 0.0
    foto_url: Optional[str] = None
    observacoes: Optional[str] = None

class Pneu(PneuCreate):
    id: str
    created_at: str
    created_by: str
''')
    print("✅ Backend Model: pneus.py criado.")

    # 2. Router de Pneus
    router_path = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.pneus import PneuCreate, Pneu

router = APIRouter(prefix="/pneus", tags=["Pneus"])

@router.get("", response_model=list[Pneu])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.pneus.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Pneu(**d) for d in docs]

@router.post("", response_model=Pneu, status_code=201)
async def criar(body: PneuCreate, user: dict = Depends(require("write"))):
    # Verifica se o número de fogo já existe
    existente = await db.pneus.find_one({"numero_fogo": body.numero_fogo})
    if existente:
        raise HTTPException(409, "Este número de fogo já está cadastrado.")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    doc["created_by"] = user["nome"]
    
    await db.pneus.insert_one(dict(doc))
    return Pneu(**doc)

@router.put("/{id}", response_model=Pneu)
async def atualizar(id: str, body: PneuCreate, user: dict = Depends(require("write"))):
    existe = await db.pneus.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Pneu não encontrado.")
    
    doc = body.model_dump()
    doc["updated_at"] = now_iso()
    doc["updated_by"] = user["nome"]
    
    await db.pneus.update_one({"id": id}, {"$set": doc})
    doc = await db.pneus.find_one({"id": id}, {"_id": 0})
    return Pneu(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.pneus.delete_one({"id": id})
    return {"ok": True}
''')
    print("✅ Backend Router: pneus.py criado.")

    # 3. Adicionar campos de configuração de eixos no Model de Veículos
    veic_model = os.path.join(raiz, "app", "backend", "models", "veiculos.py")
    if os.path.exists(veic_model):
        with open(veic_model, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'configuracao_eixos' not in c:
            c = c.replace(
                'tipo_veiculo',
                'tipo_veiculo: str | None = None\n    configuracao_eixos: str | None = None\n    tipo_tracao: str | None = None'
            )
            with open(veic_model, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Backend: campos de eixos adicionados ao Model de Veículos.")

    # 4. Adicionar campos de configuração de eixos no Model de Carretas
    carr_model = os.path.join(raiz, "app", "backend", "models", "carretas.py")
    if os.path.exists(carr_model):
        with open(carr_model, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'configuracao_eixos' not in c:
            c = c.replace(
                'tipo: str',
                'tipo: str\n    configuracao_eixos: str | None = None'
            )
            with open(carr_model, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Backend: campo de eixos adicionado ao Model de Carretas.")

    # 5. Registrar Router no server.py
    server_path = os.path.join(raiz, "app", "backend", "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'pneus' not in c:
        c = c.replace(
            'from routers import planos_manutencao,',
            'from routers import pneus, planos_manutencao,'
        )
        c = c.replace(
            'api_router.include_router(planos_manutencao.router)',
            'api_router.include_router(planos_manutencao.router)\napi_router.include_router(pneus.router)'
        )
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router de pneus registrado no server.py.")

def criar_frontend(raiz):
    # 1. Criar a página de Pneus
    page_path = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write('''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Disc, Upload, Search } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { brl } from "@/lib/format";

const STATUS_PNEU = ["Estoque", "Aplicado", "Recapagem", "Conserto", "Sucateado"];
const TIPOS_PNEU = ["Direcional", "Tração", "Misto"];

export default function Pneus() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [filtro, setFiltro] = useState("");

  const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });

  const [form, setForm] = useState({
    numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: ""
  });

  const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        ...form,
        custo_aquisicao: Number(String(form.custo_aquisicao).replace(",", ".")) || 0
      };
      return editingId ? apiPut(`/pneus/${editingId}`, payload) : apiPost("/pneus", payload);
    },
    onSuccess: () => {
      toast.success(editingId ? "Pneu atualizado!" : "Pneu cadastrado!");
      setOpen(false); setEditingId(null);
      qc.invalidateQueries({ queryKey: ["pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneus/${id}`),
    onSuccess: () => { toast.success("Pneu excluído."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pneus"] }); }
  });

  const abrirNovo = () => {
    setEditingId(null);
    setForm({ numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: "" });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({ ...r, custo_aquisicao: String(r.custo_aquisicao || "") });
    setOpen(true);
  };

  const pneusFiltrados = pneus.filter((p: any) => {
    if (!filtro) return true;
    return p.numero_fogo.toLowerCase().includes(filtro.toLowerCase()) || p.marca.toLowerCase().includes(filtro.toLowerCase());
  });

  const statusColor = (status: string) => {
    if (status === "Estoque") return "bg-sky-500/20 text-sky-400";
    if (status === "Aplicado") return "bg-emerald-500/20 text-emerald-400";
    if (status === "Recapagem") return "bg-amber-500/20 text-amber-400";
    if (status === "Sucateado") return "bg-rose-500/20 text-rose-400";
    return "bg-slate-800 text-slate-400";
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Controle de Pneus"
        description="Gestão de pneus por número de fogo, marca, DOT e status."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Pneu</Button>}
      />

      <div className="mb-4 flex gap-2">
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
          <Input placeholder="Buscar por número de fogo ou marca..." value={filtro} onChange={(e) => setFiltro(e.target.value)} className="pl-9 h-9" />
        </div>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Nº Fogo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Marca / Modelo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Medida</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">DOT</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Custo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {pneusFiltrados.length === 0 ? (
              <TableRow><TableCell colSpan={8} className="text-center py-8 text-slate-500">Nenhum pneu cadastrado.</TableCell></TableRow>
            ) : (
              pneusFiltrados.map((p: any) => (
                <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="font-bold text-slate-100">{p.numero_fogo}</TableCell>
                  <TableCell className="text-slate-300">{p.marca} {p.modelo && `/ ${p.modelo}`}</TableCell>
                  <TableCell className="text-slate-400 font-mono">{p.medida}</TableCell>
                  <TableCell className="text-slate-400">{p.dot || "—"}</TableCell>
                  <TableCell className="text-slate-400">{p.tipo}</TableCell>
                  <TableCell><span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor(p.status)}`}>{p.status}</span></TableCell>
                  <TableCell className="text-amber-400 font-mono">{brl(p.custo_aquisicao)}</TableCell>
                  <TableCell className="text-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(p)}><Pencil className="size-4 text-sky-400" /></Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(p.id)}><Trash2 className="size-4 text-red-300" /></Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Pneu" : "Novo Pneu"}</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Número de Fogo *</Label>
                <Input value={form.numero_fogo} onChange={(e) => setForm(s => ({ ...s, numero_fogo: e.target.value }))} placeholder="Ex: FOG-10492" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Marca *</Label>
                <Input value={form.marca} onChange={(e) => setForm(s => ({ ...s, marca: e.target.value }))} placeholder="Ex: Michelin" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Modelo</Label>
                <Input value={form.modelo} onChange={(e) => setForm(s => ({ ...s, modelo: e.target.value }))} placeholder="Ex: X Multi Z" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Medida *</Label>
                <Input value={form.medida} onChange={(e) => setForm(s => ({ ...s, medida: e.target.value }))} placeholder="Ex: 295/80 R22.5" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">DOT (Semana/Ano)</Label>
                <Input value={form.dot} onChange={(e) => setForm(s => ({ ...s, dot: e.target.value }))} placeholder="Ex: 4523" maxLength={4} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Tipo</Label>
                <FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_PNEU.map(t => ({ value: t, label: t }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Status</Label>
                <FieldSelect value={form.status} onChange={(v) => setForm(s => ({ ...s, status: v }))} options={STATUS_PNEU.map(s => ({ value: s, label: s }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Custo de Aquisição (R$)</Label>
                <Input value={form.custo_aquisicao} onChange={(e) => setForm(s => ({ ...s, custo_aquisicao: e.target.value }))} placeholder="0,00" />
              </div>
              <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">Observações</Label>
                <Input value={form.observacoes} onChange={(e) => setForm(s => ({ ...s, observacoes: e.target.value }))} placeholder="Ex: Comprado na loja X" />
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
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Pneu?</h2>
            <p className="text-sm text-slate-400 mb-6">Tem certeza que deseja remover este pneu?</p>
            <div className="flex justify-end gap-3">
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
    print("✅ Frontend: Pneus.tsx criado.")

    # 2. Adicionar Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c_app = f.read()
    if 'Pneus' not in c_app:
        c_app = c_app.replace('import Manutencoes from', 'import Pneus from "@/pages/Pneus";\nimport Manutencoes from')
        c_app = c_app.replace('<Route path="/manutencoes"', '<Route path="/pneus" element={<Pneus />} />\n              <Route path="/manutencoes"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c_app)
        print("✅ Frontend: Rota /pneus adicionada no App.tsx.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    criar_backend(raiz)
    criar_frontend(raiz)
    print("\n✅ Fase 1 (Cadastros Base de Pneus) aplicada com sucesso!")