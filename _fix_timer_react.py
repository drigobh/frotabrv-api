import os
import re

# ==========================================
# 1. REESCREVER O SESSION TIMER (COM useEffect)
# ==========================================
path_timer = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "SessionTimer.tsx")

conteudo_timer = r'''import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { Clock, TimerOff } from "lucide-react";
import { Button } from "@/components/ui/button";

export function SessionTimer({ timeoutMinutos, onTimeout }: { timeoutMinutos: number, onTimeout: () => void }) {
  const desativado = timeoutMinutos <= 0;
  const [segundosRestantes, setSegundosRestantes] = useState(desativado ? 0 : timeoutMinutos * 60);
  const [mostrarAviso, setMostrarAviso] = useState(false);
  const [avisoUsado, setAvisoUsado] = useState(false);

  // Sincroniza o estado quando o timeoutMinutos mudar (ex: ao carregar o perfil)
  useEffect(() => {
    if (!desativado) {
      setSegundosRestantes(timeoutMinutos * 60);
    }
  }, [timeoutMinutos, desativado]);

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
'''

with open(path_timer, "w", encoding="utf-8") as f:
    f.write(conteudo_timer)
print("✅ SessionTimer.tsx corrigido com useEffect (sincroniza com o perfil).")

# ==========================================
# 2. FORÇAR ATUALIZAÇÃO DO REACT QUERY AO SALVAR PERFIL
# ==========================================
path_perfil = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path_perfil, "r", encoding="utf-8") as f:
    p_c = f.read()

# Garantir que o useQueryClient está importado
if "useQueryClient" not in p_c:
    p_c = p_c.replace(
        'import { useQuery, useMutation } from "@tanstack/react-query";',
        'import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";'
    )

# Adicionar o useQueryClient e invalidar o "me" ao salvar
if "const qc = useQueryClient();" not in p_c:
    p_c = p_c.replace(
        'export default function Perfis() {',
        'export default function Perfis() {\n  const qc = useQueryClient();'
    )

# Invalidar o "me" no onSuccess do salvar
p_c = p_c.replace(
    'onSuccess: () => {\n      toast.success(editando ? "Perfil atualizado!" : "Perfil criado!");',
    'onSuccess: () => {\n      qc.invalidateQueries({ queryKey: ["me"] });\n      toast.success(editando ? "Perfil atualizado!" : "Perfil criado!");'
)

with open(path_perfil, "w", encoding="utf-8") as f:
    f.write(p_c)
print("✅ Perfis.tsx: React Query invalida o 'me' ao salvar um perfil.")

print("✅ Tudo pronto! Faça o git push.")