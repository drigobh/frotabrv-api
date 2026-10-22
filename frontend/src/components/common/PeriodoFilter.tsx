import { Input } from "@/components/ui/input";
import { PRESETS } from "@/lib/periodo";
import { cn } from "@/lib/utils";

interface Props {
  hoje: string;
  inicio: string;
  fim: string;
  onChange: (inicio: string, fim: string) => void;
  testId: string;
}

export function PeriodoFilter({ hoje, inicio, fim, onChange, testId }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2" data-testid={testId}>
      <Input type="date" value={inicio} max={fim || undefined} onChange={(e) => onChange(e.target.value, fim)} className="w-40" aria-label="Data inicial" data-testid={`${testId}-inicio`} />
      <span className="text-sm text-slate-500">até</span>
      <Input type="date" value={fim} min={inicio || undefined} onChange={(e) => onChange(inicio, e.target.value)} className="w-40" aria-label="Data final" data-testid={`${testId}-fim`} />
      <div className="flex flex-wrap gap-1">
        {PRESETS.map((p) => {
          const [i, f] = hoje ? p.range(hoje) : ["", ""];
          const ativo = i === inicio && f === fim;
          return (
            <button
              key={p.id}
              type="button"
              disabled={!hoje}
              onClick={() => onChange(i, f)}
              className={cn(
                "rounded-md border px-2.5 py-1 text-xs transition-colors duration-150",
                ativo ? "border-sky-500/60 bg-sky-500/15 text-sky-300" : "border-slate-800 text-slate-400 hover:border-slate-600 hover:text-slate-200",
              )}
              data-testid={`${testId}-preset-${p.id}`}
            >
              {p.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
