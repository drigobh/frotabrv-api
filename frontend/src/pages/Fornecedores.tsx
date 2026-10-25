import { useState } from "react";
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

export function validaCNPJ(cnpj: string) {
  cnpj = cnpj.replace(/[^\d]/g, '');
  if (cnpj.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(cnpj)) return false;
  
  let tamanho = cnpj.length - 2;
  let numeros = cnpj.substring(0, tamanho);
  let digitos = cnpj.substring(tamanho);
  let soma = 0;
  let pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
  if (resultado != parseInt(digitos.charAt(0))) return false;
  
  tamanho = tamanho + 1;
  numeros = cnpj.substring(0, tamanho);
  soma = 0;
  pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
  if (resultado != parseInt(digitos.charAt(1))) return false;
  
  return true;
}

export default function Fornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState({ nome: "", cnpj: "", telefone: "", email: "", endereco: "", ativo: true });
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [buscandoCnpj, setBuscandoCnpj] = useState(false);

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

  const buscarCnpj = async () => {
    const cnpjLimpo = form.cnpj.replace(/[^\d]/g, '');
    if (cnpjLimpo.length !== 14) {
      toast.error("CNPJ inválido.");
      return;
    }
    if (!validaCNPJ(cnpjLimpo)) {
      toast.error("CNPJ matematicamente inválido.");
      return;
    }
    
    setBuscandoCnpj(true);
    try {
      const res = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpjLimpo}`);
      if (!res.ok) throw new Error("Erro ao buscar CNPJ");
      const data = await res.json();
      
      setForm(s => ({
        ...s,
        nome: data.razao_social || s.nome,
        telefone: data.ddd_telefone_1 || s.telefone,
        email: data.email || s.email,
        endereco: `${data.logradouro}, ${data.numero} - ${data.bairro}, ${data.municipio} - ${data.uf}` || s.endereco
      }));
      toast.success("Dados do CNPJ carregados!");
    } catch (error) {
      toast.error("Não foi possível buscar o CNPJ.");
    } finally {
      setBuscandoCnpj(false);
    }
  };

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
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { 
              e.preventDefault(); 
              if (form.cnpj && !validaCNPJ(form.cnpj)) {
                toast.error("O CNPJ informado é inválido.");
                return;
              }
              salvar.mutate(); 
            }}>
            <div className="col-span-2 grid gap-1.5"><Label>Nome *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} required /></div>
            <div className="grid gap-1.5">
              <Label>CNPJ</Label>
              <div className="flex gap-2">
                <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: e.target.value }))} placeholder="00.000.000/0000-00" />
                <Button type="button" variant="secondary" onClick={buscarCnpj} disabled={buscandoCnpj || !form.cnpj}>
                  {buscandoCnpj ? "Buscando..." : "Buscar"}
                </Button>
              </div>
            </div>
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
