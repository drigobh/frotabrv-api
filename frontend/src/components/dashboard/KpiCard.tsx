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
  const hasSerie = kpi.serie && kpi.serie.length > 0;

  return (
    <article 
      className="glass relative overflow-hidden rounded-xl" 
      style={{ 
        padding: '12px 16px', 
        height: '90px', 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between' 
      }}
      data-testid={`kpi-${kpi.chave}`}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ 
          display: 'flex', alignItems: 'center', justifyContent: 'center', 
          width: '28px', height: '28px', borderRadius: '8px', 
          backgroundColor: `${color}20`, color: color 
        }}>
          <Icon size={16} />
        </div>
        <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>
          {kpi.titulo}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <p 
            style={{ fontSize: '22px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}
            data-testid={`kpi-${kpi.chave}-value`}
          >
            {format(kpi.valor)}
          </p>
          <p
            style={{ 
              fontSize: '10px', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '2px',
              color: t == null || t === 0 ? "#64748b" : t > 0 ? "#10b981" : "#ef4444" 
            }}
            data-testid={`kpi-${kpi.chave}-trend`}
          >
            <Trend size={12} />
            {t == null ? "sem base" : `${t > 0 ? "+" : ""}${t}%`}
          </p>
        </div>

        {hasSerie && (
          <div style={{ width: '60px', height: '30px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={kpi.serie}>
                <Area type="monotone" dataKey="valor" stroke={color} strokeWidth={2} fill={`${color}20`} isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </article>
  );
}
