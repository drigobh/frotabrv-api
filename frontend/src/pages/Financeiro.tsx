import { PageHeader } from "@/components/common/PageHeader";
import { DollarSign, TrendingUp, Wallet } from "lucide-react";

export default function Financeiro() {
  return (
    <div>
      <PageHeader eyebrow="Gestão" title="Financeiro" description="Gestão de contas, custos e faturamento da frota." />
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center text-center border-t-4 border-t-emerald-500">
          <Wallet className="size-10 text-emerald-400 mb-3" />
          <h3 className="text-lg font-bold text-slate-200">Contas a Pagar/Receber</h3>
          <p className="text-sm text-slate-500 mt-2">Gestão de despesas de manutenção, combustível e receitas de frete.</p>
        </div>
        
        <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center text-center border-t-4 border-t-sky-500">
          <TrendingUp className="size-10 text-sky-400 mb-3" />
          <h3 className="text-lg font-bold text-slate-200">DRE & Fluxo de Caixa</h3>
          <p className="text-sm text-slate-500 mt-2">Demonstrativo de resultados e balanço mensal da operação.</p>
        </div>

        <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center text-center border-t-4 border-t-amber-500">
          <DollarSign className="size-10 text-amber-400 mb-3" />
          <h3 className="text-lg font-bold text-slate-200">Conciliação Bancária</h3>
          <p className="text-sm text-slate-500 mt-2">Integração com extratos e boletos (Em breve).</p>
        </div>
      </div>
    </div>
  );
}
