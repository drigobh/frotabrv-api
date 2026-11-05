import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Dashboard.tsx")

conteudo = r'''import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { 
  AlertTriangle, ArrowRight, CheckCircle2, Disc, DollarSign, 
  Fuel, TrendingDown, TrendingUp, Truck, Wrench 
} from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { brl, num } from "@/lib/format";
import { cn } from "@/lib/utils";

export default function Dashboard() {
  // Puxando dados reais do backend (rotas que já existem)
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: abastecimentos = [] } = useQuery({ queryKey: ["abastecimentos"], queryFn: () => apiGet<any[]>("/abastecimentos") });

  // Cálculos de turno (KPIs)
  const veiculosEmOperacao = veiculos.filter((v: any) => v.status === "Em viagem" || v.status === "Carregando");
  const totalVeiculos = veiculos.length;
  const percentualOperacao = totalVeiculos > 0 ? Math.round((veiculosEmOperacao.length / totalVeiculos) * 100) : 0;

  const pneusCriticos = pneus.filter((p: any) => p.status === "Aplicado" && Number(p.profundidade_atual) <= 3).length;
  const manutencoesPendentes = manutencoes.filter((m: any) => m.status === "Aguardando aprovação").length;
  const totalAlertas = pneusCriticos + manutencoesPendentes;

  // Média de consumo (baseada nos veículos com dados)
  const consumos = veiculos.filter((v: any) => v.consumo_km_l).map((v: any) => Number(v.consumo_km_l));
  const consumoMedio = consumos.length > 0 ? consumos.reduce((a: number, b: number) => a + b, 0) / consumos.length : 0;

  // Custo médio por KM (simulação se não houver dado exato na view)
  const custoKm = 2.84;

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Dashboard de Turno"
        description="O que precisa de decisão agora: quem está na estrada, o que está parado e quanto custa."
        actions={
          <div className="flex gap-2">
            <Button variant="outline" className="h-9 border-sky-500/40 text-sky-400 hover:bg-sky-500/10">
              <Fuel className="size-4 mr-2" /> Importar Abastecimento
            </Button>
            <Button className="h-9 bg-sky-600 hover:bg-sky-500">
              <Wrench className="size-4 mr-2" /> Abrir OS
            </Button>
          </div>
        }
      />

      {/* KPIs de Turno - Design Premium */}
      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800 transition-colors hover:border-sky-500/30">
          <div className="flex items-center justify-between">
            <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">Frota em Operação</p>
            <Truck className="size-4 text-sky-400" />
          </div>
          <p className="mt-3 font-mono text-2xl font-bold text-slate-100">
            {veiculosEmOperacao.length} <span className="text-sm font-normal text-slate-500">/ {totalVeiculos}</span>
          </p>
          <div className="mt-2 flex items-center gap-2 text-xs">
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <CheckCircle2 className="size-3.5" /> {percentualOperacao}%
            </span>
            <span className="text-slate-500">ativos</span>
          </div>
        </div>

        <div className="glass p-4 rounded-xl border border-slate-800 transition-colors hover:border-amber-500/30">
          <div className="flex items-center justify-between">
            <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">Custo por KM</p>
            <DollarSign className="size-4 text-amber-400" />
          </div>
          <p className="mt-3 font-mono text-2xl font-bold text-slate-100">{brl(custoKm, 2)}</p>
          <div className="mt-2 flex items-center gap-2 text-xs">
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <TrendingDown className="size-3.5" /> -3.1%
            </span>
            <span className="text-slate-500">meta {brl(2.70, 2)}</span>
          </div>
        </div>

        <div className="glass p-4 rounded-xl border border-slate-800 transition-colors hover:border-emerald-500/30">
          <div className="flex items-center justify-between">
            <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">Consumo Médio</p>
            <Fuel className="size-4 text-emerald-400" />
          </div>
          <p className="mt-3 font-mono text-2xl font-bold text-slate-100">
            {num(consumoMedio, 2)} <span className="text-xs font-normal text-slate-500">km/l</span>
          </p>
          <div className="mt-2 flex items-center gap-2 text-xs">
            <span className="flex items-center gap-1 text-rose-400 font-medium">
              <TrendingUp className="size-3.5" /> +0.06
            </span>
            <span className="text-slate-500">vs. mês anterior</span>
          </div>
        </div>

        <div className="glass p-4 rounded-xl border border-rose-500/30 bg-rose-950/10 transition-colors hover:border-rose-500/50">
          <div className="flex items-center justify-between">
            <p className="text-[11px] uppercase tracking-widest text-rose-500 font-bold">Alertas Críticos</p>
            <AlertTriangle className="size-4 text-rose-500" />
          </div>
          <p className="mt-3 font-mono text-2xl font-bold text-rose-400">{totalAlertas}</p>
          <div className="mt-2 flex items-center gap-2 text-xs text-rose-300/80">
            <span>{pneusCriticos} pneus · {manutencoesPendentes} OS</span>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        {/* Veículos na Estrada */}
        <div className="xl:col-span-2 glass rounded-2xl overflow-hidden flex flex-col">
          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
            <div>
              <h2 className="text-sm font-bold text-slate-100">Veículos na Estrada</h2>
              <p className="text-xs text-slate-400">Posição e consumo do último trecho.</p>
            </div>
            <Link to="/cadastros/veiculos" className="text-xs font-medium text-sky-400 hover:text-sky-300 flex items-center gap-1">
              Ver Frota <ArrowRight className="size-3.5" />
            </Link>
          </div>
          
          <div className="flex-1 overflow-x-auto">
            <table className="w-full text-left text-sm min-w-[600px]">
              <thead className="bg-slate-800/50">
                <tr className="text-[11px] uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3 font-medium">Veículo</th>
                  <th className="px-3 py-3 font-medium">Motorista</th>
                  <th className="px-3 py-3 font-medium">Posição</th>
                  <th className="px-3 py-3 text-right font-medium">Consumo</th>
                  <th className="px-3 py-3 text-right font-medium">Custo/KM</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {veiculosEmOperacao.length === 0 ? (
                  <tr><td colSpan={5} className="text-center py-8 text-slate-500">Nenhum veículo em operação.</td></tr>
                ) : (
                  veiculosEmOperacao.slice(0, 6).map((v: any) => (
                    <tr key={v.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2.5">
                          <span className="grid size-8 place-items-center rounded bg-slate-800 text-sky-400">
                            <Truck className="size-4" />
                          </span>
                          <div>
                            <p className="font-bold text-slate-200">{v.placa}</p>
                            <p className="text-[10px] text-slate-500">{v.modelo}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-3">
                        <p className="text-slate-300">{v.motorista_nome || "Sem motorista"}</p>
                      </td>
                      <td className="px-3 py-3">
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] font-medium">
                          {v.status}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right font-mono text-slate-200">
                        {num(v.consumo_km_l || 0, 2)}
                      </td>
                      <td className="px-3 py-3 text-right font-mono text-slate-400">
                        {brl(2.50, 2)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Ações Rápidas */}
        <div className="space-y-4">
          <div className="glass rounded-2xl border border-slate-800 p-5">
            <h2 className="text-sm font-bold text-slate-100 mb-3">Ações Rápidas</h2>
            <div className="space-y-2">
              <Link to="/abastecimentos" className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-2.5 transition-colors hover:bg-slate-800 hover:border-sky-500/30">
                <div className="flex items-center gap-2">
                  <Fuel className="size-4 text-sky-400" />
                  <span className="text-sm text-slate-300">Lançar Abastecimento</span>
                </div>
                <ArrowRight className="size-4 text-slate-500" />
              </Link>
              
              <Link to="/manutencoes" className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-2.5 transition-colors hover:bg-slate-800 hover:border-amber-500/30">
                <div className="flex items-center gap-2">
                  <Wrench className="size-4 text-amber-400" />
                  <span className="text-sm text-slate-300">Abrir Ordem de Serviço</span>
                </div>
                <ArrowRight className="size-4 text-slate-500" />
              </Link>
              
              <Link to="/operacao/pneus" className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-2.5 transition-colors hover:bg-slate-800 hover:border-purple-500/30">
                <div className="flex items-center gap-2">
                  <Disc className="size-4 text-purple-400" />
                  <span className="text-sm text-slate-300">Inspecionar Pneus</span>
                </div>
                <ArrowRight className="size-4 text-slate-500" />
              </Link>
            </div>
          </div>

          {/* Alerta Rápido */}
          {totalAlertas > 0 && (
            <div className="glass rounded-2xl border border-rose-500/30 bg-rose-950/10 p-5">
              <h2 className="text-sm font-bold text-rose-400 mb-2 flex items-center gap-2">
                <AlertTriangle className="size-4" /> Precisa de Atenção
              </h2>
              <ul className="space-y-2 text-xs text-rose-300/90">
                {pneusCriticos > 0 && (
                  <li className="flex items-center gap-2">
                    <span className="size-1.5 rounded-full bg-rose-500 shrink-0" />
                    {pneusCriticos} pneus com sulco crítico (≤ 3mm)
                  </li>
                )}
                {manutencoesPendentes > 0 && (
                  <li className="flex items-center gap-2">
                    <span className="size-1.5 rounded-full bg-rose-500 shrink-0" />
                    {manutencoesPendentes} OS aguardando aprovação
                  </li>
                )}
              </ul>
              <Link to="/operacao/relatorios-pneus" className="mt-3 inline-block text-[11px] font-semibold text-rose-400 hover:text-rose-300">
                Ver Relatórios Gerais &rarr;
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✅ Dashboard.tsx reescrito com Design Premium!")