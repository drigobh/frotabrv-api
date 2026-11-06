import { useState, useEffect } from "react";
import { Clock } from "lucide-react";

export function SessionTimer({ timeoutMinutos, onTimeout }: { timeoutMinutos: number, onTimeout: () => void }) {
  const [segundosRestantes, setSegundosRestantes] = useState(timeoutMinutos * 60);

  useEffect(() => {
    if (segundosRestantes <= 0) {
      onTimeout();
      return;
    }
    const interval = setInterval(() => {
      setSegundosRestantes((s) => s - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [segundosRestantes, onTimeout]);

  const minutos = Math.floor(segundosRestantes / 60);
  const segundos = segundosRestantes % 60;

  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/50 text-xs text-slate-400">
      <Clock className="size-3.5" />
      <span className="font-mono">{String(minutos).padStart(2, '0')}:{String(segundos).padStart(2, '0')}</span>
    </div>
  );
}
