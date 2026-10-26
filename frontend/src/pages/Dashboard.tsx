import { useQuery } from "@tanstack/react-query";
import { Truck, Fuel, Wrench, TrendingUp, AlertTriangle } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, num } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useMe } from "@/hooks/useSession";

export default function Dashboard() {
  const { data: me } = useMe();
  const { data, isLoading } = useQuery({ queryKey: ["dashboard"], queryFn: () => apiGet<any>("/dashboard"), staleTime: 0, refetchOnMount: true });

  if (isLoading) return <div className="p-10 text-center text-slate-500">Carregando indicadores...</div>;

  const kpis = [
    { label: "Custo Combustível", valor: brl(data?.total_abastecimento || 0), icon: Fuel, color: "#0ea5e9" },
    { label: "Custo Manutenção", valor: brl(data?.total_manutencao || 0), icon: Wrench, color: "#f59e0b" },
    { label: "Custo Total", valor: brl(data?.total_geral || 0), icon: TrendingUp, color: "#10b981" },
    { label: "Abastecimentos", valor: num(data?.abastecimentos?.length || 0), icon: Truck, color: "#8b5cf6" },
  ];

  return (
    <div>
      <PageHeader 
        eyebrow="Dashboard" 
        title={`Olá, ${me?.nome?.split(" ")[0] || "Usuário"}`} 
        description="Indicadores da frota em tempo real e custos dos últimos 6 meses." 
      />

      {/* Cards de KPI */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 md:grid-cols-4">
        {kpis.map((kpi, i) => (
          <div key={i} className="glass rounded-xl p-4 flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-500 font-medium">{kpi.label}</p>
              <p className="text-2xl font-bold text-slate-100 mt-1">{kpi.valor}</p>
            </div>
            <div className="size-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${kpi.color}20`, color: kpi.color }}>
              <kpi.icon className="size-5" />
            </div>
          </div>
        ))}
      </div>

      {/* Gráficos */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 mb-6">Custos Operacionais (Combustível x Manutenção)</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.meses_grafico || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="mes" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `R$${v/1000}k`} />
                <Tooltip 
                  cursor={{ fill: '#1e293b' }}
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                  formatter={(value: any) => brl(value)}
                />
                <Bar dataKey="abastecimento" name="Combustível" stackId="a" fill="#0ea5e9" radius={[0, 0, 4, 4]} />
                <Bar dataKey="manutencao" name="Manutenção" stackId="a" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 mb-6">Top 5 Veículos (KM/L)</h3>
          <div className="space-y-4">
            {(data?.top_veiculos || []).length === 0 && <p className="text-sm text-slate-500">Sem dados suficientes.</p>}
            {(data?.top_veiculos || []).map((v: any, i: number) => (
              <div key={i}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-300">{i + 1}º {v.label}</span>
                  <span className="font-bold text-emerald-400">{num(v.media, 2)}</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full" style={{ width: `${Math.min((v.media / 5) * 100, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
