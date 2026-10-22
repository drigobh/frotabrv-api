import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, Plus, Search, Trash2, Undo2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost } from "@/lib/api";
import { brl, dataBR, errMsg } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useVeiculos } from "@/hooks/useCadastros";
import { useHoje, useMe } from "@/hooks/useSession";
import { ORIGEM_LABEL, type Conta, type ContaCreate, type TipoConta } from "@/types/financeiro";

type Filtro = "abertas" | "vencidas" | "pagas" | "todas";
const SEM_VEICULO = "__none__";

export function ContasTab({ tipo }: { tipo: TipoConta }) {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const [filtro, setFiltro] = useState<Filtro>("abertas");
  const [busca, setBusca] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ descricao: "", categoria: "", veiculo_id: SEM_VEICULO, valor: "", vencimento: "" });
  const [baixa, setBaixa] = useState<{ conta: Conta; data: string } | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const pagar = tipo === "pagar";
  const p = pagar ? "pagar" : "receber";

  const q = useQuery({ queryKey: ["financeiro", "contas", tipo], queryFn: () => apiGet<Conta[]>(`/financeiro/contas?tipo=${tipo}`) });
  const todas = q.isError ? [] : (q.data ?? []);
  const termo = busca.trim().toLowerCase();
  const rows = useMemo(() => {
    const base = todas.filter((c) => !termo || `${c.descricao} ${c.veiculo_label ?? ""} ${c.categoria}`.toLowerCase().includes(termo));
    if (filtro === "abertas") return base.filter((c) => c.status === "aberta").sort((a, b) => a.vencimento.localeCompare(b.vencimento));
    if (filtro === "vencidas") return base.filter((c) => c.vencida).sort((a, b) => a.vencimento.localeCompare(b.vencimento));
    if (filtro === "pagas") return base.filter((c) => c.status === "paga");
    return base;
  }, [todas, filtro, termo]);
  const total = rows.reduce((s, c) => s + c.valor, 0);
  const n = (f: Filtro) => (f === "abertas" ? todas.filter((c) => c.status === "aberta") : f === "vencidas" ? todas.filter((c) => c.vencida) : f === "pagas" ? todas.filter((c) => c.status === "paga") : todas).length;

  const invalidate = () => void qc.invalidateQueries({ queryKey: ["financeiro"] });
  const onError = (e: unknown) => toast.error(errMsg(e));

  const criar = useMutation({
    mutationFn: (body: ContaCreate) => apiPost<Conta>("/financeiro/contas", body),
    onSuccess: () => { toast.success("Conta lançada"); setOpen(false); invalidate(); },
    onError,
  });
  const baixar = useMutation({
    mutationFn: ({ id, data }: { id: string; data: string }) => apiPost<Conta>(`/financeiro/contas/${id}/baixa`, { data }),
    onSuccess: () => { toast.success(pagar ? "Pagamento registrado" : "Recebimento registrado"); setBaixa(null); invalidate(); },
    onError,
  });
  const estornar = useMutation({
    mutationFn: (id: string) => apiPost<Conta>(`/financeiro/contas/${id}/estorno`),
    onSuccess: () => { toast.success("Baixa estornada"); invalidate(); },
    onError,
  });
  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/financeiro/contas/${id}`),
    onSuccess: () => { toast.success("Conta excluída"); setExcluirId(null); invalidate(); },
    onError,
  });

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          <Tabs value={filtro} onValueChange={(v) => setFiltro(v as Filtro)}>
            <TabsList>
              {(["abertas", "vencidas", "pagas", "todas"] as Filtro[]).map((f) => (
                <TabsTrigger key={f} value={f} data-testid={`contas-${p}-tab-${f}`}>
                  {f === "abertas" ? "Em aberto" : f === "vencidas" ? "Vencidas" : f === "pagas" ? (pagar ? "Pagas" : "Recebidas") : "Todas"} ({n(f)})
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-slate-500" />
            <Input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Buscar descrição, placa…" className="w-64 pl-8" data-testid={`contas-${p}-search`} />
          </div>
        </div>
        <div className="flex items-center gap-4">
          <p className="text-sm text-slate-400">Total no filtro: <span className={cn("font-semibold tabular-nums", pagar ? "text-red-300" : "text-emerald-300")} data-testid={`contas-${p}-total`}>{brl(total)}</span></p>
          <Button onClick={() => { setForm({ descricao: "", categoria: "", veiculo_id: SEM_VEICULO, valor: "", vencimento: hoje }); setOpen(true); }} data-testid={`contas-${p}-new-button`}>
            <Plus className="size-4" /> Conta a {p}
          </Button>
        </div>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid={`contas-${p}-table`}>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Vencimento", "Descrição", "Origem", "Caminhão", "Valor", "Situação", ""].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={7} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhuma conta neste filtro."}</TableCell></TableRow>
            )}
            {rows.slice(0, 300).map((c) => (
              <TableRow key={c.id} className="border-slate-800/70" data-testid={`conta-row-${c.id}`}>
                <TableCell className={cn("font-mono text-sm", c.vencida && "text-red-300")}>{dataBR(c.vencimento)}</TableCell>
                <TableCell className="max-w-[320px] truncate" title={c.descricao}>{c.descricao}</TableCell>
                <TableCell className="text-xs text-slate-400">{ORIGEM_LABEL[c.origem]}</TableCell>
                <TableCell className="font-mono text-sm">{c.veiculo_label?.split(" · ")[0] ?? "—"}</TableCell>
                <TableCell className="tabular-nums">{brl(c.valor)}</TableCell>
                <TableCell>
                  {c.status === "paga" ? (
                    <StatusBadge tone="ativo" testId={`conta-status-${c.id}`}>{pagar ? "Paga" : "Recebida"} {dataBR(c.pago_em)}</StatusBadge>
                  ) : c.vencida ? (
                    <StatusBadge tone="excluido" testId={`conta-status-${c.id}`}>Vencida</StatusBadge>
                  ) : (
                    <StatusBadge tone="info" testId={`conta-status-${c.id}`}>Em aberto</StatusBadge>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    {c.status === "aberta" ? (
                      <Button size="sm" variant="outline" onClick={() => setBaixa({ conta: c, data: hoje })} data-testid={`conta-baixa-${c.id}`}>
                        <CheckCircle2 className="size-3.5" /> {pagar ? "Pagar" : "Receber"}
                      </Button>
                    ) : (
                      <Button size="sm" variant="ghost" onClick={() => estornar.mutate(c.id)} disabled={estornar.isPending} data-testid={`conta-estorno-${c.id}`}>
                        <Undo2 className="size-3.5" /> Estornar
                      </Button>
                    )}
                    {me?.perfil === "admin" && c.origem === "manual" && (
                      <Button size="icon-sm" variant="ghost" className="text-red-300" aria-label="Excluir" onClick={() => setExcluirId(c.id)} data-testid={`conta-delete-${c.id}`}>
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
        <DialogContent className="sm:max-w-lg" data-testid={`conta-${p}-dialog`}>
          <DialogHeader><DialogTitle>Nova conta a {p}</DialogTitle></DialogHeader>
          <form
            className="grid grid-cols-2 gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              criar.mutate({
                tipo, descricao: form.descricao, categoria: form.categoria || "Outros",
                veiculo_id: form.veiculo_id === SEM_VEICULO ? null : form.veiculo_id,
                valor: Number(form.valor.replace(",", ".")), vencimento: form.vencimento,
              });
            }}
          >
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="ct-desc">Descrição *</Label>
              <Input id="ct-desc" required value={form.descricao} onChange={(e) => setForm((s) => ({ ...s, descricao: e.target.value }))} placeholder={pagar ? "Ex.: Pedágio, pneus, IPVA" : "Ex.: Reembolso, armazenagem"} data-testid="conta-form-descricao" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ct-cat">Categoria</Label>
              <Input id="ct-cat" value={form.categoria} onChange={(e) => setForm((s) => ({ ...s, categoria: e.target.value }))} placeholder="Outros" data-testid="conta-form-categoria" />
            </div>
            <div className="grid gap-1.5">
              <Label>Caminhão</Label>
              <FieldSelect value={form.veiculo_id} onChange={(v) => setForm((s) => ({ ...s, veiculo_id: v }))} options={[{ value: SEM_VEICULO, label: "— Despesa geral —" }, ...(veiculos.data ?? []).map((v) => ({ value: v.id, label: v.placa }))]} testId="conta-form-veiculo" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ct-valor">Valor (R$) *</Label>
              <Input id="ct-valor" required inputMode="decimal" value={form.valor} onChange={(e) => setForm((s) => ({ ...s, valor: e.target.value }))} data-testid="conta-form-valor" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ct-venc">Vencimento *</Label>
              <Input id="ct-venc" type="date" required value={form.vencimento} onChange={(e) => setForm((s) => ({ ...s, vencimento: e.target.value }))} data-testid="conta-form-vencimento" />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={criar.isPending} data-testid="conta-form-submit">Lançar</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={baixa !== null} onOpenChange={(o) => !o && setBaixa(null)}>
        <DialogContent className="sm:max-w-sm" data-testid="conta-baixa-dialog">
          <DialogHeader><DialogTitle>{pagar ? "Registrar pagamento" : "Registrar recebimento"}</DialogTitle></DialogHeader>
          {baixa && (
            <div className="grid gap-3">
              <p className="text-sm text-slate-300">{baixa.conta.descricao}</p>
              <p className="font-heading text-2xl font-semibold">{brl(baixa.conta.valor)}</p>
              <div className="grid gap-1.5">
                <Label htmlFor="bx-data">Data</Label>
                <Input id="bx-data" type="date" value={baixa.data} onChange={(e) => setBaixa({ ...baixa, data: e.target.value })} data-testid="conta-baixa-data" />
              </div>
              <DialogFooter>
                <Button disabled={baixar.isPending || !baixa.data} onClick={() => baixar.mutate({ id: baixa.conta.id, data: baixa.data })} data-testid="conta-baixa-confirm">Confirmar</Button>
              </DialogFooter>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir conta?"
        description="Só contas lançadas manualmente podem ser excluídas. A ação fica na auditoria."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="conta-excluir"
      />
    </div>
  );
}
