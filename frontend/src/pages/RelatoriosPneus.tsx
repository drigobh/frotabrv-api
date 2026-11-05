import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { BarChart3, AlertTriangle, TrendingUp, DollarSign, Disc, ArrowRightLeft } from "lucide-react";
import { brl } from "@/lib/format";

export default function RelatoriosPneus() {
  const { data: marcas = [] } = useQuery({ queryKey: ["relatorio-marcas"], queryFn: () => apiGet<any[]>("/pneus/relatorios/desempenho-marcas") });
  const { data: alertas = { sulco_critico: [], na_oficina: [] } } = useQuery({ queryKey: ["relatorio-alertas"], queryFn: () => apiGet<any>("/pneus/relatorios/alertas") });
  const { data: financeiro = [] } = useQuery({ queryKey: ["relatorio-financeiro"], queryFn: () => apiGet<any[]>("/pneus/relatorios/financeiro") });

  return (
    <div>
      <PageHeader
        eyebrow="Inteligência"
        title="Relatórios de Pneus"
        description="Análise de vida útil, custos e alertas da frota."
      />

      {/* Cards de Alerta Rápido */}
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 mb-6">
        <div className="glass p-4 rounded-xl border border-rose-500/30 flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-rose-500 font-bold">Sulco Crítico</p>
            <p className="text-2xl font-bold text-rose-400">{alertas.sulco_critico.length}</p>
          </div>
          <AlertTriangle className="size-8 text-rose-400 opacity-50" />
        </div>
        <div className="glass p-4 rounded-xl border border-amber-500/30 flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-amber-500 font-bold">Na Borracharia</p>
            <p className="text-2xl font-bold text-amber-400">{alertas.na_oficina.length}</p>
          </div>
          <ArrowRightLeft className="size-8 text-amber-400 opacity-50" />
        </div>
        <div className="glass p-4 rounded-xl border border-sky-500/30 flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-sky-500 font-bold">Pneus Sucateados</p>
            <p className="text-2xl font-bold text-sky-400">
              {financeiro.find((f: any) => f._id === "Sucateado")?.quantidade || 0}
            </p>
          </div>
          <Disc className="size-8 text-sky-400 opacity-50" />
        </div>
        <div className="glass p-4 rounded-xl border border-emerald-500/30 flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-emerald-500 font-bold">Investimento Total</p>
            <p className="text-xl font-bold text-emerald-400">
              {brl(financeiro.reduce((acc: number, f: any) => acc + (f.custo_total || 0), 0))}
            </p>
          </div>
          <DollarSign className="size-8 text-emerald-400 opacity-50" />
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Desempenho por Marca */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-6 flex items-center gap-2">
            <TrendingUp className="size-5 text-emerald-400" /> Vida Útil Média por Marca (KM)
          </h3>
          <div className="space-y-4">
            {marcas.length === 0 ? (
              <p className="text-sm text-slate-500">Sem dados suficientes de pneus sucateados.</p>
            ) : (
              marcas.map((m: any, i: number) => {
                const maxKm = marcas[0].km_medio;
                const pct = (m.km_medio / maxKm) * 100;
                return (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-300 font-medium">{m.marca} ({m.total_pneus} pneus)</span>
                      <span className="text-emerald-400 font-bold">{Math.round(m.km_medio).toLocaleString('pt-BR')} km</span>
                    </div>
                    <div className="h-2.5 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-emerald-500 to-emerald-300 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                    <p className="text-[10px] text-slate-500 mt-1 text-right">Custo Médio: {brl(m.custo_medio)}</p>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Pneus com Sulco Crítico */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
            <AlertTriangle className="size-5 text-rose-400" /> Urgente: Troca de Pneus (Sulco ≤ 3mm)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase text-slate-500 bg-slate-800/50">
                <tr>
                  <th className="px-3 py-2 rounded-tl-lg">Nº Fogo</th>
                  <th className="px-3 py-2">Marca</th>
                  <th className="px-3 py-2 rounded-tr-lg">Sulco</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {alertas.sulco_critico.length === 0 ? (
                  <tr><td colSpan={3} className="text-center py-4 text-slate-500">Nenhum pneu em estado crítico.</td></tr>
                ) : (
                  alertas.sulco_critico.map((p: any) => (
                    <tr key={p.id} className="hover:bg-slate-800/30">
                      <td className="px-3 py-2 font-bold text-slate-200">{p.numero_fogo}</td>
                      <td className="px-3 py-2 text-slate-400">{p.marca}</td>
                      <td className="px-3 py-2"><span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 font-bold">{p.profundidade_atual} mm</span></td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
