import { Link } from "react-router-dom";
import { motion } from "motion/react";
import { Flame, Trophy } from "lucide-react";
import { mesCurto, num } from "@/lib/format";
import type { Campeoes } from "@/types/dashboard";

const MESES_LONGOS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
const mesLongo = (ym: string) => MESES_LONGOS[Number(ym.slice(5, 7)) - 1] ?? ym;

// Selo do campeão de economia (mês fechado) + líder parcial do mês corrente.
export function CampeaoCard({ campeoes }: { campeoes: Campeoes }) {
  const { mes_passado: c, mes_atual: lider } = campeoes;
  return (
    <section className="glass relative overflow-hidden rounded-2xl p-5" data-testid="campeao-card">
      <div className="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full bg-amber-400/10 blur-3xl" />
      <div className="relative flex flex-wrap items-center gap-6">
        {c ? (
          <div className="flex items-center gap-5">
            <motion.div
              initial={{ scale: 0.6, rotate: -12, opacity: 0 }}
              animate={{ scale: 1, rotate: 0, opacity: 1 }}
              transition={{ type: "spring", stiffness: 220, damping: 14 }}
              className="relative grid size-20 shrink-0 place-items-center rounded-full bg-gradient-to-br from-amber-300 via-amber-500 to-orange-600 shadow-[0_0_32px_rgba(245,158,11,0.35)] ring-4 ring-amber-300/25"
              data-testid="campeao-selo"
            >
              <div className="grid size-16 place-items-center rounded-full border-2 border-dashed border-amber-100/60">
                <Trophy className="size-8 text-amber-950" />
              </div>
              <span className="absolute -bottom-2 rounded-full bg-slate-950 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-amber-300 ring-1 ring-amber-400/40">
                {mesCurto(c.mes)}
              </span>
            </motion.div>
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-amber-300">Campeão de economia · {mesLongo(c.mes)}</p>
              <p className="mt-1 font-heading text-2xl font-semibold text-slate-50" data-testid="campeao-nome">{c.motorista_nome}</p>
              <p className="mt-1 text-sm text-slate-400">
                <span className="font-semibold tabular-nums text-slate-100" data-testid="campeao-media">{num(c.media_km_l, 2)} km/L</span>
                {" · "}{num(c.km_rodados)} km · {c.atingiu_meta ? `bateu a meta de ${num(c.meta_km_l, 2)}` : `meta ${num(c.meta_km_l, 2)}`} · entre {c.participantes} motoristas
              </p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-500" data-testid="campeao-vazio">Sem dados de KM/L no mês passado para eleger um campeão.</p>
        )}

        <div className="ml-auto flex items-center gap-4">
          {lider && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3" data-testid="lider-atual">
              <p className="flex items-center gap-1.5 text-xs text-slate-400"><Flame className="size-3.5 text-orange-400" /> Líder parcial de {mesLongo(lider.mes)}</p>
              <p className="mt-1 font-medium text-slate-100" data-testid="lider-nome">{lider.motorista_nome}</p>
              <p className="text-xs tabular-nums text-slate-400">{num(lider.media_km_l, 2)} km/L {lider.atingiu_meta ? "· na meta" : ""}</p>
            </div>
          )}
          <Link to="/ranking" className="text-sm text-sky-400 transition-colors hover:text-sky-300" data-testid="campeao-ver-ranking">Ver ranking →</Link>
        </div>
      </div>
    </section>
  );
}
