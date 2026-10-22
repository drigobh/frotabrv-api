import { useQuery } from "@tanstack/react-query";
import { ArrowDownCircle, ArrowUpCircle, TrendingUp, Wallet } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, num } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { ResumoFinanceiro } from "@/types/financeiro";

function Resumo({ label, valor, detalhe, icon: Icon, cor, testId }: { label: string; valor: string; detalhe?: string; icon: typeof Wallet; cor: string; testId: string }) {
  return (
    <div className="glass rounded-2xl p-4">
      <div className="flex items-center justify-between text-sm text-slate-400">{label}<Icon className={cn("size-4", cor)} /></div>
      <p className="mt-2 font-heading text-2xl font-semibold tabular-nums text-slate-50" data-testid={testId}>{valor}</p>
      {detalhe && <p className="mt-1 text-xs text-slate-500">{detalhe}</p>}
    </div>
  );
}

export function RentabilidadeTab({ inicio, fim }: { inicio: string; fim: string }) {
  const q = useQuery({
    queryKey: ["financeiro", "rentabilidade", inicio, fim],
    queryFn: () => apiGet<ResumoFinanceiro>(`/financeiro/rentabilidade?inicio=${inicio}&fim=${fim}`),
    enabled: Boolean(inicio && fim),
  });
  const d = q.isError ? undefined : q.data;
  const maxReceita = Math.max(1, ...(d?.veiculos.map((v) => v.receita) ?? [1]));

  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Resumo label="Receita (fretes)" valor={d ? brl(d.receita_total) : "…"} icon={ArrowUpCircle} cor="text-emerald-400" testId="fin-receita-total" />
        <Resumo label="Despesas" valor={d ? brl(d.despesa_total) : "…"} detalhe="combustível + manutenção + outras" icon={ArrowDownCircle} cor="text-red-400" testId="fin-despesa-total" />
        <Resumo
          label="Lucro operacional"
          valor={d ? brl(d.lucro_total) : "…"}
          detalhe={d && d.receita_total ? `margem ${num((d.lucro_total / d.receita_total) * 100, 1)}%` : undefined}
          icon={TrendingUp}
          cor="text-sky-400"
          testId="fin-lucro-total"
        />
        <Resumo
          label="Em aberto (geral)"
          valor={d ? `${brl(d.a_receber_aberto - d.a_pagar_aberto)}` : "…"}
          detalhe={d ? `a receber ${brl(d.a_receber_aberto)} · a pagar ${brl(d.a_pagar_aberto)}` : undefined}
          icon={Wallet}
          cor="text-amber-400"
          testId="fin-saldo-aberto"
        />
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <div className="flex items-baseline justify-between px-5 pt-4">
          <h2 className="text-lg font-semibold">Rentabilidade por caminhão</h2>
          <p className="text-xs text-slate-500">ordenado pelo lucro</p>
        </div>
        <Table data-testid="rentabilidade-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Caminhão", "Viagens", "Receita", "Combustível", "Manutenção", "Outras", "Lucro", "Margem", "Custo/KM"].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {d && d.veiculos.length === 0 && (
              <TableRow><TableCell colSpan={9} className="py-10 text-center text-slate-500">Sem movimentação no período.</TableCell></TableRow>
            )}
            {d?.veiculos.map((v) => (
              <TableRow key={v.veiculo_id} className="border-slate-800/70" data-testid={`rentabilidade-row-${v.veiculo_id}`}>
                <TableCell>
                  <p className="font-mono text-slate-100">{v.veiculo_label.split(" · ")[0]}</p>
                  <div className="mt-1 h-1 w-28 overflow-hidden rounded-full bg-slate-800">
                    <div className="h-full rounded-full bg-emerald-500/80 transition-[width] duration-700" style={{ width: `${(v.receita / maxReceita) * 100}%` }} />
                  </div>
                </TableCell>
                <TableCell className="tabular-nums">{v.viagens}</TableCell>
                <TableCell className="tabular-nums text-emerald-300">{brl(v.receita)}</TableCell>
                <TableCell className="tabular-nums text-slate-300">{brl(v.combustivel)}</TableCell>
                <TableCell className="tabular-nums text-slate-300">{brl(v.manutencao)}</TableCell>
                <TableCell className="tabular-nums text-slate-400">{brl(v.outras_despesas)}</TableCell>
                <TableCell className={cn("font-semibold tabular-nums", v.lucro >= 0 ? "text-sky-300" : "text-red-300")} data-testid={`rentabilidade-lucro-${v.veiculo_id}`}>{brl(v.lucro)}</TableCell>
                <TableCell className="tabular-nums">{v.margem != null ? `${num(v.margem, 1)}%` : "—"}</TableCell>
                <TableCell className="tabular-nums text-slate-400">{v.custo_km != null ? brl(v.custo_km) : "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
