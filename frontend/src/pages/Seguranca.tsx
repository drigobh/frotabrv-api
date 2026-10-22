import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { QrCode, ShieldCheck, ShieldOff } from "lucide-react";
import { toast } from "sonner";
import { apiPost } from "@/lib/api";
import { errMsg } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { useMe } from "@/hooks/useSession";
import type { OkOut, TwoFASetupOut, Usuario } from "@/types/auth";

export default function Seguranca() {
  const qc = useQueryClient();
  const { data: me } = useMe();
  const [setup, setSetup] = useState<TwoFASetupOut | null>(null);
  const [codigo, setCodigo] = useState("");
  const [senhas, setSenhas] = useState({ atual: "", nova: "", confirma: "" });

  const onError = (e: unknown) => toast.error(errMsg(e));
  const atualizarMe = (u: Usuario) => qc.setQueryData(["me"], u);

  const gerar = useMutation({ mutationFn: () => apiPost<TwoFASetupOut>("/auth/2fa/setup"), onSuccess: (s) => { setSetup(s); setCodigo(""); }, onError });
  const ativar = useMutation({
    mutationFn: () => apiPost<Usuario>("/auth/2fa/enable", { codigo }),
    onSuccess: (u) => { atualizarMe(u); setSetup(null); setCodigo(""); toast.success("2FA ativado com sucesso"); },
    onError,
  });
  const desativar = useMutation({
    mutationFn: () => apiPost<Usuario>("/auth/2fa/disable", { codigo }),
    onSuccess: (u) => { atualizarMe(u); setCodigo(""); toast.success("2FA desativado"); },
    onError,
  });
  const trocar = useMutation({
    mutationFn: () => apiPost<OkOut>("/auth/change-password", { senha_atual: senhas.atual, nova_senha: senhas.nova }),
    onSuccess: () => { setSenhas({ atual: "", nova: "", confirma: "" }); toast.success("Senha alterada"); },
    onError,
  });

  const codigoInput = (
    <Input
      inputMode="numeric"
      maxLength={6}
      placeholder="000000"
      value={codigo}
      onChange={(e) => setCodigo(e.target.value.replace(/\D/g, ""))}
      className="w-40 text-center font-mono text-lg tracking-[0.4em]"
      data-testid="twofa-code-input"
      aria-describedby="twofa-help"
    />
  );

  return (
    <div>
      <PageHeader eyebrow="Conta" title="Segurança" description="Proteja seu acesso com verificação em duas etapas e uma senha forte." />
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="glass rounded-2xl p-6" data-testid="twofa-section">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-lg font-semibold"><ShieldCheck className="size-5 text-emerald-400" /> Autenticação em 2 etapas</h2>
            <StatusBadge tone={me?.totp_enabled ? "ativo" : "inativo"} testId="twofa-status">{me?.totp_enabled ? "Ativo" : "Desativado"}</StatusBadge>
          </div>

          {me?.totp_enabled ? (
            <div className="space-y-3">
              <p id="twofa-help" className="text-sm text-slate-400">Para desativar, informe o código atual do Google Authenticator.</p>
              <div className="flex gap-2">
                {codigoInput}
                <Button variant="destructive" disabled={codigo.length !== 6 || desativar.isPending} onClick={() => desativar.mutate()} data-testid="twofa-disable-button">
                  <ShieldOff className="size-4" /> Desativar
                </Button>
              </div>
            </div>
          ) : setup ? (
            <div className="space-y-4">
              <ol className="list-decimal space-y-1 pl-5 text-sm text-slate-300">
                <li>Abra o Google Authenticator e escaneie o QR Code.</li>
                <li>Digite o código de 6 dígitos gerado pelo app.</li>
              </ol>
              <div className="flex flex-wrap items-center gap-5">
                <img src={setup.qr_code} alt="QR Code 2FA" className="size-44 rounded-xl bg-white p-2" data-testid="twofa-qr" />
                <div className="min-w-0 text-xs text-slate-400">
                  <p>Chave manual:</p>
                  <p className="mt-1 break-all font-mono text-sm text-slate-100" data-testid="twofa-secret">{setup.secret}</p>
                </div>
              </div>
              <p id="twofa-help" className="sr-only">Código de 6 dígitos</p>
              <div className="flex gap-2">
                {codigoInput}
                <Button disabled={codigo.length !== 6 || ativar.isPending} onClick={() => ativar.mutate()} data-testid="twofa-enable-button">Ativar 2FA</Button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p id="twofa-help" className="text-sm text-slate-400">Opcional, mas recomendado. Após ativar, o login pedirá também o código do app.</p>
              <Button onClick={() => gerar.mutate()} disabled={gerar.isPending} data-testid="twofa-setup-button"><QrCode className="size-4" /> Gerar QR Code</Button>
            </div>
          )}
        </section>

        <section className="glass rounded-2xl p-6">
          <h2 className="mb-4 text-lg font-semibold">Alterar senha</h2>
          <form
            className="grid gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              if (senhas.nova !== senhas.confirma) return void toast.error("A confirmação não confere");
              trocar.mutate();
            }}
          >
            <div className="grid gap-1.5"><Label htmlFor="s-atual">Senha atual</Label><Input id="s-atual" type="password" value={senhas.atual} onChange={(e) => setSenhas((s) => ({ ...s, atual: e.target.value }))} required data-testid="senha-atual-input" /></div>
            <div className="grid gap-1.5"><Label htmlFor="s-nova">Nova senha (mín. 8)</Label><Input id="s-nova" type="password" minLength={8} value={senhas.nova} onChange={(e) => setSenhas((s) => ({ ...s, nova: e.target.value }))} required data-testid="senha-nova-input" /></div>
            <div className="grid gap-1.5"><Label htmlFor="s-conf">Confirmar nova senha</Label><Input id="s-conf" type="password" minLength={8} value={senhas.confirma} onChange={(e) => setSenhas((s) => ({ ...s, confirma: e.target.value }))} required data-testid="senha-confirma-input" /></div>
            <Button type="submit" className="mt-1 w-fit" disabled={trocar.isPending} data-testid="senha-submit-button">Salvar nova senha</Button>
          </form>
        </section>
      </div>
    </div>
  );
}
