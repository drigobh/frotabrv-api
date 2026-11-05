import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { Activity, Disc, 
  ArrowLeft, CalendarClock, DollarSign, FileText, Fuel, 
  MapPin, Truck, Wrench 
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
  const [abaAtiva, setAbaAtiva] = useState<Aba>("Visão Geral");

  // Buscando dados (num sistema real, seria uma rota /veiculos/{id} que traz tudo)
  const { data: detalhes, isLoading } = useQuery({ queryKey: ["veiculo-detalhes", id], queryFn: () => apiGet<any>(`/veiculos/detalhes/${id}`) });

  const veiculo = detalhes?.veiculo;
  const abastecimentos = detalhes?.abastecimentos || [];
  const manutencoes = detalhes?.manutencoes || [];
  const pneus = detalhes?.pneus || [];

  
  
  

  // Cálculos
  const custoTotal = abastecimentos.reduce((a: number, b: any) => a + (b.valor_total || 0), 0) + manutencoes.reduce((a: number, b: any) => a + (b.valor || 0), 0);
  const totalLitros = abastecimentos.reduce((a: number, b: any) => a + (b.litros || 0), 0);
  const consumoMedio = abastecimentos.length > 0 ? (abastecimentos[0].hodometro_km - abastecimentos[abastecimentos.length-1].hodometro_km) / totalLitros : 0;

  return (
    <div>
      <PageHeader
        eyebrow="Frota"
        title={veiculo ? `${veiculo.placa} · ${veiculo.modelo}` : "Visão 360º do Veículo"}
        description={veiculo ? `Placa: ${veiculo.placa} · Ano: ${veiculo.ano || "—"} · Chassi: ${veiculo.template_chassi_id || "—"}` : "Buscando histórico completo no banco de dados..."}
        actions={
          <div className="flex gap-2">
            <Link to="/cadastros/veiculos">
              <Button variant="outline" className="h-9 border-slate-700 text-slate-300">
                <ArrowLeft className="size-4 mr-2" /> Voltar
              </Button>
            </Link>
            <Button className="h-9 bg-sky-600 hover:bg-sky-500">
              <Wrench className="size-4 mr-2" /> Agendar Manutenção
            </Button>
          </div>
        }
      />

      {/* Cards de KPI do Veículo */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Custo Total</p>
          <p className="mt-2 font-mono text-xl font-bold text-slate-100">{brl(custoTotal)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Consumo Médio</p>
          <p className="mt-2 font-mono text-xl font-bold text-emerald-400">{num(consumoMedio, 2)} <span className="text-xs text-slate-500">km/l</span></p>
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
              {/* Mock da Timeline */}
              {[
                { data: "03/11", evento: "Abastecimento · 412,6 L", valor: "R$ 2.549,87", tipo: "Combustível", cor: "text-sky-400" },
                { data: "28/10", evento: "OS-1031 · troca de filtro separador", valor: "R$ 640,00", tipo: "Manutenção", cor: "text-amber-400" },
                { data: "21/10", evento: "Rodízio de pneus · eixos 2 e 3", valor: "R$ 320,00", tipo: "Pneu", cor: "text-purple-400" },
                { data: "14/10", evento: "Abastecimento · 398,2 L", valor: "R$ 2.468,84", tipo: "Combustível", cor: "text-sky-400" },
              ].map((h, i) => (
                <div key={i} className="flex items-center gap-4 border-l-2 border-slate-700 pl-4 py-1">
                  <span className="font-mono text-xs text-slate-500 w-12">{h.data}</span>
                  <div className="flex-1">
                    <p className="text-sm text-slate-200">{h.evento}</p>
                    <p className={cn("text-[11px] font-bold uppercase", h.cor)}>{h.tipo}</p>
                  </div>
                  <span className="font-mono text-sm text-slate-300">{h.valor}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {abaAtiva === "Abastecimentos" && (
          <div className="p-6 text-center text-slate-500">
            <Fuel className="size-8 mx-auto mb-2 opacity-50" />
            <p>Histórico de abastecimentos em breve.</p>
          </div>
        )}

        {abaAtiva === "Manutenção" && (
          <div className="p-6 text-center text-slate-500">
            <Wrench className="size-8 mx-auto mb-2 opacity-50" />
            <p>Histórico de manutenções em breve.</p>
          </div>
        )}

        {abaAtiva === "Pneus" && (
          <div className="p-6 text-center text-slate-500">
            <Disc className="size-8 mx-auto mb-2 opacity-50" />
            <p>Mapa de pneus em breve.</p>
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
