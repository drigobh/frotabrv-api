import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const TONES = {
  ativo: "bg-emerald-950/70 text-emerald-300 border-emerald-800/60",
  inativo: "bg-slate-800/80 text-slate-300 border-slate-700",
  acoplado: "bg-blue-950/70 text-blue-300 border-blue-800/60",
  desacoplado: "bg-amber-950/70 text-amber-300 border-amber-800/60",
  excluido: "bg-red-950/70 text-red-300 border-red-800/60",
  info: "bg-sky-950/70 text-sky-300 border-sky-800/60",
} as const;

export type Tone = keyof typeof TONES;

export function StatusBadge({ tone, children, testId }: { tone: Tone; children: ReactNode; testId?: string }) {
  return (
    <span
      data-testid={testId}
      className={cn(
        "inline-flex items-center gap-1 whitespace-nowrap rounded-md border px-2 py-0.5 text-xs font-medium",
        TONES[tone],
      )}
    >
      {children}
    </span>
  );
}
