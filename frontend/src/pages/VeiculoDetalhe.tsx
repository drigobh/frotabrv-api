import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams, Link, useNavigate } from "react-router-dom";
import { 
  ArrowLeft, CalendarClock, FileText, Fuel, MapPin, Truck, Wrench, Disc, Activity, Filter
} from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { brl, num } from "@/lib/format";
import { cn } from "@/lib/utils";

const abas = ["Visão Geral", "Abastecimentos", "Manutenção", "Pneus", "Documentos"] as const;
type Aba = typeof abas[number];

export default function VeiculoDetalhe() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [abaAtiva, setAbaAtiva] = useState<Aba>("Visão Geral");
  
  // Filtro de Mês/Ano
  const [mesFiltro, setMesFiltro] = useState(0);
  const [anoFiltro, setAnoFiltro] = useState(new Date().getFullYear());

  const { data: detalhes, isLoading } = useQuery({ 
    queryKey: ["veiculo-detalhes", id, mesFiltro, anoFiltro], 
    queryFn: () => apiGet<any>(`/veiculos/detalhes/${id}?mes=${mesFiltro}&ano=${anoFiltro}`) 
  });

  const veiculo = detalhes?.veiculo;
  const abastecimentos = detalhes?.abastecimentos || [];
  const manutencoes = detalhes?.manutencoes || [];
  const pneus = detalhes?.pneus || [];
  const financeiro = detalhes?.financeiro || { custo_total: 0, consumo_medio: 0 };

  const meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];

  return (
    <div>
      <PageHeader
        eyebrow="Frota"
        title={veiculo ? `${veiculo.placa} · ${veiculo.modelo}` : "Visão 360º do Veículo"}
        description={veiculo ? `Placa: ${veiculo.placa} · Ano: ${veiculo.ano || "—"} · Chassi: ${veiculo.template_chassi_id || "—"}` : "Buscando histórico completo..."}
        actions={
          <div className="flex gap-2">
            <Link to="/gestao/veiculo-360">
              <Button variant="outline" className="h-9 border-slate-700 text-slate-300">
                <ArrowLeft className="size-4 mr-2" /> Voltar
              </Button>
            </Link>
            <Button onClick={() => navigate("/agendamento")} className="h-9 bg-sky-600 hover:bg-sky-500">
              <Wrench className="size-4 mr-2" /> Agendar Manutenção
            </Button>
          </div>
        }
      />

      {/* Filtro de Mês/Ano */}
      <div className="flex flex-wrap items-center gap-3 mb-6 bg-slate-900/50 border border-slate-800 p-3 rounded-xl">
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Filter className="size-4" /> Filtrar Período:
        </div>
        <select 
          value={mesFiltro} 
          onChange={(e) => setMesFiltro(Number(e.target.value))}
          className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3"
        >
          <option value={0}>Todos os Meses</option>
          {meses.map((m, i) => <option key={m} value={i+1}>{m}</option>)}
        </select>
        <select 
          value={anoFiltro} 
          onChange={(e) => setAnoFiltro(Number(e.target.value))}
          className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3"
        >
          {[2024, 2025, 2026, 2027].map(a => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      {/* KPIs do Veículo */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Custo Total</p>
          <p className="mt-2 font-mono text-xl font-bold text-slate-100">{brl(financeiro.custo_total)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Consumo Médio</p>
          <p className="mt-2 font-mono text-xl font-bold text-emerald-400">
            {financeiro.consumo_medio > 0 ? num(financeiro.consumo_medio, 2) : "0,00"} <span className="text-xs text-slate-500">km/l</span>
          </p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Pneus Instalados</p>
          <p className="mt-2 font-mono text-xl font-bold text-slate-100">{pneus.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">OS Realizadas</p>
          <p className="mt-2 font-mono text-xl font-bold text-slate-100">{manutencoes.length}</p>
        </div>
      </div>

      {/* Navegação por Abas */}
      <div className="flex gap-1 overflow-x-auto scroll-thin rounded-xl border border-slate-800 bg-slate-900/50 p-1 mb-4">
        {abas.map((a) => (
          <button
            key={a}
            onClick={() => setAbaAtiva(a)}
            className={cn(
              "shrink-0 rounded-lg px-4 py-2 text-sm font-medium transition-colors",
              abaAtiva === a ? "bg-sky-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            )}
          >
            {a}
          </button>
        ))}
      </div>

      {/* Conteúdo das Abas */}
      <div className="glass rounded-2xl border border-slate-800 overflow-hidden">
        
        {abaAtiva === "Visão Geral" && (
          <div className="p-6">
            <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
              <Activity className="size-4 text-sky-400" /> Linha do Tempo Recente
            </h3>
            <div className="space-y-4">
              {abastecimentos.length === 0 && manutencoes.length === 0 ? (
                <p className="text-sm text-slate-500">Nenhum evento registrado neste período.</p>
              ) : (
                <>
                  {abastecimentos.slice(0, 3).map((a: any, i: number) => (
                    <div key={`ab-${i}`} className="flex items-center gap-4 border-l-2 border-slate-700 pl-4 py-1">
                      <span className="font-mono text-xs text-slate-500 w-12">{a.data_abastecimento?.split("-").reverse().slice(0,2).join("/")}</span>
                      <div className="flex-1">
                        <p className="text-sm text-slate-200">Abastecimento · {num(a.litros, 1)} L</p>
                        <p className="text-[11px] font-bold uppercase text-sky-400">Combustível</p>
                      </div>
                      <span className="font-mono text-sm text-slate-300">{brl(a.valor_total)}</span>
                    </div>
                  ))}
                  {manutencoes.slice(0, 3).map((m: any, i: number) => (
                    <div key={`man-${i}`} className="flex items-center gap-4 border-l-2 border-slate-700 pl-4 py-1">
                      <span className="font-mono text-xs text-slate-500 w-12">OS</span>
                      <div className="flex-1">
                        <p className="text-sm text-slate-200">{m.descricao || "Manutenção"}</p>
                        <p className="text-[11px] font-bold uppercase text-amber-400">Manutenção</p>
                      </div>
                      <span className="font-mono text-sm text-slate-300">{brl(m.valor)}</span>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        )}

        {abaAtiva === "Abastecimentos" && (
          <div className="p-0">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50 text-[11px] uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Data</th>
                  <th className="px-3 py-3 font-medium">Litros</th>
                  <th className="px-3 py-3 font-medium">Valor</th>
                  <th className="px-3 py-3 text-right font-medium">Hodômetro</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {abastecimentos.length === 0 ? (
                  <tr><td colSpan={4} className="p-6 text-center text-slate-500">Nenhum abastecimento no período.</td></tr>
                ) : (
                  abastecimentos.map((a: any) => (
                    <tr key={a.id} className="hover:bg-slate-800/30">
                      <td className="px-5 py-3 font-mono">{a.data_abastecimento?.split("T")[0].split("-").reverse().join("/") || "—"}</td>
                      <td className="px-3 py-3">{num(a.litros, 1)} L</td>
                      <td className="px-3 py-3 font-mono">{brl(a.valor_total)}</td>
                      <td className="px-3 py-3 text-right font-mono">{num(a.hodometro_km)} km</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {abaAtiva === "Manutenção" && (
          <div className="p-0">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50 text-[11px] uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-medium">OS / Descrição</th>
                  <th className="px-3 py-3 font-medium">Status</th>
                  <th className="px-3 py-3 text-right font-medium">Valor</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {manutencoes.length === 0 ? (
                  <tr><td colSpan={3} className="p-6 text-center text-slate-500">Nenhuma manutenção registrada.</td></tr>
                ) : (
                  manutencoes.map((m: any) => (
                    <tr key={m.id} className="hover:bg-slate-800/30">
                      <td className="px-5 py-3">{m.descricao || "Manutenção"}</td>
                      <td className="px-3 py-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700 text-slate-300 uppercase">{m.status}</span>
                      </td>
                      <td className="px-3 py-3 text-right font-mono">{brl(m.valor)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}

        {abaAtiva === "Pneus" && (
          <div className="p-6">
            {pneus.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <Disc className="size-8 mx-auto mb-2 opacity-50" />
                <p>Nenhum pneu instalado neste veículo.</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {pneus.map((p: any) => (
                  <div key={p.id} className="glass p-3 rounded-lg border border-slate-700">
                    <p className="font-bold text-sky-400">{p.numero_fogo}</p>
                    <p className="text-xs text-slate-400">{p.marca} · {p.medida}</p>
                    <p className="text-[10px] text-slate-500 mt-1">Posição: {p.posicao || "—"}</p>
                    <p className="text-xs font-mono mt-1 text-slate-300">Sulco: {p.profundidade_atual || "—"} mm</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {abaAtiva === "Documentos" && (
          <div className="p-6 text-center text-slate-500">
            <FileText className="size-8 mx-auto mb-2 opacity-50" />
            <p>Documentos e vencimentos em breve.</p>
          </div>
        )}
      </div>
    </div>
  );
}
