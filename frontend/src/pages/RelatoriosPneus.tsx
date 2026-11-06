import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { BarChart3, AlertTriangle, TrendingUp, DollarSign, Disc, ArrowRightLeft, PieChart } from "lucide-react";
import { brl } from "@/lib/format";

export default function RelatoriosPneus() {
  const { data: marcas = [] } = useQuery({ queryKey: ["relatorio-marcas"], queryFn: () => apiGet<any[]>("/pneus/relatorios/desempenho-marcas") });
  const { data: pareto = [] } = useQuery({ queryKey: ["relatorio-pareto"], queryFn: () => apiGet<any[]>("/pneus/relatorios/pareto") });
  const { data: alertas = { sulco_critico: [], na_oficina: [] } } = useQuery({ queryKey: ["relatorio-alertas"], queryFn: () => apiGet<any>("/pneus/relatorios/alertas") });
  const { data: financeiro = [] } = useQuery({ queryKey: ["relatorio-financeiro"], queryFn: () => apiGet<any[]>("/pneus/relatorios/financeiro") });

  const totalSucateados = pareto.reduce((acc: number, p: any) => acc + p.quantidade, 0);

  return (
    <div>
      <PageHeader
        eyebrow="Inteligência"
        title="Relatórios de Pneus"
        description="Análise de vida útil, custos e motivos de descarte."
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Sulco Crítico</p>
          <p className="text-2xl font-bold text-rose-400 mt-1">{alertas.sulco_critico.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Na Borracharia</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">{alertas.na_oficina.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Total Sucateados</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">{totalSucateados}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-xs uppercase text-slate-400">Investimento Total</p>
          <p className="text-xl font-bold text-emerald-400 mt-1">
            {brl(financeiro.reduce((acc: number, f: any) => acc + (f.custo_total || 0), 0))}
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Desempenho por Marca */}
        <div className="glass p-6 rounded-2xl border border-slate-800">
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
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Pareto de Descarte */}
        <div className="glass p-6 rounded-2xl border border-slate-800">
          <h3 className="text-lg font-bold text-slate-100 mb-6 flex items-center gap-2">
            <PieChart className="size-5 text-amber-400" /> Motivos de Sucateamento (Pareto)
          </h3>
          <div className="space-y-3">
            {pareto.length === 0 ? (
              <p className="text-sm text-slate-500">Nenhum pneu sucateado ainda.</p>
            ) : (
              pareto.map((p: any, i: number) => {
                const pct = (p.quantidade / totalSucateados) * 100;
                return (
                  <div key={i}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-300">{p.motivo}</span>
                      <span className="text-amber-400 font-bold">{p.quantidade} un ({Math.round(pct)}%)</span>
                    </div>
                    <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-amber-500 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
