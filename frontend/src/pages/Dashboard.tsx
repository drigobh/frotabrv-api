import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";
import { Truck, Wrench, Fuel, MapPin, DollarSign, Users } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { brl } from "@/lib/format";

const COLORS = ['#0284c7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Dashboard() {
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: abastecimentos = [] } = useQuery({ queryKey: ["abastecimentos"], queryFn: () => apiGet<any[]>("/abastecimentos") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });

  // 1. Dados para os Cards de KPI
  const kpis = useMemo(() => {
    const totalFornecedores = fornecedores.length;
    const custoManutencoes = manutencoes.reduce((acc: number, m: any) => acc + (m.custo || 0), 0);
    const volumeAbastecido = abastecimentos.reduce((acc: number, a: any) => acc + (a.litros || 0), 0);
    const estados = [...new Set(fornecedores.map((f: any) => f.estado))].filter(Boolean).length;
    
    return { totalFornecedores, custoManutencoes, volumeAbastecido, estados };
  }, [fornecedores, manutencoes, abastecimentos]);

  // 2. Dados para o Gráfico de Fornecedores por Estado
  const fornecedoresPorEstado = useMemo(() => {
    const counts: Record<string, number> = {};
    fornecedores.forEach((f: any) => {
      if (f.estado) counts[f.estado] = (counts[f.estado] || 0) + 1;
    });
    return Object.entries(counts).map(([estado, quantidade]) => ({ estado, quantidade })).sort((a, b) => b.quantidade - a.quantidade).slice(0, 8);
  }, [fornecedores]);

  // 3. Dados para o Gráfico de Custos de Manutenção (Mensal)
  const custosManutencao = useMemo(() => {
    const custos: Record<string, number> = {};
    manutencoes.forEach((m: any) => {
      if (m.data && m.custo) {
        const mes = m.data.slice(0, 7); // YYYY-MM
        custos[mes] = (custos[mes] || 0) + m.custo;
      }
    });
    return Object.entries(custos).sort().map(([mes, custo]) => ({ mes, custo }));
  }, [manutencoes]);

  // 4. Dados para o Gráfico de Volume Abastecido (Mensal)
  const volumeAbastecimento = useMemo(() => {
    const volumes: Record<string, number> = {};
    abastecimentos.forEach((a: any) => {
      if (a.data && a.litros) {
        const mes = a.data.slice(0, 7);
        volumes[mes] = (volumes[mes] || 0) + a.litros;
      }
    });
    return Object.entries(volumes).sort().map(([mes, litros]) => ({ mes, litros }));
  }, [abastecimentos]);

  // 5. Dados para o Gráfico de Top 5 Veículos (por Custo de Manutenção)
  const topVeiculos = useMemo(() => {
    const custos: Record<string, number> = {};
    manutencoes.forEach((m: any) => {
      if (m.veiculo_label && m.custo) {
        const placa = m.veiculo_label.split(" ")[0];
        custos[placa] = (custos[placa] || 0) + m.custo;
      }
    });
    return Object.entries(custos).sort((a, b) => b[1] - a[1]).slice(0, 5).map(([nome, custo]) => ({ nome, custo }));
  }, [manutencoes]);

  return (
    <div>
      <PageHeader eyebrow="Visão Geral" title="Dashboard" description="Indicadores consolidados da frota." />

      {/* Cards de KPI */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400 mb-1">Fornecedores</p><p className="text-3xl font-bold text-slate-100">{kpis.totalFornecedores}</p></div>
          <div className="p-3 bg-sky-500/10 rounded-xl"><Truck className="size-6 text-sky-400" /></div>
        </div>
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400 mb-1">Custo Manutenções</p><p className="text-3xl font-bold text-amber-400">{brl(kpis.custoManutencoes)}</p></div>
          <div className="p-3 bg-amber-500/10 rounded-xl"><Wrench className="size-6 text-amber-400" /></div>
        </div>
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400 mb-1">Volume Abastecido</p><p className="text-3xl font-bold text-emerald-400">{kpis.volumeAbastecido.toLocaleString('pt-BR')} L</p></div>
          <div className="p-3 bg-emerald-500/10 rounded-xl"><Fuel className="size-6 text-emerald-400" /></div>
        </div>
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400 mb-1">Estados Atendidos</p><p className="text-3xl font-bold text-indigo-400">{kpis.estados}</p></div>
          <div className="p-3 bg-indigo-500/10 rounded-xl"><MapPin className="size-6 text-indigo-400" /></div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Fornecedores por Estado */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><MapPin className="size-5 text-sky-400" /> Top Fornecedores por Estado</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={fornecedoresPorEstado}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="estado" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="quantidade" fill="#0284c7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Custos de Manutenção */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><DollarSign className="size-5 text-amber-400" /> Custos de Manutenção (Mensal)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={custosManutencao}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="mes" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} formatter={(value: any) => brl(value)} />
                <Line type="monotone" dataKey="custo" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Volume Abastecido */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Fuel className="size-5 text-emerald-400" /> Volume Abastecido (Litros)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={volumeAbastecimento}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="mes" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="litros" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top 5 Veículos */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Users className="size-5 text-purple-400" /> Top 5 Veículos (Custo Manutenção)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={topVeiculos} dataKey="custo" nameKey="nome" cx="50%" cy="50%" outerRadius={80} fill="#8884d8" label>
                  {topVeiculos.map((entry, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} formatter={(value: any) => brl(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
