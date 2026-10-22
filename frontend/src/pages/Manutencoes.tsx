import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus, Trash2, Wrench } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { brl, dataBR, errMsg, num } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { StatusBadge, type Tone } from "@/components/common/StatusBadge";
import { useVeiculos } from "@/hooks/useCadastros";
import { useHoje, useMe } from "@/hooks/useSession";
import { STATUS_MANUTENCAO, type Manutencao, type ManutencaoCreate, type StatusManutencao, type TipoManutencao } from "@/types/manutencoes";

type Filtro = "todas" | StatusManutencao;
const TOM: Record<StatusManutencao, Tone> = { agendada: "info", em_execucao: "desacoplado", concluida: "ativo" };

interface FormState {
  veiculo_id: string;
  tipo: TipoManutencao;
  descricao: string;
  oficina: string;
  custo: string;
  data: string;
  km: string;
  pecas: string;
  status: StatusManutencao;
  proxima_km: string;
}

const vazio = (hoje: string): FormState => ({
  veiculo_id: "", tipo: "preventiva", descricao: "", oficina: "", custo: "", data: hoje, km: "", pecas: "", status: "agendada", proxima_km: "",
});

const fromRow = (m: Manutencao): FormState => ({
  veiculo_id: m.veiculo_id, tipo: m.tipo, descricao: m.descricao, oficina: m.oficina, custo: String(m.custo), data: m.data,
  km: m.km != null ? String(m.km) : "", pecas: m.pecas, status: m.status, proxima_km: m.proxima_km != null ? String(m.proxima_km) : "",
});

const toPayload = (f: FormState): ManutencaoCreate => ({
  ...f,
  custo: Number(f.custo.replace(",", ".") || 0),
  km: f.km ? Number(f.km) : null,
  proxima_km: f.proxima_km ? Number(f.proxima_km) : null,
});

