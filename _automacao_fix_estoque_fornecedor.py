import os

def fix_backend_model(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "pecas.py")
    codigo = '''from pydantic import BaseModel, Field
from typing import Optional

class PecaCreate(BaseModel):
    nome: str = Field(min_length=2)
    codigo: Optional[str] = None
    preco_custo: float = 0.0
    quantidade_estoque: int = 0
    estoque_minimo: int = 5
    fornecedor_id: Optional[str] = None
    ativo: bool = True

class Peca(PecaCreate):
    id: str
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Backend: Modelo de Peças atualizado com fornecedor_id.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    
    codigo = r'''import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Package, Plus, Pencil, Trash2, AlertTriangle, CheckCircle2, Search } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { brl } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function Estoque() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [busca, setBusca] = useState("");

  const [form, setForm] = useState({ nome: "", codigo: "", preco_custo: "", quantidade_estoque: "", estoque_minimo: "5", fornecedor_id: "", ativo: true });

  const q = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas") });
  const fornQ = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  
  const rows = q.data ?? [];
  const fornecedores = fornQ.data ?? [];

  const rowsFiltradas = useMemo(() => {
    return rows.filter(r => r.nome.toLowerCase().includes(busca.toLowerCase()) || (r.codigo && r.codigo.toLowerCase().includes(busca.toLowerCase())));
  }, [rows, busca]);

  const salvar = useMutation({
    mutationFn: () => {
      const payload = { 
        ...form, 
        preco_custo: Number(form.preco_custo.replace(",", ".")) || 0, 
        quantidade_estoque: Number(form.quantidade_estoque) || 0, 
        estoque_minimo: Number(form.estoque_minimo) || 0 
      };
      if (editingId) return apiPut(`/pecas/${editingId}`, payload);
      return apiPost("/pecas", payload);
    },
    onSuccess: () => { 
      toast.success(editingId ? "Peça atualizada" : "Peça cadastrada"); 
      setOpen(false); 
      setEditingId(null); 
      qc.invalidateQueries({ queryKey: ["pecas"] }); 
    },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pecas/${id}`),
    onSuccess: () => { 
      toast.success("Peça excluída"); 
      setExcluirId(null); 
      qc.invalidateQueries({ queryKey: ["pecas"] }); 
    },
    onError: (e: any) => toast.error(e.message || "Erro ao excluir"),
  });

  const abrirNovo = () => { 
    setEditingId(null); 
    setForm({ nome: "", codigo: "", preco_custo: "", quantidade_estoque: "", estoque_minimo: "5", fornecedor_id: "", ativo: true }); 
    setOpen(true); 
  };

  const abrirEdicao = (r: any) => { 
    setEditingId(r.id); 
    setForm({ 
      nome: r.nome, codigo: r.codigo || "", preco_custo: String(r.preco_custo), 
      quantidade_estoque: String(r.quantidade_estoque), estoque_minimo: String(r.estoque_minimo), 
      fornecedor_id: r.fornecedor_id || "", ativo: r.ativo 
    }); 
    setOpen(true); 
  };

  const totalItens = rows.length;
  const valorTotal = rows.reduce((s, r) => s + (r.preco_custo * r.quantidade_estoque), 0);
  const itensBaixos = rows.filter(r => r.quantidade_estoque <= r.estoque_minimo).length;

  return (
    <div>
      <PageHeader 
        eyebrow="Operação" 
        title="Estoque de Peças" 
        description="Controle de almoxarifado." 
        actions={<Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Nova Peça</Button>} 
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-4">
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div><p className="text-xs text-slate-500 font-medium">Total de Itens</p><p className="text-2xl font-bold text-slate-100 mt-1">{totalItens}</p></div>
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><Package className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div><p className="text-xs text-slate-500 font-medium">Valor do Estoque</p><p className="text-2xl font-bold text-amber-400 mt-1">{brl(valorTotal)}</p></div>
          <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center font-bold text-amber-400">R$</div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div><p className="text-xs text-slate-500 font-medium">Estoque Baixo</p><p className="text-2xl font-bold text-red-400 mt-1">{itensBaixos}</p></div>
          <div className="size-10 rounded-lg bg-red-500/10 flex items-center justify-center"><AlertTriangle className="size-5 text-red-400" /></div>
        </div>
      </div>

      <div className="mb-4">
        <div className="relative w-72">
          <Search className="absolute left-2 top-2.5 size-4 text-slate-500" />
          <Input placeholder="Buscar peça..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-8" />
        </div>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Peça / Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Atual</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Mínima</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-right">Preço Custo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-right">Valor Total</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && <TableRow><TableCell colSpan={7} className="py-10 text-center text-slate-500">Nenhuma peça cadastrada.</TableCell></TableRow>}
            {rowsFiltradas.map((r) => {
              const estoqueBaixo = r.quantidade_estoque <= r.estoque_minimo;
              const forn = fornecedores.find((f: any) => f.id === r.fornecedor_id);
              return (
                <TableRow key={r.id} className="border-slate-800/70">
                  <TableCell className="font-medium text-slate-200">
                    <div>{r.nome}</div>
                    <div className="text-slate-500 font-mono text-xs">{r.codigo || "—"}</div>
                    {forn && <div className="text-[10px] text-sky-400 mt-0.5">Fornecedor: {forn.nome}</div>}
                  </TableCell>
                  <TableCell className={`text-center font-bold ${estoqueBaixo ? 'text-red-400' : 'text-emerald-400'}`}>{r.quantidade_estoque}</TableCell>
                  <TableCell className="text-center text-slate-400">{r.estoque_minimo}</TableCell>
                  <TableCell className="text-right text-slate-300">{brl(r.preco_custo)}</TableCell>
                  <TableCell className="text-right font-medium text-slate-200">{brl(r.preco_custo * r.quantidade_estoque)}</TableCell>
                  <TableCell className="text-center">
                    {estoqueBaixo ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400"><AlertTriangle className="size-3" /> Baixo</span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400"><CheckCircle2 className="size-3" /> OK</span>
                    )}
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="flex gap-1 justify-center">
                      <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                      <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4" /></Button>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Package className="size-5 text-sky-400" /> {editingId ? "Editar Peça" : "Nova Peça"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 grid gap-1.5"><Label>Nome da Peça *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} required /></div>
            <div className="col-span-2 grid gap-1.5"><Label>Código / Referência</Label><Input value={form.codigo} onChange={(e) => setForm(s => ({ ...s, codigo: e.target.value }))} /></div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Fornecedor</Label>
              <FieldSelect 
                value={form.fornecedor_id} 
                onChange={(v) => setForm(s => ({ ...s, fornecedor_id: v }))} 
                options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} 
                placeholder="Selecione o fornecedor" 
              />
            </div>
            <div className="grid gap-1.5"><Label>Preço de Custo (R$)</Label><Input inputMode="decimal" value={form.preco_custo} onChange={(e) => setForm(s => ({ ...s, preco_custo: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Qtd. em Estoque</Label><Input type="number" value={form.quantidade_estoque} onChange={(e) => setForm(s => ({ ...s, quantidade_estoque: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Estoque Mínimo</Label><Input type="number" value={form.estoque_minimo} onChange={(e) => setForm(s => ({ ...s, estoque_minimo: e.target.value }))} /></div>
            <div className="flex items-center gap-2 mt-6">
              <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-4" />
              <Label>Peça Ativa</Label>
            </div>
            <DialogFooter className="col-span-2 mt-4"><Button type="submit" disabled={salvar.isPending || !form.nome}>{editingId ? "Salvar" : "Cadastrar"}</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir peça?" description="Ação irreversível." confirmLabel="Excluir" destructive pending={excluir.isPending} onConfirm={() => excluirId && excluir.mutate(excluirId)} testId="peca-excluir" />
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend: Tela de Estoque atualizada com Fornecedores.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend_model(raiz)
    fix_frontend(raiz)