import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, FileBadge, Gauge, Link2, Truck, UserRound, IdCard, Wrench } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { apiGet } from "@/lib/api";
import { brl, mesCurto, num } from "@/lib/format";
import { cn } from "@/lib/utils";
import { PageHeader } from "@/components/common/PageHeader";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { CampeaoCard } from "@/components/dashboard/CampeaoCard";
import { HistoricoTimeline } from "@/components/acoplamentos/HistoricoTimeline";
import { useMe } from "@/hooks/useSession";
import type { Dashboard as DashboardData, Kpi } from "@/types/dashboard";

const KPI_META: Record<Kpi["chave"], { icon: typeof Truck; color: string; format: (v: number) => string }> = {
  veiculos: { icon: Truck, color: "#38BDF8", format: (v) => num(v) },
  motoristas: { icon: UserRound, color: "#10B981", format: (v) => num(v) },
  acoplamentos: { icon: Link2, color: "#F59E0B", format: (v) => num(v) },
  km: { icon: Gauge, color: "#A3E635", format: (v) => `${num(v)}` },
};

export default function Dashboard() {
  const { data: me } = useMe();
  const q = useQuery({ queryKey: ["dashboard"], queryFn: () => apiGet<DashboardData>("/dashboard") });
  const d = q.isError ? undefined : q.data;

  const status = d?.status_frota;
  const totalFrota = status ? status.acoplados + status.disponiveis + status.em_manutencao : 0;
  const barras = status
    ? [
        { label: "Acoplados", valor: status.acoplados, cor: "bg-sky-500" },
        { label: "Disponíveis", valor: status.disponiveis, cor: "bg-emerald-500" },
        { label: "Em manutenção", valor: status.em_manutencao, cor: "bg-amber-500" },
      ]
    : [];

  return (
    <div>
      <PageHeader
        eyebrow="Central de operações"
        title={`Olá, ${me?.nome.split(" ")[0] ?? ""}`}
        description="Indicadores da frota em tempo real, custos dos últimos 6 meses e alertas que precisam de atenção."
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {d
          ? d.kpis.map((k) => <KpiCard key={k.chave} kpi={k} {...KPI_META[k.chave]} />)
          : Array.from({ length: 4 }).map((_, i) => <div key={i} className="glass h-[184px] animate-pulse rounded-2xl" />)}
      </div>

      {d && <div className="mt-6"><CampeaoCard campeoes={d.campeoes} /></div>}

      <div className="mt-6 grid gap-6 xl:grid-cols-12">
        <section className="glass rounded-2xl p-5 xl:col-span-8" data-testid="custos-chart">
          <div className="mb-4 flex items-baseline justify-between">
            <h2 className="text-lg font-semibold">Custos operacionais</h2>
            <p className="text-xs text-slate-500">Combustível × Manutenção</p>
          </div>
          <div className="h-64">
            {d && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={d.custos.map((c) => ({ ...c, mesLabel: mesCurto(c.mes) }))} barGap={4}>
                  <CartesianGrid stroke="#1E293B" vertical={false} />
                  <XAxis dataKey="mesLabel" stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748B" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v: number) => `${Math.round(v / 1000)}k`} />
                  <Tooltip
                    cursor={{ fill: "rgba(56,189,248,0.06)" }}
                    contentStyle={{ background: "#0F172A", border: "1px solid #334155", borderRadius: 10 }}
                    formatter={(value: number, name: string) => [brl(value), name === "combustivel" ? "Combustível" : "Manutenção"]}
                  />
                  <Bar dataKey="combustivel" fill="#38BDF8" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="manutencao" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>

        <section className="glass rounded-2xl p-5 xl:col-span-4" data-testid="status-frota">
          <h2 className="mb-4 text-lg font-semibold">Status da frota</h2>
          <div className="space-y-4">
            {barras.map((b) => (
              <div key={b.label}>
                <div className="mb-1 flex justify-between text-sm">
                  <span className="text-slate-300">{b.label}</span>
                  <span className="font-mono text-slate-100">{b.valor}</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                  <div className={cn("h-full rounded-full transition-[width] duration-700", b.cor)} style={{ width: `${totalFrota ? (b.valor / totalFrota) * 100 : 0}%` }} />
                </div>
              </div>
            ))}
            {status && <p className="pt-2 text-xs text-slate-500">{status.inativos} veículo(s) inativo(s) fora da operação.</p>}
          </div>
        </section>

        <section className="glass rounded-2xl p-5 xl:col-span-5" data-testid="alertas">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold">
            <AlertTriangle className="size-4 text-amber-400" /> Alertas
            {d && d.alertas.length > 0 && <span className="font-mono text-sm text-slate-500" data-testid="alertas-count">{d.alertas.length}</span>}
          </h2>
          {d && d.alertas.length === 0 && <p className="text-sm text-slate-500">Nenhum alerta no momento.</p>}
          <ul className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
            {d?.alertas.map((a, i) => (
              <li
                key={i}
                className={cn(
                  "flex items-start gap-3 rounded-lg border px-3 py-2.5",
                  a.severidade === "alta" ? "border-red-900/60 bg-red-950/30" : "border-amber-900/50 bg-amber-950/20",
                )}
                data-testid="alerta-item"
              >
                {a.tipo === "cnh" ? <IdCard className="mt-0.5 size-4 text-amber-300" /> : a.tipo === "documento" ? <FileBadge className="mt-0.5 size-4 text-sky-300" /> : <Wrench className="mt-0.5 size-4 text-amber-300" />}
                <div>
                  <p className="text-sm font-medium text-slate-100">{a.titulo}</p>
                  <p className="text-xs text-slate-400">{a.detalhe}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="glass rounded-2xl p-5 xl:col-span-7">
          <h2 className="mb-4 text-lg font-semibold">Últimas movimentações de acoplamento</h2>
          <HistoricoTimeline items={d?.historico_recente ?? []} testId="dashboard-historico" />
        </section>
      </div>
    </div>
  );
}
