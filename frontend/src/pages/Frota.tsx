import { PageHeader } from "@/components/common/PageHeader";
import { Truck, Map, Activity } from "lucide-react";

export default function Frota() {
  return (
    <div>
      <PageHeader eyebrow="Operação" title="Frota" description="Visão consolidada de veículos e disponibilidade." />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center text-center border-t-4 border-t-sky-500">
          <Truck className="size-10 text-sky-400 mb-3" />
          <h3 className="text-lg font-bold text-slate-200">Disponibilidade da Frota</h3>
          <p className="text-sm text-slate-500 mt-2">Status em tempo real de cavalos e carretas (rodando, oficina, parado).</p>
        </div>
        
        <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center text-center border-t-4 border-t-amber-500">
          <Map className="size-10 text-amber-400 mb-3" />
          <h3 className="text-lg font-bold text-slate-200">Rastreamento e Rotas</h3>
          <p className="text-sm text-slate-500 mt-2">Integração com telemetria para monitorar posições em tempo real.</p>
        </div>

        <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center text-center border-t-4 border-t-indigo-500">
          <Activity className="size-10 text-indigo-400 mb-3" />
          <h3 className="text-lg font-bold text-slate-200">Indicadores de Uso</h3>
          <p className="text-sm text-slate-500 mt-2">KM rodados, horas de motor e taxa de ocupação dos veículos.</p>
        </div>
      </div>
    </div>
  );
}
