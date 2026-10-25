import os
import re

def criar_backend_fornecedores(raiz):
    # 1. Modelo
    model_path = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel, Field
from typing import Optional

class FornecedorCreate(BaseModel):
    nome: str = Field(min_length=2)
    cnpj: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    ativo: bool = True

class Fornecedor(FornecedorCreate):
    id: str
''')

    # 2. Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.fornecedores import Fornecedor, FornecedorCreate
import uuid

router = APIRouter(prefix="/fornecedores", tags=["fornecedores"])

@router.get("", response_model=list[Fornecedor])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.fornecedores.find({}, {"_id": 0}).sort("nome", 1).to_list(2000)
    return docs

@router.post("", response_model=Fornecedor, status_code=201)
async def criar(body: FornecedorCreate, _u: dict = Depends(require("write"))):
    if await db.fornecedores.find_one({"nome": body.nome}):
        raise HTTPException(409, "Fornecedor já cadastrado")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.fornecedores.insert_one(doc)
    return doc

@router.put("/{id}", response_model=Fornecedor)
async def atualizar(id: str, body: FornecedorCreate, _u: dict = Depends(require("write"))):
    existe = await db.fornecedores.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Fornecedor não encontrado")
    if await db.fornecedores.find_one({"nome": body.nome, "id": {"$ne": id}}):
        raise HTTPException(409, "Já existe outro fornecedor com este nome")
    
    doc = body.model_dump()
    await db.fornecedores.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    em_uso = await db.manutencoes.find_one({"fornecedor_id": id})
    if em_uso:
        raise HTTPException(400, "Não é possível excluir: fornecedor em uso.")
    await db.fornecedores.delete_one({"id": id})
    return {"ok": True}
''')

    # 3. Registrar no server.py
    server_path = os.path.join(raiz, "app", "backend", "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "fornecedores" not in content:
        content = content.replace("from routers import auth", "from routers import auth, fornecedores")
        content = content.replace("api_router.include_router(auth.router)", "api_router.include_router(auth.router)\napi_router.include_router(fornecedores.router)")
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(content)
    print("✅ Backend de Fornecedores criado.")

def criar_frontend_fornecedores(raiz):
    # 1. Página de Fornecedores
    page_path = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(r'''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Truck, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";

export default function Fornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ nome: "", cnpj: "", telefone: "", email: "", endereco: "", ativo: true });
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const rows = q.data ?? [];

  const salvar = useMutation({
    mutationFn: () => {
      if (editingId) return apiPut(`/fornecedores/${editingId}`, form);
      return apiPost("/fornecedores", form);
    },
    onSuccess: () => {
      toast.success(editingId ? "Fornecedor atualizado" : "Fornecedor cadastrado");
      setOpen(false); setEditingId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] });
    },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/fornecedores/${id}`),
    onSuccess: () => { toast.success("Fornecedor excluído"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao excluir"),
  });

  const abrirNovo = () => { setEditingId(null); setForm({ nome: "", cnpj: "", telefone: "", email: "", endereco: "", ativo: true }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ nome: r.nome, cnpj: r.cnpj || "", telefone: r.telefone || "", email: r.email || "", endereco: r.endereco || "", ativo: r.ativo }); setOpen(true); };

  return (
    <div>
      <PageHeader eyebrow="Cadastros" title="Fornecedores" description="Oficinas, postos e prestadores de serviço." actions={<Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Novo Fornecedor</Button>} />
      
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Nome</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">CNPJ</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Telefone</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && <TableRow><TableCell colSpan={5} className="py-10 text-center text-slate-500">Nenhum fornecedor cadastrado.</TableCell></TableRow>}
            {rows.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-medium text-slate-200">{r.nome}</TableCell>
                <TableCell className="text-slate-400">{r.cnpj || "—"}</TableCell>
                <TableCell className="text-slate-400">{r.telefone || "—"}</TableCell>
                <TableCell>{r.ativo ? <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 text-xs font-bold rounded">Ativo</span> : <span className="bg-slate-500/20 text-slate-400 px-2 py-0.5 text-xs font-bold rounded">Inativo</span>}</TableCell>
                <TableCell className="text-center">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                    <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4" /></Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Truck className="size-5 text-sky-400" /> {editingId ? "Editar Fornecedor" : "Novo Fornecedor"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 grid gap-1.5"><Label>Nome *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} required /></div>
            <div className="grid gap-1.5"><Label>CNPJ</Label><Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Telefone</Label><Input value={form.telefone} onChange={(e) => setForm(s => ({ ...s, telefone: e.target.value }))} /></div>
            <div className="col-span-2 grid gap-1.5"><Label>E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} /></div>
            <div className="col-span-2 grid gap-1.5"><Label>Endereço</Label><Input value={form.endereco} onChange={(e) => setForm(s => ({ ...s, endereco: e.target.value }))} /></div>
            <div className="col-span-2 flex items-center gap-3 mt-2">
              <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-4" />
              <Label>Ativo</Label>
            </div>
            <DialogFooter className="col-span-2 mt-4"><Button type="submit" disabled={salvar.isPending || !form.nome}>{editingId ? "Salvar Alterações" : "Cadastrar"}</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      
      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir fornecedor?" description="Ação irreversível." confirmLabel="Excluir" destructive pending={excluir.isPending} onConfirm={() => excluirId && excluir.mutate(excluirId)} testId="fornecedor-excluir" />
    </div>
  );
}
''')
    # 2. Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()
    if "Fornecedores" not in app_content:
        app_content = app_content.replace("import Combustiveis from", "import Fornecedores from '@/pages/Fornecedores';\nimport Combustiveis from")
        app_content = app_content.replace('<Route path="cadastros/combustiveis"', '<Route path="cadastros/fornecedores" element={<Fornecedores />} />\n          <Route path="cadastros/combustiveis"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_content)

    # 3. Link no Sidebar.tsx
    sidebar_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        sidebar_content = f.read()
    if "fornecedores" not in sidebar_content:
        sidebar_content = sidebar_content.replace('{ label: "Combustíveis", icon: Fuel, path: "/cadastros/combustiveis" },', '{ label: "Combustíveis", icon: Fuel, path: "/cadastros/combustiveis" },\n        { label: "Fornecedores", icon: Truck, path: "/cadastros/fornecedores" },')
        with open(sidebar_path, 'w', encoding='utf-8') as f:
            f.write(sidebar_content)
    print("✅ Frontend de Fornecedores criado e registrado no Menu.")

def integrar_manutencoes(raiz):
    # 1. Atualizar Modelo de Manutenção para ter o fornecedor_id e o usuario
    model_path = os.path.join(raiz, "app", "backend", "models", "manutencoes.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if "fornecedor_id" not in c:
        c = c.replace('oficina: Optional[str] = None', 'oficina: Optional[str] = None\n    fornecedor_id: Optional[str] = None')
    if "criado_por" not in c:
        c = c.replace('id: str\n    veiculo_label: str', 'id: str\n    veiculo_label: str\n    criado_por: str')
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write(c)

    # 2. Atualizar o Router de Manutenção para salvar o usuário e buscar o fornecedor
    router_path = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'doc["criado_por"]' not in c:
        c = c.replace('doc["created_at"] = now_iso()', 'doc["criado_por"] = user.get("nome", "Sistema")\n    doc["created_at"] = now_iso()')
        # Atualizar
        c = c.replace('doc["veiculo_label"] = f"{veiculo[\'placa\']} · {veiculo[\'modelo\']}"', 'doc["veiculo_label"] = f"{veiculo[\'placa\']} · {veiculo[\'modelo\']}"\n    doc["criado_por"] = existe.get("criado_por", user.get("nome", "Sistema"))')
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(c)

    # 3. Atualizar Frontend (Tela de Manutenção)
    page_path = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    with open(page_path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Autopreencher Hodômetro e Motorista
    old_veiculo_change = '''const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));'''
    new_veiculo_change = '''const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));

  const handleVeiculoChange = (veiculoId: string) => {
    set("veiculo_id")(veiculoId);
    const v = veiculos.data?.find((x: any) => x.id === veiculoId);
    if (v) {
      setForm(s => ({ ...s, km_manutencao: String(v.hodometro_km || 0) }));
    }
  };'''
    if 'handleVeiculoChange' not in c:
        c = c.replace(old_veiculo_change, new_veiculo_change)

    # Trocar o FieldSelect do veículo para usar o handleVeiculoChange
    c = c.replace('<FieldSelect value={form.veiculo_id} onChange={set("veiculo_id")} options={veicOpts} placeholder="Selecione o veículo" testId="manutencao-form-veiculo" />', '<FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="manutencao-form-veiculo" />')

    # Mostrar o usuário logado
    if 'useMe' not in c:
        c = c.replace('import { useHoje } from "@/hooks/useSession";', 'import { useHoje, useMe } from "@/hooks/useSession";\nimport { UserCircle } from "lucide-react";')
    if 'const { data: me } = useMe();' not in c:
        c = c.replace('const hoje = useHoje();', 'const hoje = useHoje();\n  const { data: me } = useMe();')
    
    if 'Criado por:' not in c:
        c = c.replace(
            '<DialogTitle className="flex items-center gap-2"><Wrench className="size-5 text-sky-400" /> {editingId ? "Editar" : "Nova"} manutenção</DialogTitle>',
            '''<div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2"><Wrench className="size-5 text-sky-400" /> {editingId ? "Editar" : "Nova"} manutenção</DialogTitle>
              <span className="text-xs text-slate-500 flex items-center gap-1"><UserCircle className="size-3"/> {me?.nome || "Usuário"}</span>
            </div>'''
        )

    # Buscar Fornecedores
    if 'useFornecedores' not in c:
        c = c.replace('const q = useQuery({', 'const fq = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });\n  const fornecedores = fq.data ?? [];\n\n  const q = useQuery({')

    # Trocar Input de Oficina por FieldSelect de Fornecedores
    if 'form.fornecedor_id' not in c:
        c = c.replace(
            '<div className="grid gap-1.5"><Label>Oficina / prestador</Label><Input value={form.oficina} onChange={(e) => set("oficina")(e.target.value)} /></div>',
            '''<div className="grid gap-1.5">
              <Label>Fornecedor / Oficina *</Label>
              <FieldSelect value={form.fornecedor_id} onChange={set("fornecedor_id")} options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} placeholder="Selecione o prestador" testId="manutencao-form-fornecedor" />
            </div>'''
        )
        # Atualizar o estado vazio
        c = c.replace('oficina: "",', 'oficina: "",\n  fornecedor_id: "",')
        # Atualizar o abrirEdicao
        c = c.replace('oficina: r.oficina || "",', 'oficina: r.oficina || "",\n      fornecedor_id: (r as any).fornecedor_id || "",')
    
    # Coluna Criado Por (Info) na tabela
    if 'criado_por' not in c:
        c = c.replace(
            '<TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>',
            '<TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>'
        )
        c = c.replace(
            '<TableCell className="text-center px-3">\n                  <div className="flex gap-1 justify-center">',
            '''<TableCell className="text-center px-3">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Criado por: ${(r as any).criado_por || 'Sistema'}`}>
                      <Info className="size-4 text-slate-400" />
                    </Button>'''
        )
        # Importar Info
        c = c.replace('import { Wrench, Plus, Trash2, Pencil, CheckCircle2, Clock, AlertCircle }', 'import { Wrench, Plus, Trash2, Pencil, CheckCircle2, Clock, AlertCircle, Info }')

    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Tela de Manutenções integrada com Fornecedores e Autopreenchimento.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backend_fornecedores(raiz)
    criar_frontend_fornecedores(raiz)
    integrar_manutencoes(raiz)