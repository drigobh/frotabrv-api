import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { Clock, TimerOff } from "lucide-react";
import { Button } from "@/components/ui/button";

export function SessionTimer({ timeoutMinutos, onTimeout }: { timeoutMinutos: number, onTimeout: () => void }) {
  const desativado = timeoutMinutos <= 0;
  const [segundosRestantes, setSegundosRestantes] = useState(desativado ? 0 : timeoutMinutos * 60);
  const [mostrarAviso, setMostrarAviso] = useState(false);
  const [avisoUsado, setAvisoUsado] = useState(false);

  useEffect(() => {
    if (desativado) return;
    if (segundosRestantes <= 0) {
      onTimeout();
      return;
    }

    if (segundosRestantes === 30 && !avisoUsado) {
      setMostrarAviso(true);
      setAvisoUsado(true);
    }

    const interval = setInterval(() => {
      setSegundosRestantes((s) => s - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [segundosRestantes, onTimeout, desativado, avisoUsado]);

  if (desativado) {
    return (
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-500/10 text-purple-400" title="Timer de sessão desativado">
        <TimerOff className="size-3.5" />
      </div>
    );
  }

  const minutos = Math.floor(segundosRestantes / 60);
  const segundos = segundosRestantes % 60;

  return (
    <>
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/50 text-xs text-slate-400">
        <Clock className="size-3.5" />
        <span className="font-mono">{String(minutos).padStart(2, '0')}:{String(segundos).padStart(2, '0')}</span>
      </div>

      {/* Aviso Centralizado (Portal) */}
      {mostrarAviso && createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center mb-4">
              <TimerOff className="size-6 text-amber-400" />
            </div>
            <h2 className="text-lg font-bold text-slate-100 mb-2">Sessão Expirando</h2>
            <p className="text-sm text-slate-400 mb-6">
              Você será desconectado automaticamente em <strong className="text-amber-400">30 segundos</strong>.
            </p>
            <div className="flex justify-center gap-3">
              <Button 
                onClick={() => {
                  setSegundosRestantes(timeoutMinutos * 60);
                  setMostrarAviso(false);
                }}
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                Continuar Conectado
              </Button>
              <Button 
                variant="outline" 
                onClick={onTimeout}
                className="border-slate-700 text-slate-300"
              >
                Sair Agora
              </Button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
