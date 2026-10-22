import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Route, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost } from "@/lib/api";
import { brl, dataBR, errMsg } from "@/lib/format";
import { addDias } from "@/lib/periodo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { useMotoristas, useVeiculos } from "@/hooks/useCadastros";
import { useHoje, useMe } from "@/hooks/useSession";
import type { Frete, FreteCreate } from "@/types/financeiro";

const SEM = "__none__";
const vazio = (hoje: string) => ({ data: hoje, veiculo_id: "", motorista_id: SEM, cliente: "", origem: "", destino: "", valor: "", vencimento: hoje ? addDias(hoje, 30) : "", observacoes: "" });

export function FretesTab({ inicio, fim }: { inicio: string; fim: string }) {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(() => vazio(""));
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const q = useQuery({
    queryKey: ["financeiro", "fretes", inicio, fim],
    queryFn: () => apiGet<Frete[]>(`/financeiro/fretes?inicio=${inicio}&fim=${fim}`),
    enabled: Boolean(inicio && fim),
  });
  const rows = q.isError ? [] : (q.data ?? []);
  const total = rows.reduce((s, f) => s + f.valor, 0);
  const invalidate = () => void qc.invalidateQueries({ queryKey: ["financeiro"] });

  const criar = useMutation({
    mutationFn: (body: FreteCreate) => apiPost<Frete>("/financeiro/fretes", body),
    onSuccess: () => { toast.success("Frete lançado — conta a receber criada"); setOpen(false); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/financeiro/fretes/${id}`),
    onSuccess: () => { toast.success("Frete excluído"); setExcluirId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-slate-400">
          <span className="tabular-nums text-slate-100" data-testid="fretes-count">{rows.length}</span> viagem(ns) no período · receita{" "}
          <span className="font-semibold tabular-nums text-emerald-300" data-testid="fretes-total">{brl(total)}</span>
        </p>
        <Button onClick={() => { setForm(vazio(hoje)); setOpen(true); }} data-testid="frete-new-button"><Plus className="size-4" /> Lançar frete</Button>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="fretes-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Caminhão", "Motorista", "Cliente", "Rota", "Valor", "Vencimento", ""].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={8} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhum frete no período."}</TableCell></TableRow>
            )}
            {rows.map((f) => (
              <TableRow key={f.id} className="border-slate-800/70" data-testid={`frete-row-${f.id}`}>
                <TableCell className="font-mono text-sm">{dataBR(f.data)}</TableCell>
                <TableCell className="font-mono">{f.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300">{f.motorista_label ?? "—"}</TableCell>
                <TableCell>{f.cliente}</TableCell>
                <TableCell className="text-sm text-slate-400">{f.origem} <span className="text-sky-400">→</span> {f.destino}</TableCell>
                <TableCell className="tabular-nums text-emerald-300">{brl(f.valor)}</TableCell>
                <TableCell className="font-mono text-sm text-slate-400">{dataBR(f.vencimento)}</TableCell>
                <TableCell className="text-right">
                  {me?.perfil === "admin" && (
                    <Button size="icon-sm" variant="ghost" className="text-red-300" aria-label="Excluir" onClick={() => setExcluirId(f.id)} data-testid={`frete-delete-${f.id}`}>
                      <Trash2 className="size-4" />
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-xl" data-testid="frete-dialog">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Route className="size-5 text-emerald-400" /> Lançar frete</DialogTitle></DialogHeader>
          <form
            className="grid grid-cols-2 gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              criar.mutate({
                ...form, motorista_id: form.motorista_id === SEM ? null : form.motorista_id,
                valor: Number(form.valor.replace(",", ".")),
              });
            }}
          >
            <div className="grid gap-1.5">
              <Label>Caminhão *</Label>
              <FieldSelect value={form.veiculo_id} onChange={set("veiculo_id")} options={(veiculos.data ?? []).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }))} placeholder="Selecione" testId="frete-form-veiculo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Motorista</Label>
              <FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: SEM, label: "— Não informado —" }, ...(motoristas.data ?? []).map((m) => ({ value: m.id, label: m.nome }))]} testId="frete-form-motorista" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="fr-cli">Cliente *</Label>
              <Input id="fr-cli" required value={form.cliente} onChange={(e) => set("cliente")(e.target.value)} data-testid="frete-form-cliente" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="fr-or">Origem *</Label>
              <Input id="fr-or" required value={form.origem} onChange={(e) => set("origem")(e.target.value)} placeholder="Cidade/UF" data-testid="frete-form-origem" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="fr-de">Destino *</Label>
              <Input id="fr-de" required value={form.destino} onChange={(e) => set("destino")(e.target.value)} placeholder="Cidade/UF" data-testid="frete-form-destino" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="fr-data">Data da viagem *</Label>
              <Input id="fr-data" type="date" required value={form.data} onChange={(e) => set("data")(e.target.value)} data-testid="frete-form-data" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="fr-valor">Valor do frete (R$) *</Label>
              <Input id="fr-valor" required inputMode="decimal" value={form.valor} onChange={(e) => set("valor")(e.target.value)} data-testid="frete-form-valor" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="fr-venc">Vencimento do recebimento *</Label>
              <Input id="fr-venc" type="date" required value={form.vencimento} onChange={(e) => set("vencimento")(e.target.value)} data-testid="frete-form-vencimento" />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={criar.isPending || !form.veiculo_id} data-testid="frete-form-submit">Lançar frete</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir frete?"
        description="A conta a receber vinculada também será removida. A ação fica na auditoria."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="frete-excluir"
      />
    </div>
  );
}
