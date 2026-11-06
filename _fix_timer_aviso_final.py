import os
import re

# ==========================================
# 1. BACKEND: GARANTIR QUE O TIMEOUT SEJA SALVO E RETORNADO
# ==========================================
path_perfis = os.path.join(os.getcwd(), "app", "backend", "routers", "perfis.py")

with open(path_perfis, "r", encoding="utf-8") as f:
    p_c = f.read()

# Garantir que a criação salve o timeout (aceitando 0)
if "timeout_minutos" not in p_c:
    p_c = p_c.replace(
        '"permissoes": body.get("permissoes", []),',
        '"permissoes": body.get("permissoes", []),\n        "timeout_minutos": body.get("timeout_minutos", 30),\n        "tentativas_login": body.get("tentativas_login", 5),'
    )
else:
    # Se já tem, garante que o valor 0 não seja ignorado
    p_c = p_c.replace(
        'body.get("timeout_minutos", 30)',
        'body.get("timeout_minutos") if body.get("timeout_minutos") is not None else 30'
    )

with open(path_perfis, "w", encoding="utf-8") as f:
    f.write(p_c)
print("✅ Backend: Perfis salvam timeout (incluindo 0 para desativar).")

# 2. Auth.py: Garantir que /auth/me retorne o timeout do perfil
path_auth = os.path.join(os.getcwd(), "app", "backend", "routers", "auth.py")

with open(path_auth, "r", encoding="utf-8") as f:
    a_c = f.read()

padrao_me = r'@router\.get\("/me"\)[\s\S]*?(?=@router|\Z)'
nova_rota_me = '''
@router.get("/me")
async def me(_u: dict = Depends(require("read"))):
    usuario = await db.usuarios.find_one({"id": _u["id"]}, {"_id": 0, "senha": 0})
    if not usuario:
        raise HTTPException(404, "Usuário não encontrado.")
    
    timeout = 30
    if usuario.get("perfil_id"):
        perfil = await db.perfis.find_one({"id": usuario["perfil_id"]}, {"_id": 0})
        if perfil:
            usuario["permissoes"] = perfil.get("permissoes", [])
            usuario["perfil_nome"] = perfil.get("nome", "")
            timeout = perfil.get("timeout_minutos", 30)
    
    usuario["timeout_minutos"] = timeout
    return usuario
'''
if re.search(padrao_me, a_c):
    a_c = re.sub(padrao_me, nova_rota_me.strip() + "\n\n", a_c)
    with open(path_auth, "w", encoding="utf-8") as f:
        f.write(a_c)
    print("✅ Backend: /auth/me retorna o timeout do perfil.")

# ==========================================
# 2. FRONTEND: CORRIGIR O SESSION TIMER
# ==========================================
path_timer = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "SessionTimer.tsx")

conteudo_timer = r'''import { useState, useEffect } from "react";
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

    // Mostra o aviso apenas uma vez, quando faltar 30 segundos
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

      {/* Modal de Aviso de 30 Segundos - Renderizado via Portal ou Fixed */}
      {mostrarAviso && (
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
                  // Reinicia o timer
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
        </div>
      )}
    </>
  );
}
'''

with open(path_timer, "w", encoding="utf-8") as f:
    f.write(conteudo_timer)
print("✅ SessionTimer: Aviso centralizado e limitação de uso.")

# ==========================================
# 3. FRONTEND: CORRIGIR O FORMULÁRIO DE PERFIL (TIMEOUT 0)
# ==========================================
path_perfil = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path_perfil, "r", encoding="utf-8") as f:
    pf_c = f.read()

# Ajustar o input de timeout para aceitar 0 e não dar fallback para 30
pf_c = pf_c.replace(
    'value={form.timeout_minutos || 30}',
    'value={form.timeout_minutos === 0 ? 0 : (form.timeout_minutos || 30)}'
)

# Ajustar o abrirEdicao para carregar o timeout real
pf_c = pf_c.replace(
    'timeout_minutos: p.timeout_minutos || 30',
    'timeout_minutos: p.timeout_minutos !== undefined ? p.timeout_minutos : 30'
)

with open(path_perfil, "w", encoding="utf-8") as f:
    f.write(pf_c)
print("✅ Perfis.tsx: Campo de timeout aceita 0 (desativado).")

print("✅ Tudo pronto! Faça o git push.")