export default function Manutencoes() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const [filtro, setFiltro] = useState<Filtro>("todas");
  const [editando, setEditando] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<FormState>(() => vazio(""));
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<Manutencao[]>("/manutencoes") });
  const todas = q.isError ? [] : (q.data ?? []);
  const rows = useMemo(() => (filtro === "todas" ? todas : todas.filter((m) => m.status === filtro)), [todas, filtro]);
  const custoTotal = rows.reduce((s, m) => s + m.custo, 0);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["manutencoes"] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
    void qc.invalidateQueries({ queryKey: ["financeiro"] });
  };

  const salvar = useMutation({
    mutationFn: ({ id, body }: { id: string | null; body: ManutencaoCreate }) =>
      id ? apiPut<Manutencao>(`/manutencoes/${id}`, body) : apiPost<Manutencao>("/manutencoes", body),
    onSuccess: (_d, vars) => {
      toast.success(vars.id ? "Manutenção atualizada" : "Manutenção registrada");
      setOpen(false);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/manutencoes/${id}`),
    onSuccess: () => { toast.success("Manutenção excluída"); setExcluirId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });

  const set = <K extends keyof FormState>(k: K) => (v: FormState[K]) => setForm((s) => ({ ...s, [k]: v }));
  const contagem = (s: StatusManutencao) => todas.filter((m) => m.status === s).length;

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Manutenções"
        description="Preventivas e corretivas, com custo, oficina e próxima revisão por KM (gera alerta no dashboard)."
        actions={
          <Button onClick={() => { setEditando(null); setForm(vazio(hoje)); setOpen(true); }} data-testid="manutencao-new-button">
            <Plus className="size-4" /> Nova manutenção
          </Button>
        }
      />

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <Tabs value={filtro} onValueChange={(v) => setFiltro(v as Filtro)}>
          <TabsList>
            <TabsTrigger value="todas" data-testid="manutencao-tab-todas">Todas ({todas.length})</TabsTrigger>
            {(Object.keys(STATUS_MANUTENCAO) as StatusManutencao[]).map((s) => (
              <TabsTrigger key={s} value={s} data-testid={`manutencao-tab-${s}`}>{STATUS_MANUTENCAO[s]} ({contagem(s)})</TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
        <p className="text-sm text-slate-400">Custo no filtro: <span className="font-semibold text-slate-100" data-testid="manutencao-custo-total">{brl(custoTotal)}</span></p>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="manutencao-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Veículo", "Tipo", "Descrição", "Oficina", "Custo", "Próx. KM", "Status", ""].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={9} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhuma manutenção encontrada."}</TableCell></TableRow>
            )}
            {rows.map((m) => (
              <TableRow key={m.id} className="border-slate-800/70" data-testid={`manutencao-row-${m.id}`}>
                <TableCell className="font-mono text-sm">{dataBR(m.data)}</TableCell>
                <TableCell className="font-mono">{m.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell>
                  <span className={m.tipo === "preventiva" ? "text-sky-300" : "text-amber-300"}>{m.tipo === "preventiva" ? "Preventiva" : "Corretiva"}</span>
                </TableCell>
                <TableCell className="max-w-[260px] truncate">{m.descricao}</TableCell>
                <TableCell className="text-slate-400">{m.oficina || "—"}</TableCell>
                <TableCell className="tabular-nums">{brl(m.custo)}</TableCell>
                <TableCell className="font-mono tabular-nums">{m.proxima_km != null ? num(m.proxima_km) : "—"}</TableCell>
                <TableCell><StatusBadge tone={TOM[m.status]} testId={`manutencao-status-${m.id}`}>{STATUS_MANUTENCAO[m.status]}</StatusBadge></TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button size="icon-sm" variant="ghost" onClick={() => { setEditando(m.id); setForm(fromRow(m)); setOpen(true); }} aria-label="Editar" data-testid={`manutencao-edit-${m.id}`}>
                      <Pencil className="size-4" />
                    </Button>
                    {me?.perfil === "admin" && (
                      <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(m.id)} aria-label="Excluir" data-testid={`manutencao-delete-${m.id}`}>
                        <Trash2 className="size-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-xl" data-testid="manutencao-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Wrench className="size-5 text-amber-400" /> {editando ? "Editar manutenção" : "Nova manutenção"}</DialogTitle>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate({ id: editando, body: toPayload(form) }); }}>
            <div className="col-span-2 grid gap-1.5">
              <Label>Veículo *</Label>
              <FieldSelect value={form.veiculo_id} onChange={set("veiculo_id")} options={(veiculos.data ?? []).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }))} placeholder="Selecione o veículo" testId="manutencao-form-veiculo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Tipo *</Label>
              <FieldSelect value={form.tipo} onChange={(v) => set("tipo")(v as TipoManutencao)} options={[{ value: "preventiva", label: "Preventiva" }, { value: "corretiva", label: "Corretiva" }]} testId="manutencao-form-tipo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Status *</Label>
              <FieldSelect value={form.status} onChange={(v) => set("status")(v as StatusManutencao)} options={(Object.keys(STATUS_MANUTENCAO) as StatusManutencao[]).map((s) => ({ value: s, label: STATUS_MANUTENCAO[s] }))} testId="manutencao-form-status" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="mn-desc">Descrição *</Label>
              <Input id="mn-desc" value={form.descricao} onChange={(e) => set("descricao")(e.target.value)} required data-testid="manutencao-form-descricao" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="mn-data">Data *</Label>
              <Input id="mn-data" type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required data-testid="manutencao-form-data" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="mn-custo">Custo (R$)</Label>
              <Input id="mn-custo" inputMode="decimal" value={form.custo} onChange={(e) => set("custo")(e.target.value)} data-testid="manutencao-form-custo" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="mn-oficina">Oficina / prestador</Label>
              <Input id="mn-oficina" value={form.oficina} onChange={(e) => set("oficina")(e.target.value)} data-testid="manutencao-form-oficina" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="mn-km">KM na manutenção</Label>
              <Input id="mn-km" type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} data-testid="manutencao-form-km" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="mn-prox">Próxima revisão (KM) — gera alerta</Label>
              <Input id="mn-prox" type="number" value={form.proxima_km} onChange={(e) => set("proxima_km")(e.target.value)} data-testid="manutencao-form-proxima-km" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="mn-pecas">Peças substituídas</Label>
              <Textarea id="mn-pecas" rows={2} value={form.pecas} onChange={(e) => set("pecas")(e.target.value)} data-testid="manutencao-form-pecas" />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={salvar.isPending || !form.veiculo_id} data-testid="manutencao-form-submit">Salvar</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir manutenção?"
        description="Esta ação é registrada na auditoria e não pode ser desfeita."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="manutencao-excluir"
      />
    </div>
  );
}
