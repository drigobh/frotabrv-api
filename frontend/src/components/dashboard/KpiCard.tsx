import { ArrowDownRight, ArrowUpRight, Minus, type LucideIcon } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import type { Kpi } from "@/types/dashboard";
import { cn } from "@/lib/utils";

interface Props {
  kpi: Kpi;
  icon: LucideIcon;
  format: (v: number) => string;
  color: string;
}

export function KpiCard({ kpi, icon: Icon, format, color }: Props) {
  const t = kpi.tendencia;
  const Trend = t == null || t === 0 ? Minus : t > 0 ? ArrowUpRight : ArrowDownRight;
  return (
    <article 
      className="glass lift relative overflow-hidden rounded-xl" 
      style={{ padding: '12px', height: '110px', display: 'flex', flexDirection: 'column' }}
      data-testid={`kpi-${kpi.chave}`}
    >
      <div className="flex items-start justify-between">
        <p className="text-xs text-slate-400">{kpi.titulo}</p>
        <Icon className="size-3.5 text-slate-500" />
      </div>
      <p 
        className="font-heading font-semibold tabular-nums text-slate-50" 
        style={{ fontSize: '24px', marginTop: '4px', lineHeight: '1.2' }}
        data-testid={`kpi-${kpi.chave}-value`}
      >
        {format(kpi.valor)}
      </p>
      <p
        className={cn(
          "inline-flex items-center gap-1 text-[10px]",
          t == null || t === 0 ? "text-slate-500" : t > 0 ? "text-emerald-400" : "text-red-400",
        )}
        style={{ marginTop: '2px' }}
        data-testid={`kpi-${kpi.chave}-trend`}
      >
        <Trend className="size-3" />
        {t == null ? "sem base anterior" : `${t > 0 ? "+" : ""}${t.toLocaleString("pt-BR")}% vs anterior`}
      </p>
      <div style={{ flex: 1, minHeight: '30px', marginTop: '4px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={kpi.serie} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={`spark-${kpi.chave}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area type="monotone" dataKey="valor" stroke={color} strokeWidth={2} fill={`url(#spark-${kpi.chave})`} isAnimationActive={false} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}
