import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { KeyRound, ShieldCheck, Truck } from "lucide-react";
import { toast } from "sonner";
import { apiPost } from "@/lib/api";
import { errMsg } from "@/lib/format";
import { beginSession } from "@/lib/session";
import { useMe } from "@/hooks/useSession";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { LoginOut } from "@/types/auth";

const HERO =
  "https://images.unsplash.com/photo-1618582948377-cd7eb0e8cb14?crop=entropy&cs=srgb&fm=jpg&q=80&w=1600";

export default function Login() {
  const navigate = useNavigate();
  const me = useMe();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [codigo, setCodigo] = useState("");
  const [precisa2fa, setPrecisa2fa] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  const login = useMutation({
    mutationFn: () => apiPost<LoginOut>("/auth/login", { email, senha, codigo: precisa2fa ? codigo : null }),
    onSuccess: (r) => {
      setErro(null);
      if (r.requires_2fa) {
        setPrecisa2fa(true);
        toast.info("Informe o código do Google Authenticator");
        return;
      }
      beginSession(r.token);
      navigate("/", { replace: true });
    },
    onError: (e) => setErro(errMsg(e)),
  });

  if (me.data) return <Navigate to="/" replace />;

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.2fr_1fr]">
      <div className="relative hidden overflow-hidden lg:block">
        <img src={HERO} alt="Caminhão em rodovia" className="absolute inset-0 size-full object-cover" />
        <div
          className="absolute inset-0"
          style={{ background: "linear-gradient(135deg, rgba(8,12,20,0.92) 0%, rgba(15,23,42,0.85) 50%, rgba(15,23,42,0.6) 100%)" }}
        />
        <div className="relative flex h-full flex-col justify-between p-12">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-lg bg-sky-500/15 ring-1 ring-sky-400/30">
              <Truck className="size-5 text-sky-400" />
            </div>
            <span className="font-heading text-xl font-semibold">Bravus Transportes</span>
          </div>
          <div className="max-w-lg">
            <p className="mb-3 font-mono text-xs uppercase tracking-[0.2em] text-sky-400">Central de operações</p>
            <h1 className="text-5xl font-semibold leading-[1.05] text-white">Toda a frota sob controle, em um só painel.</h1>
            <p className="mt-4 text-slate-300">
              Cavalos, carretas, motoristas, acoplamentos, abastecimentos e manutenções — com histórico completo de quem fez o quê e quando.
            </p>
          </div>
          <p className="text-xs text-slate-500">Uso interno · Bravus Transportes</p>
        </div>
      </div>

      <div className="flex items-center justify-center p-6">
        <form
          className="glass w-full max-w-md rounded-2xl p-8 animate-fade-up"
          onSubmit={(e) => { e.preventDefault(); login.mutate(); }}
          data-testid="login-form"
        >
          <div className="mb-6">
            <h2 className="text-2xl font-semibold">{precisa2fa ? "Verificação em duas etapas" : "Entrar"}</h2>
            <p className="mt-1 text-sm text-slate-400">
              {precisa2fa ? "Digite o código de 6 dígitos do Google Authenticator." : "Acesse com seu e-mail e senha corporativos."}
            </p>
          </div>

          {!precisa2fa ? (
            <div className="grid gap-4">
              <div className="grid gap-1.5">
                <Label htmlFor="login-email">E-mail</Label>
                <Input id="login-email" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} required data-testid="login-email-input" />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="login-senha">Senha</Label>
                <Input id="login-senha" type="password" autoComplete="current-password" value={senha} onChange={(e) => setSenha(e.target.value)} required data-testid="login-password-input" />
              </div>
            </div>
          ) : (
            <div className="grid gap-1.5">
              <Label htmlFor="login-codigo" className="flex items-center gap-1.5"><ShieldCheck className="size-4 text-emerald-400" /> Código 2FA</Label>
              <Input
                id="login-codigo"
                inputMode="numeric"
                maxLength={6}
                autoFocus
                value={codigo}
                onChange={(e) => setCodigo(e.target.value.replace(/\D/g, ""))}
                className="text-center font-mono text-2xl tracking-[0.5em]"
                data-testid="login-2fa-input"
              />
            </div>
          )}

          {erro && (
            <p className="mt-4 rounded-lg border border-red-900/60 bg-red-950/40 px-3 py-2 text-sm text-red-300" role="alert" aria-live="polite" data-testid="login-error">
              {erro}
            </p>
          )}

          <Button type="submit" className="mt-6 w-full" size="lg" disabled={login.isPending} data-testid="login-submit-button">
            <KeyRound className="size-4" /> {login.isPending ? "Entrando…" : precisa2fa ? "Verificar" : "Entrar"}
          </Button>
          {precisa2fa && (
            <button type="button" className="mt-3 w-full text-sm text-slate-400 hover:text-slate-200" onClick={() => { setPrecisa2fa(false); setCodigo(""); }} data-testid="login-back-button">
              Voltar
            </button>
          )}
        </form>
      </div>
    </div>
  );
}
