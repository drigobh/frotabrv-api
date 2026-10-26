import { useQuery } from "@tanstack/react-query";
import { Truck, Fuel, Wrench, TrendingUp } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, num } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useMe } from "@/hooks/useSession";

export default function Dashboard() {
  const { data: me } = useMe();
  // Busca as duas listas que já sabemos que funcionam
  const { data: abastecimentos = [], isLoading: loadAb } = useQuery({ queryKey: ["abastecimentos"], queryFn: () => apiGet<any[]>("/abastecimentos") });
  const { data: manutencoes = [], isLoading: loadMan } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });

  if (loadAb || loadMan) return <div className="p-10 text-center text-slate-500">Carregando indicadores...</div>;

  // Cálculos
  const totalAbast = abastecimentos.reduce((s, a) => s + (Number(a.valor_total) || 0), 0);
  const totalManut = manutencoes.reduce((s, m) => s + (Number(m.custo) || 0), 0);
  const totalGeral = totalAbast + totalManut;

  // Agrupamento Mensal
  const meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
  const hoje = new Date();
  const dadosGrafico = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date(hoje.getFullYear(), hoje.getMonth() - i, 1);
    const mesAnoStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    const label = `${meses[d.getMonth()]}/${d.getFullYear().toString().slice(2)}`;
    
    const vAbast = abastecimentos.filter(a => a.data && a.data.startsWith(mesAnoStr)).reduce((s, a) => s + (Number(a.valor_total) || 0), 0);
    const vManut = manutencoes.filter(m => m.data && m.data.startsWith(mesAnoStr)).reduce((s, m) => s + (Number(m.custo) || 0), 0);
    
    dadosGrafico.push({ mes: label, abastecimento: vAbast, manutencao: vManut });
  }

  // Ranking Top 5
  const rankingMap: Record<string, { label: string, litros: number, km: number }> = {};
  abastecimentos.forEach(a => {
    const vId = a.veiculo_id;
    if (!vId) return;
    if (!rankingMap[vId]) rankingMap[vId] = { label: (a.veiculo_label || "").split(" · ")[0], litros: 0, km: 0 };
    rankingMap[vId].litros += (Number(a.litros) || 0);
    rankingMap[vId].km += (Number(a.km_rodados) || 0);
  });
  const topVeiculos = Object.values(rankingMap)
    .map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 }))
    .sort((a, b) => b.media - a.media)
    .slice(0, 5);

  const kpis = [
    { label: "Custo Combustível", valor: brl(totalAbast), icon: Fuel, color: "#0ea5e9" },
    { label: "Custo Manutenção", valor: brl(totalManut), icon: Wrench, color: "#f59e0b" },
    { label: "Custo Total", valor: brl(totalGeral), icon: TrendingUp, color: "#10b981" },
    { label: "Abastecimentos", valor: num(abastecimentos.length), icon: Truck, color: "#8b5cf6" },
  ];

  return (
    <div>
      <PageHeader eyebrow="Dashboard" title={`Olá, ${me?.nome?.split(" ")[0] || "Usuário"}`} description="Indicadores da frota em tempo real e custos dos últimos 6 meses." />

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

      <div className="grid md:grid-cols-2 gap-6">
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 mb-6">Custos Operacionais (Combustível x Manutenção)</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={dadosGrafico}>
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
            {topVeiculos.length === 0 && <p className="text-sm text-slate-500">Sem dados suficientes.</p>}
            {topVeiculos.map((v: any, i: number) => (
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
