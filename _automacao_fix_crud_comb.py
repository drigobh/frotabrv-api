import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "combustiveis.py")
    
    codigo = '''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.combustiveis import Combustivel, CombustivelCreate
import uuid

router = APIRouter(prefix="/combustiveis", tags=["combustiveis"])

@router.get("", response_model=list[Combustivel])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.combustiveis.find({}, {"_id": 0}).sort("nome", 1).to_list(1000)
    return docs

@router.post("", response_model=Combustivel, status_code=201)
async def criar(body: CombustivelCreate, _u: dict = Depends(require("write"))):
    if await db.combustiveis.find_one({"nome": body.nome}):
        raise HTTPException(409, "Combustível já cadastrado")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.combustiveis.insert_one(doc)
    return doc

@router.put("/{id}", response_model=Combustivel)
async def atualizar(id: str, body: CombustivelCreate, _u: dict = Depends(require("write"))):
    existe = await db.combustiveis.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Combustível não encontrado")
    
    # Verifica se o novo nome já existe em outro registro
    if await db.combustiveis.find_one({"nome": body.nome, "id": {"$ne": id}}):
        raise HTTPException(409, "Já existe outro combustível com este nome")
    
    doc = body.model_dump()
    await db.combustiveis.update_one({"id": id}, {"$set": doc})
    doc["id"] = id
    return doc

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    # Verifica se está em uso em algum abastecimento
    em_uso = await db.abastecimentos.find_one({"combustivel_id": id})
    if em_uso:
        raise HTTPException(400, "Não é possível excluir: combustível em uso em abastecimentos.")
    
    await db.combustiveis.delete_one({"id": id})
    return {"ok": True}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Backend atualizado com PUT e DELETE.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Combustiveis.tsx")
    
    codigo = r'''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";

export default function Combustiveis() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ nome: "", is_arla: false });
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["combustiveis"], queryFn: () => apiGet<any[]>("/combustiveis") });
  const rows = q.data ?? [];

  const salvar = useMutation({
    mutationFn: () => {
      if (editingId) return apiPut(`/combustiveis/${editingId}`, { ...form, ativo: true });
      return apiPost("/combustiveis", { ...form, ativo: true });
    },
    onSuccess: () => {
      toast.success(editingId ? "Combustível atualizado" : "Combustível cadastrado");
      setOpen(false);
      setEditingId(null);
      qc.invalidateQueries({ queryKey: ["combustiveis"] });
    },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/combustiveis/${id}`),
    onSuccess: () => {
      toast.success("Combustível excluído");
      setExcluirId(null);
      qc.invalidateQueries({ queryKey: ["combustiveis"] });
    },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao excluir"),
  });

  const abrirNovo = () => {
    setEditingId(null);
    setForm({ nome: "", is_arla: false });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({ nome: r.nome, is_arla: r.is_arla });
    setOpen(true);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Tipos de Combustível"
        description="Gerencie os combustíveis. Arla não entra no cálculo de média de consumo."
        actions={
          <Button onClick={abrirNovo}>
            <Plus className="size-4 mr-2" /> Novo Combustível
          </Button>
        }
      />

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Nome</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Cálculo de Média</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow>
                <TableCell colSpan={3} className="py-10 text-center text-slate-500">
                  Nenhum combustível cadastrado.
                </TableCell>
              </TableRow>
            )}
            {rows.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-medium text-slate-200">{r.nome}</TableCell>
                <TableCell>
                  {r.is_arla ? (
                    <span className="inline-flex items-center rounded bg-amber-500/20 px-2 py-0.5 text-xs font-bold text-amber-400">
                      Ignorado (Arla)
                    </span>
                  ) : (
                    <span className="inline-flex items-center rounded bg-emerald-500/20 px-2 py-0.5 text-xs font-bold text-emerald-400">
                      Entra no Cálculo
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)} aria-label="Editar">
                      <Pencil className="size-4 text-sky-400" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)} aria-label="Excluir">
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Fuel className="size-5 text-sky-400" />
              {editingId ? "Editar Combustível" : "Novo Combustível"}
            </DialogTitle>
          </DialogHeader>
          <form className="grid gap-4 py-4" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="grid gap-1.5">
              <Label htmlFor="comb-nome">Nome do Combustível *</Label>
              <Input id="comb-nome" value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: Diesel S-10" required />
            </div>
            <div className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-950/50 p-3">
              <input 
                type="checkbox" 
                id="comb-arla"
                checked={form.is_arla} 
                onChange={(e) => setForm(s => ({ ...s, is_arla: e.target.checked }))} 
                className="size-5 cursor-pointer accent-amber-500" 
              />
              <div>
                <Label htmlFor="comb-arla" className="cursor-pointer font-medium text-slate-200">É Arla 32?</Label>
                <p className="text-xs text-slate-500">Se marcado, este combustível não será usado no cálculo de KM/L.</p>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={salvar.isPending || !form.nome}>
                {editingId ? "Salvar Alterações" : "Cadastrar"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir combustível?"
        description="Se houver abastecimentos vinculados a este combustível, a exclusão será bloqueada."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="combustivel-excluir"
      />
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend atualizado com os botões de Editar e Excluir.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)