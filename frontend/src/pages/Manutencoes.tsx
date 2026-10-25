import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Wrench, Plus, Trash2, Pencil, CheckCircle2, Clock, AlertCircle, Info } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { brl, dataBR, errMsg } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { useVeiculos } from "@/hooks/useCadastros";
import { useHoje } from "@/hooks/useSession";
import type { Manutencao } from "@/types/manutencoes";

const TODOS = "__all__";
const STATUS = ["Agendada", "Em execução", "Concluída"] as const;
const TIPOS = ["Preventiva", "Corretiva"] as const;

const vazio = (hoje: string) => ({
  veiculo_id: "",
  tipo: "Preventiva",
  status: "Agendada",
  descricao: "",
  data: hoje,
  custo: "",
  oficina: "",
  fornecedor_id: "",
  km_manutencao: "",
  proxima_revisao_km: "",
  pecas_substituidas: "",
});

export default function Manutencoes() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const [filtroVeiculo, setFiltroVeiculo] = useState(TODOS);
  const [filtroStatus, setFiltroStatus] = useState(TODOS);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(() => vazio(""));
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const fq = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const fornecedores = fq.data ?? [];

  const q = useQuery({
    queryKey: ["manutencoes"],
    queryFn: () => apiGet<Manutencao[]>("/manutencoes"),
  });

  const rows = q.isError ? [] : (q.data ?? []);

  const rowsFiltradas = useMemo(() => {
    let filtered = rows;
    if (filtroVeiculo !== TODOS) {
      filtered = filtered.filter(r => r.veiculo_id === filtroVeiculo);
    }
    if (filtroStatus !== TODOS) {
      filtered = filtered.filter(r => r.status === filtroStatus);
    }
    return filtered;
  }, [rows, filtroVeiculo, filtroStatus]);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["manutencoes"] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        ...form,
        custo: Number(form.custo.replace(",", ".")) || 0,
        km_manutencao: form.km_manutencao ? Number(form.km_manutencao) : null,
        proxima_revisao_km: form.proxima_revisao_km ? Number(form.proxima_revisao_km) : null,
      };
      if (editingId) return apiPut<Manutencao>(`/manutencoes/${editingId}`, payload);
      return apiPost<Manutencao>("/manutencoes", payload);
    },
    onSuccess: () => {
      toast.success(editingId ? "Manutenção atualizada" : "Manutenção registrada");
      setOpen(false);
      setEditingId(null);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/manutencoes/${id}`),
    onSuccess: () => {
      toast.success("Manutenção excluída");
      setExcluirId(null);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));

  const handleVeiculoChange = (veiculoId: string) => {
    set("veiculo_id")(veiculoId);
    const v = veiculos.data?.find((x: any) => x.id === veiculoId);
    if (v) {
      setForm(s => ({ ...s, km_manutencao: String(v.hodometro_km || 0) }));
    }
  };
  const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));

  const abrirNovo = () => {
    setEditingId(null);
    setForm(vazio(hoje));
    setOpen(true);
  };

  const abrirEdicao = (r: Manutencao) => {
    setEditingId(r.id);
    setForm({
      veiculo_id: r.veiculo_id,
      tipo: r.tipo,
      status: r.status,
      descricao: r.descricao,
      data: r.data,
      custo: String(r.custo),
      oficina: r.oficina || "",
      fornecedor_id: (r as any).fornecedor_id || "",
      km_manutencao: r.km_manutencao ? String(r.km_manutencao) : "",
      proxima_revisao_km: r.proxima_revisao_km ? String(r.proxima_revisao_km) : "",
      pecas_substituidas: r.pecas_substituidas || "",
    });
    setOpen(true);
  };

  const statusColor = (status: string) => {
    if (status === "Concluída") return "bg-emerald-500/20 text-emerald-400";
    if (status === "Em execução") return "bg-amber-500/20 text-amber-400";
    return "bg-sky-500/20 text-sky-400";
  };

  const statusIcon = (status: string) => {
    if (status === "Concluída") return <CheckCircle2 className="size-3" />;
    if (status === "Em execução") return <Clock className="size-3" />;
    return <AlertCircle className="size-3" />;
  };

  const custoTotal = rowsFiltradas.reduce((s, r) => s + (r.custo || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Manutenções"
        description="Preventivas e corretivas, com custo, oficina e próxima revisão por KM."
        actions={<Button onClick={abrirNovo}><Plus className="size-4" /> Nova manutenção</Button>}
      />

      {/* Cards de Resumo */}
      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-4">
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Total de Manutenções</p>
            <p className="text-2xl font-bold text-slate-100 mt-1">{rowsFiltradas.length}</p>
          </div>
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><Wrench className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Custo Total</p>
            <p className="text-2xl font-bold text-amber-400 mt-1">{brl(custoTotal)}</p>
          </div>
          <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 font-bold">R$</div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Agendadas</p>
            <p className="text-2xl font-bold text-sky-400 mt-1">{rowsFiltradas.filter(r => r.status === 'Agendada').length}</p>
          </div>
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><AlertCircle className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Concluídas</p>
            <p className="text-2xl font-bold text-emerald-400 mt-1">{rowsFiltradas.filter(r => r.status === 'Concluída').length}</p>
          </div>
          <div className="size-10 rounded-lg bg-emerald-500/10 flex items-center justify-center"><CheckCircle2 className="size-5 text-emerald-400" /></div>
        </div>
      </div>

      {/* Filtros */}
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="grid w-64 gap-1.5">
          <Label>Veículo</Label>
          <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} testId="filtro-manutencao-veiculo" />
        </div>
        <div className="grid w-48 gap-1.5">
          <Label>Status</Label>
          <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: TODOS, label: "Todos os status" }, ...STATUS.map(s => ({ value: s, label: s }))]} testId="filtro-manutencao-status" />
        </div>
        {(filtroVeiculo !== TODOS || filtroStatus !== TODOS) && (
          <Button variant="ghost" onClick={() => { setFiltroVeiculo(TODOS); setFiltroStatus(TODOS); }}>Limpar Filtros</Button>
        )}
      </div>

      {/* Tabela */}
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Veículo", "Tipo", "Descrição", "Oficina", "Custo", "Próx. KM", "Status", "Ações"].map((h) => (
                <TableHead key={h} className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-3">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && (
              <TableRow><TableCell colSpan={9} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhuma manutenção encontrada."}</TableCell></TableRow>
            )}
            {rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-mono text-xs whitespace-nowrap px-3">{dataBR(r.data)}</TableCell>
                <TableCell className="font-mono text-xs whitespace-nowrap px-3">{r.veiculo_label?.split(" · ")[0]}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-3">{r.tipo}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-3 max-w-[200px] truncate" title={r.descricao}>{r.descricao}</TableCell>
                <TableCell className="text-xs text-slate-400 px-3 truncate max-w-[120px]">{r.oficina || "—"}</TableCell>
                <TableCell className="tabular-nums text-xs font-medium px-3 text-amber-300">{brl(r.custo)}</TableCell>
                <TableCell className="tabular-nums text-xs px-3 text-sky-300">{r.proxima_revisao_km ? r.proxima_revisao_km.toLocaleString('pt-BR') : "—"}</TableCell>
                <TableCell className="px-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${statusColor(r.status)}`}>
                    {statusIcon(r.status)} {r.status}
                  </span>
                </TableCell>
                <TableCell className="text-center px-3">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Criado por: ${(r as any).criado_por || 'Sistema'}`}>
                      <Info className="size-4 text-slate-400" />
                    </Button>
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

      {/* Dialog de Cadastro/Edição */}
      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2"><Wrench className="size-5 text-sky-400" /> {editingId ? "Editar" : "Nova"} manutenção</DialogTitle>
              <span className="text-xs text-slate-500 flex items-center gap-1"><UserCircle className="size-3"/> {me?.nome || "Usuário"}</span>
            </div>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 grid gap-1.5">
              <Label>Veículo *</Label>
              <FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="manutencao-form-veiculo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Tipo *</Label>
              <FieldSelect value={form.tipo} onChange={set("tipo")} options={TIPOS.map(t => ({ value: t, label: t }))} testId="manutencao-form-tipo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Status *</Label>
              <FieldSelect value={form.status} onChange={set("status")} options={STATUS.map(s => ({ value: s, label: s }))} testId="manutencao-form-status" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Descrição *</Label>
              <Input value={form.descricao} onChange={(e) => set("descricao")(e.target.value)} placeholder="Ex: Troca de óleo" required />
            </div>
            <div className="grid gap-1.5">
              <Label>Data *</Label>
              <Input type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label>Custo (R$)</Label>
              <Input inputMode="decimal" value={form.custo} onChange={(e) => set("custo")(e.target.value)} placeholder="0,00" />
            </div>
            <div className="grid gap-1.5">
              <Label>Oficina / prestador</Label>
              <Input value={form.oficina} onChange={(e) => set("oficina")(e.target.value)} />
            </div>
            <div className="grid gap-1.5">
              <Label>KM na manutenção</Label>
              <Input type="number" value={form.km_manutencao} onChange={(e) => set("km_manutencao")(e.target.value)} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Próxima revisão (KM) — gera alerta</Label>
              <Input type="number" value={form.proxima_revisao_km} onChange={(e) => set("proxima_revisao_km")(e.target.value)} placeholder="Ex: 350000" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Peças substituídas</Label>
              <textarea value={form.pecas_substituidas} onChange={(e) => set("pecas_substituidas")(e.target.value)} className="flex min-h-[60px] w-full rounded-md border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100" placeholder="Liste as peças..." />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={salvar.isPending || !form.veiculo_id || !form.descricao}>{editingId ? "Salvar Alterações" : "Registrar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* ConfirmDialog para Exclusão */}
      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir manutenção?"
        description="Esta ação não pode ser desfeita."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="manutencao-excluir"
      />
    </div>
  );
}
