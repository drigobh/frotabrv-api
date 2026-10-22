import { motion } from "motion/react";
import type { HistoricoItem } from "@/types/acoplamentos";
import { dataHoraBR } from "@/lib/format";
import { StatusBadge, type Tone } from "@/components/common/StatusBadge";

export const ICONE: Record<HistoricoItem["item"], string> = {
  veiculo: "🚛",
  carreta: "🚚",
  motorista: "👤",
  conjunto: "🚛🚚👤",
};

const TOM: Record<HistoricoItem["status"], Tone> = {
  Acoplado: "acoplado",
  Desacoplado: "desacoplado",
  Excluído: "excluido",
};

export function HistoricoTimeline({ items, testId = "historico" }: { items: HistoricoItem[]; testId?: string }) {
  if (items.length === 0) {
    return <p className="py-6 text-center text-sm text-slate-500" data-testid={`${testId}-empty`}>Sem movimentações.</p>;
  }
  return (
    <ol className="relative space-y-3 border-l border-slate-800 pl-5" data-testid={`${testId}-list`}>
      {items.map((h, i) => (
        <motion.li
          key={h.id}
          initial={{ opacity: 0, x: -4 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: Math.min(i * 0.03, 0.4), duration: 0.25 }}
          className="relative"
          data-testid={`${testId}-item`}
        >
          <span className="absolute -left-[27px] top-1.5 size-3 rounded-full border-2 border-[#0B0F17] bg-sky-500" />
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm font-medium text-slate-100">{h.evento}</span>
            <StatusBadge tone={TOM[h.status]}>{h.status}</StatusBadge>
            <span className="font-mono text-xs text-slate-500">{h.conjunto}</span>
          </div>
          <p className="mt-0.5 text-sm text-slate-300">
            <span className="mr-1.5" aria-hidden>{ICONE[h.item]}</span>
            {h.descricao}
          </p>
          <p className="mt-0.5 text-xs text-slate-500">
            {h.usuario} · {dataHoraBR(h.created_at)}
          </p>
        </motion.li>
      ))}
    </ol>
  );
}
