import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";
import { Truck, Wrench, Fuel, DollarSign, Users, MapPin } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { brl } from "@/lib/format";

const COLORS = ['#0284c7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard-resumo"],
    queryFn: () => apiGet<any>("/dashboard/resumo")
  });

  if (isLoading) return <div className="p-8 text-center text-slate-400">Carregando dashboard...</div>;

  const resumo = data || { fornecedores_por_estado: [], custos_manutencao: [], volume_abastecimentos: [], top_fornecedores: [] };

  return (
    <div>
      <PageHeader eyebrow="Visão Geral" title="Dashboard" description="Indicadores consolidados da frota." />

      {/* Cards de Resumo Rápidos */}
      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Total Fornecedores</p>
            <p className="text-3xl font-bold text-slate-100">
              {resumo.fornecedores_por_estado.reduce((acc: any, item: any) => acc + item.quantidade, 0)}
            </p>
          </div>
          <div className="p-3 bg-sky-500/10 rounded-xl"><Truck className="size-6 text-sky-400" /></div>
        </div>
        
        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Custo Manutenções</p>
            <p className="text-3xl font-bold text-amber-400">
              {brl(resumo.custos_manutencao.reduce((acc: any, item: any) => acc + item.custo, 0))}
            </p>
          </div>
          <div className="p-3 bg-amber-500/10 rounded-xl"><Wrench className="size-6 text-amber-400" /></div>
        </div>

        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Volume Abastecido</p>
            <p className="text-3xl font-bold text-emerald-400">
              {resumo.volume_abastecimentos.reduce((acc: any, item: any) => acc + item.litros, 0).toLocaleString('pt-BR')} L
            </p>
          </div>
          <div className="p-3 bg-emerald-500/10 rounded-xl"><Fuel className="size-6 text-emerald-400" /></div>
        </div>

        <div className="glass p-5 rounded-2xl flex justify-between items-center">
          <div>
            <p className="text-xs uppercase text-slate-400 mb-1">Estados Atendidos</p>
            <p className="text-3xl font-bold text-indigo-400">{resumo.fornecedores_por_estado.length}</p>
          </div>
          <div className="p-3 bg-indigo-500/10 rounded-xl"><MapPin className="size-6 text-indigo-400" /></div>
        </div>
      </div>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Gráfico 1: Fornecedores por Estado */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><MapPin className="size-5 text-sky-400" /> Top Fornecedores por Estado</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={resumo.fornecedores_por_estado.slice(0, 8)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="estado" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="quantidade" fill="#0284c7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico 2: Custos de Manutenção por Mês */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><DollarSign className="size-5 text-amber-400" /> Custos de Manutenção (Mensal)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={resumo.custos_manutencao}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="mes" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} formatter={(value: any) => brl(value)} />
                <Line type="monotone" dataKey="custo" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico 3: Volume de Abastecimento */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Fuel className="size-5 text-emerald-400" /> Volume Abastecido (Litros)</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={resumo.volume_abastecimentos}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="mes" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="litros" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Gráfico 4: Top 5 Fornecedores */}
        <div className="glass p-6 rounded-2xl">
          <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Users className="size-5 text-purple-400" /> Top 5 Fornecedores</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={resumo.top_fornecedores}
                  dataKey="quantidade"
                  nameKey="nome"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  label
                >
                  {resumo.top_fornecedores.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}
