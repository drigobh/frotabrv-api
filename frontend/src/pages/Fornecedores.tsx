import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Building2, User, MapPin, Star, Pencil, Trash2, Plus, Search, AlertTriangle, Wrench } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function Fornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const [filtroNome, setFiltroNome] = useState("");
  const [filtroCidade, setFiltroCidade] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("__all__");
  const [filtroStatus, setFiltroStatus] = useState("__all__");
  const [filtroTipoForn, setFiltroTipoForn] = useState("__all__");

  const [form, setForm] = useState({
    nome: "", tipo_fornecedor_id: "", documento: "", tipo_pessoa: "PJ",
    telefone: "", email: "", endereco: "", bairro: "", cidade: "", estado: "",
    avaliacao: 0, ativo: true
  });

  const { data: fornecedores = [], refetch } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });

  const rowsFiltradas = useMemo(() => {
    let filtered = fornecedores;
    if (filtroNome) filtered = filtered.filter(f => f.nome.toLowerCase().includes(filtroNome.toLowerCase()) || (f.documento && f.documento.includes(filtroNome)));
    if (filtroCidade) filtered = filtered.filter(f => f.cidade && f.cidade.toLowerCase().includes(filtroCidade.toLowerCase()));
    if (filtroTipo !== "__all__") filtered = filtered.filter(f => f.tipo_pessoa === filtroTipo);
    if (filtroStatus !== "__all__") filtered = filtered.filter(f => f.ativo === (filtroStatus === "ativo"));
    if (filtroTipoForn !== "__all__") filtered = filtered.filter(f => f.tipo_fornecedor_id === filtroTipoForn);
    return filtered;
  }, [fornecedores, filtroNome, filtroCidade, filtroTipo, filtroStatus, filtroTipoForn]);

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/fornecedores/${editingId}`, form) : apiPost("/fornecedores", form),
    onSuccess: () => { toast.success("Fornecedor salvo"); setOpen(false); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/fornecedores/${id}`),
    onSuccess: () => { toast.success("Fornecedor excluído"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao excluir"),
  });

  const preencherTiposEmMassa = async () => {
    if (!confirm("Isso vai preencher o tipo 'Combustíveis e lubrificantes' em TODOS os fornecedores sem tipo. Continuar?")) return;
    const tipoAlvo = tipos.find((t: any) => t.nome.toLowerCase().includes("combustíveis e lubrificantes"));
    if (!tipoAlvo) return toast.error("Tipo não encontrado.");
    const semTipo = rowsFiltradas.filter(r => !r.tipo_fornecedor_id);
    let count = 0;
    for (const f of semTipo) {
      try {
        await apiPut(`/fornecedores/${f.id}`, { ...f, tipo_fornecedor_id: tipoAlvo.id });
        count++;
      } catch (e) {}
    }
    toast.success(`${count} fornecedores atualizados.`);
    qc.invalidateQueries({ queryKey: ["fornecedores"] });
  };

  const abrirNovo = () => {
    setEditingId(null);
    setForm({ nome: "", tipo_fornecedor_id: "", documento: "", tipo_pessoa: "PJ", telefone: "", email: "", endereco: "", bairro: "", cidade: "", estado: "", avaliacao: 0, ativo: true });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({
      nome: r.nome, tipo_fornecedor_id: r.tipo_fornecedor_id || "", documento: r.documento || "", tipo_pessoa: r.tipo_pessoa || "PJ",
      telefone: r.telefone || "", email: r.email || "", endereco: r.endereco || "", bairro: r.bairro || "", cidade: r.cidade || "", estado: r.estado || "",
      avaliacao: r.avaliacao || 0, ativo: r.ativo
    });
    setOpen(true);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Fornecedores"
        description="Gerencie oficinas, postos e prestadores de serviço."
        actions={<div className="flex gap-2">
          <Button variant="outline" onClick={preencherTiposEmMassa} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
            <Wrench className="size-4 mr-2" /> Preencher Tipos em Massa
          </Button>
          <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Fornecedor</Button>
        </div>}
      />

      <div className="mb-4 grid grid-cols-1 md:grid-cols-5 gap-2">
        <Input placeholder="Buscar por Nome ou Documento..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} className="h-9" />
        <Input placeholder="Cidade..." value={filtroCidade} onChange={(e) => setFiltroCidade(e.target.value)} className="h-9" />
        <FieldSelect value={filtroTipo} onChange={setFiltroTipo} options={[{ value: "__all__", label: "PJ e PF" }, { value: "PJ", label: "Apenas PJ" }, { value: "PF", label: "Apenas PF" }]} />
        <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: "__all__", label: "Todos os Status" }, { value: "ativo", label: "Apenas Ativos" }, { value: "inativo", label: "Apenas Inativos" }]} />
        <FieldSelect value={filtroTipoForn} onChange={setFiltroTipoForn} options={[{ value: "__all__", label: "Todos os Tipos" }, ...tipos.filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))]} />
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo de Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Localização</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Avaliação</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && (
              <TableRow><TableCell colSpan={6} className="py-10 text-center text-slate-500">Nenhum fornecedor encontrado.</TableCell></TableRow>
            )}
            {rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-medium text-slate-200">
                  <div className="flex items-center gap-2">
                    {r.tipo_pessoa === 'PJ' ? <Building2 className="size-4 text-sky-400" /> : <User className="size-4 text-purple-400" />}
                    <div>
                      <div className="flex items-center gap-2">{r.nome}<span className="text-[9px] font-bold bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{r.tipo_pessoa}</span></div>
                      <div className="text-slate-500 font-mono text-xs">{r.documento || "—"}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-xs text-slate-400">
                  {tipos.find((t: any) => t.id === r.tipo_fornecedor_id)?.nome || "—"}
                </TableCell>
                <TableCell className="text-slate-400 text-xs">
                  <div className="flex flex-col gap-1">
                    <span className="flex items-center gap-1"><MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}</span>
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex justify-center gap-0.5">
                    {[1, 2, 3, 4, 5].map(star => (
                      <Star key={star} className={`size-3 ${star <= (r.avaliacao || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-700'}`} />
                    ))}
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${r.ativo ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                    {r.ativo ? "Ativo" : "Inativo"}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle>{editingId ? "Editar Fornecedor" : "Novo Fornecedor"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 grid gap-1">
              <Label className="text-xs">Tipo de Fornecedor *</Label>
              <FieldSelect value={form.tipo_fornecedor_id} onChange={(v) => setForm(s => ({ ...s, tipo_fornecedor_id: v }))} options={tipos.filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))} placeholder="Selecione o tipo..." />
            </div>

            <div className="col-span-2 grid gap-1">
              <Label className="text-xs">Nome / Razão Social *</Label>
              <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} className="h-9" required />
            </div>

            <div className="grid gap-1">
              <Label className="text-xs">Documento / CNPJ</Label>
              <Input value={form.documento} onChange={(e) => setForm(s => ({ ...s, documento: e.target.value }))} className="h-9" />
            </div>
            <div className="grid gap-1">
              <Label className="text-xs">Tipo Pessoa</Label>
              <FieldSelect value={form.tipo_pessoa} onChange={(v) => setForm(s => ({ ...s, tipo_pessoa: v }))} options={[{ value: "PJ", label: "PJ" }, { value: "PF", label: "PF" }]} />
            </div>

            <div className="grid gap-1"><Label className="text-xs">Telefone</Label><Input value={form.telefone} onChange={(e) => setForm(s => ({ ...s, telefone: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9" /></div>

            <div className="col-span-2 grid gap-1"><Label className="text-xs">Endereço</Label><Input value={form.endereco} onChange={(e) => setForm(s => ({ ...s, endereco: e.target.value }))} className="h-9" /></div>

            <div className="grid gap-1"><Label className="text-xs">Bairro</Label><Input value={form.bairro} onChange={(e) => setForm(s => ({ ...s, bairro: e.target.value }))} className="h-9" /></div>
            <div className="grid grid-cols-3 gap-1">
              <div className="col-span-2 grid gap-1"><Label className="text-xs">Cidade</Label><Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} className="h-9" /></div>
              <div className="grid gap-1"><Label className="text-xs">UF</Label><Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="uppercase h-9" /></div>
            </div>

            <div className="col-span-2 grid gap-1">
              <Label className="text-xs">Avaliação</Label>
              <div className="flex gap-1 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-5 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
              </div>
            </div>

            <div className="col-span-2 flex items-center gap-2 mt-1">
              <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-3.5" />
              <Label className="text-xs">Ativo</Label>
            </div>

            <DialogFooter className="col-span-2 mt-2">
              <Button type="submit" className="h-9" disabled={salvar.isPending || !form.nome || !form.tipo_fornecedor_id}>{editingId ? "Salvar" : "Cadastrar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir Fornecedor?" onConfirm={() => excluirId && excluir.mutate(excluirId)} confirmLabel="Excluir" destructive pending={excluir.isPending} />
    </div>
  );
}
