import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost } from "@/lib/api";
import { brl, dataBR, errMsg, num } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { useMotoristas, useVeiculos } from "@/hooks/useCadastros";
import { useHoje, useMe } from "@/hooks/useSession";
import type { Abastecimento } from "@/types/abastecimentos";

const TODOS = "__all__";
const NENHUM = "__none__";

const vazio = (hoje: string) => ({ data: hoje, veiculo_id: "", motorista_id: NENHUM, litros: "", preco_litro: "", posto: "", km: "", observacoes: "" });

export default function Abastecimentos() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const [filtroVeiculo, setFiltroVeiculo] = useState(TODOS);
  const [mes, setMes] = useState("");
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(() => vazio(""));
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const params = new URLSearchParams();
  if (filtroVeiculo !== TODOS) params.set("veiculo_id", filtroVeiculo);
  if (mes) params.set("mes", mes);
  const q = useQuery({
    queryKey: ["abastecimentos", filtroVeiculo, mes],
    queryFn: () => apiGet<Abastecimento[]>(`/abastecimentos?${params.toString()}`),
  });
  const rows = q.isError ? [] : (q.data ?? []);

  const resumo = useMemo(() => {
    const litros = rows.reduce((s, r) => s + r.litros, 0);
    const valor = rows.reduce((s, r) => s + r.valor_total, 0);
    const comKm = rows.filter((r) => r.km_rodados != null);
    const km = comKm.reduce((s, r) => s + (r.km_rodados ?? 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + r.litros, 0);
    
    // Novos cálculos
    const maior = rows.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rows.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rows.length ? valor / rows.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;

    return { 
      litros, valor, km, media: litrosKm ? km / litrosKm : 0, preco: litros ? valor / litros : 0,
      maior, menor, mediaValor, mediaKm
    };
  }, [rows]);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["abastecimentos"] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
    void qc.invalidateQueries({ queryKey: ["veiculos"] });
    void qc.invalidateQueries({ queryKey: ["financeiro"] });
    void qc.invalidateQueries({ queryKey: ["ranking"] });
  };

  const criar = useMutation({
    mutationFn: () =>
      apiPost<Abastecimento>("/abastecimentos", {
        data: form.data,
        veiculo_id: form.veiculo_id,
        motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id,
        litros: Number(form.litros.replace(",", ".")),
        preco_litro: Number(form.preco_litro.replace(",", ".")),
        posto: form.posto,
        km: Number(form.km),
        observacoes: form.observacoes,
      }),
    onSuccess: (a) => {
      toast.success(a.media_km_l ? `Abastecimento registrado · média ${num(a.media_km_l, 2)} km/L` : "Abastecimento registrado");
      setOpen(false);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/abastecimentos/${id}`),
    onSuccess: () => { toast.success("Abastecimento excluído"); setExcluirId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });

  const total = Number(form.litros.replace(",", ".")) * Number(form.preco_litro.replace(",", "."));
  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));
  const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));

  const cards = [
    { label: "Maior abastecimento", valor: resumo.maior ? brl(resumo.maior.valor_total) : "—", sub: resumo.maior?.veiculo_label.split(" · ")[0], testId: "resumo-maior" },
    { label: "Menor abastecimento", valor: resumo.menor ? brl(resumo.menor.valor_total) : "—", sub: resumo.menor?.motorista_label || resumo.menor?.veiculo_label.split(" · ")[0], testId: "resumo-menor" },
    { label: "Média por abastecimento", valor: brl(resumo.mediaValor), sub: "R$ por registro", testId: "resumo-media-valor" },
    { label: "Média de KM rodados", valor: `${num(resumo.mediaKm, 0)} km`, sub: "por abastecimento", testId: "resumo-media-km" },
  ];


  const handleVeiculoChange = async (veiculoId: string) => {
    set("veiculo_id")(veiculoId);
    if (!veiculoId) return;

    try {
      // Busca o último KM (do cadastro ou último abastecimento)
      const kmData = await apiGet<{ ultimo_km: number }>(`/abastecimentos/ultimo-km/${veiculoId}`);
      setForm(s => ({ ...s, km: String(kmData.ultimo_km) }));

      // Busca o acoplamento ativo para preencher o motorista
      const acoplamentos = await apiGet<any[]>("/acoplamentos");
      const acoplamentoAtivo = acoplamentos.find(a => a.veiculo_id === veiculoId);
      
      if (acoplamentoAtivo) {
        if (acoplamentoAtivo.motorista_id) {
          setForm(s => ({ ...s, motorista_id: acoplamentoAtivo.motorista_id }));
        }
      } else {
        setForm(s => ({ ...s, motorista_id: NENHUM }));
      }
    } catch (error) {
      console.error("Erro ao buscar dados do veículo:", error);
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Abastecimentos"
        description="Registro detalhado com cálculo automático de KM rodados e média KM/L a partir do hodômetro."
        actions={
          <Button onClick={() => { setForm(vazio(hoje)); setOpen(true); }} data-testid="abastecimento-new-button">
            <Plus className="size-4" /> Novo abastecimento
          </Button>
        }
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((c) => (
          <div key={c.label} className="glass rounded-xl" style={{ padding: '12px 16px', height: '90px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }} data-testid={c.testId}>
            <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            <div>
              <p style={{ fontSize: '20px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '10px', color: '#64748b', marginTop: '4px' }}>{c.sub}</p>}
            </div>
          </div>
        ))}
      </div>

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="grid w-64 gap-1.5">
          <Label>Veículo</Label>
          <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} testId="abastecimento-filtro-veiculo" />
        </div>
        <div className="grid gap-1.5">
          <Label htmlFor="filtro-mes">Mês</Label>
          <Input id="filtro-mes" type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="w-44" data-testid="abastecimento-filtro-mes" />
        </div>
        {(mes || filtroVeiculo !== TODOS) && (
          <Button variant="ghost" onClick={() => { setMes(""); setFiltroVeiculo(TODOS); }} data-testid="abastecimento-limpar-filtros">Limpar filtros</Button>
        )}
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="abastecimento-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Veículo", "Motorista", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", ""].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={11} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhum abastecimento encontrado."}</TableCell></TableRow>
            )}
            {rows.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70" data-testid={`abastecimento-row-${r.id}`}>
                <TableCell className="font-mono text-sm">{dataBR(r.data)}</TableCell>
                <TableCell className="font-mono">{r.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300">{r.motorista_label ?? "—"}</TableCell>
                <TableCell className="tabular-nums">{num(r.litros, 1)}</TableCell>
                <TableCell className="tabular-nums">{num(r.preco_litro, 2)}</TableCell>
                <TableCell className="tabular-nums font-medium">{brl(r.valor_total)}</TableCell>
                <TableCell className="max-w-[180px] truncate text-slate-400">{r.posto}</TableCell>
                <TableCell className="font-mono tabular-nums">{num(r.km)}</TableCell>
                <TableCell className="tabular-nums">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                <TableCell className="tabular-nums text-sky-300">{r.media_km_l != null ? `${num(r.media_km_l, 2)}` : "—"}</TableCell>
                <TableCell className="text-right">
                  {me?.perfil === "admin" && (
                    <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)} aria-label="Excluir" data-testid={`abastecimento-delete-${r.id}`}>
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
        <DialogContent className="sm:max-w-lg" data-testid="abastecimento-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><Fuel className="size-5 text-sky-400" /> Novo abastecimento</DialogTitle>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); criar.mutate(); }}>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-data">Data *</Label>
              <Input id="ab-data" type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required data-testid="abastecimento-form-data" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-km">Hodômetro (KM) *</Label>
              <Input id="ab-km" type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} required data-testid="abastecimento-form-km" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Veículo *</Label>
              <FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="abastecimento-form-veiculo" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Motorista</Label>
              <FieldSelect
                value={form.motorista_id}
                onChange={set("motorista_id")}
                options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter(m => m.ativo).map((m) => ({ value: m.id, label: m.nome }))]}
                testId="abastecimento-form-motorista"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-litros">Litros *</Label>
              <Input id="ab-litros" inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} required data-testid="abastecimento-form-litros" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-preco">Preço por litro (R$) *</Label>
              <Input id="ab-preco" inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} required data-testid="abastecimento-form-preco" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="ab-posto">Posto *</Label>
              <Input id="ab-posto" value={form.posto} onChange={(e) => set("posto")(e.target.value)} required data-testid="abastecimento-form-posto" />
            </div>
            <p className="col-span-2 rounded-lg bg-slate-950/60 px-3 py-2 text-sm text-slate-300" data-testid="abastecimento-form-total">
              Valor total: <span className="font-semibold text-slate-50">{Number.isFinite(total) ? brl(total) : "—"}</span>
            </p>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={criar.isPending || !form.veiculo_id} data-testid="abastecimento-form-submit">Registrar</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir abastecimento?"
        description="Esta ação é registrada na auditoria e não pode ser desfeita."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="abastecimento-excluir"
      />
    </div>
  );
}
