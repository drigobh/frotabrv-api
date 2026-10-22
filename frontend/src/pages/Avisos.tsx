import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarClock, Mail, Plus, Send, X } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut } from "@/lib/api";
import { brl, dataBR, dataHoraBR, errMsg } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AdminOnly } from "@/components/layout/AdminOnly";
import type { AvisoConfig, AvisoConfigIn, AvisoEnvio, AvisoItem, AvisoResumo } from "@/types/avisos";

function Lista({ titulo, itens, testId }: { titulo: string; itens: AvisoItem[]; testId: string }) {
  return (
    <div data-testid={testId}>
      <p className="mb-2 text-sm font-medium text-slate-300">{titulo} <span className="font-mono text-slate-500">({itens.length})</span></p>
      {itens.length === 0 ? (
        <p className="text-xs text-slate-500">Nada nos próximos 30 dias.</p>
      ) : (
        <ul className="max-h-56 space-y-1 overflow-y-auto pr-1">
          {itens.map((i, k) => (
            <li key={k} className="flex items-center justify-between gap-3 rounded-md bg-slate-900/50 px-2.5 py-1.5 text-sm">
              <span className="min-w-0 truncate text-slate-200" title={i.titulo}>{i.titulo}</span>
              <span className="flex shrink-0 items-center gap-2 text-xs">
                {i.valor != null && <span className="tabular-nums text-slate-300">{brl(i.valor)}</span>}
                <span className={cn("font-mono", i.dias < 0 ? "text-red-300" : "text-amber-300")}>{i.dias < 0 ? `vencido ${-i.dias}d` : `${dataBR(i.data)}`}</span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function AvisosConteudo() {
  const qc = useQueryClient();
  const [novo, setNovo] = useState("");
  const cfg = useQuery({ queryKey: ["avisos", "config"], queryFn: () => apiGet<AvisoConfig>("/avisos/config") });
  const previa = useQuery({ queryKey: ["avisos", "previa"], queryFn: () => apiGet<AvisoResumo>("/avisos/previa") });
  const envios = useQuery({ queryKey: ["avisos", "envios"], queryFn: () => apiGet<AvisoEnvio[]>("/avisos/envios") });
  const c = cfg.isError ? undefined : cfg.data;
  const p = previa.isError ? undefined : previa.data;

  const salvar = useMutation({
    mutationFn: (body: AvisoConfigIn) => apiPut<AvisoConfig>("/avisos/config", body),
    onSuccess: (data) => { qc.setQueryData(["avisos", "config"], data); setNovo(""); toast.success("Destinatários atualizados"); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const enviar = useMutation({
    mutationFn: () => apiPost<AvisoEnvio>("/avisos/enviar-agora"),
    onSuccess: (r) => {
      void qc.invalidateQueries({ queryKey: ["avisos", "envios"] });
      if (r.falhas.length) toast.warning(`Enviado para ${r.enviados} de ${r.destinatarios.length}. ${r.falhas[0]}`);
      else toast.success(`Resumo enviado para ${r.enviados} destinatário(s)`);
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const extras = c?.emails_extras ?? [];
  const adicionar = () => {
    const e = novo.trim().toLowerCase();
    if (!e) return;
    if (extras.includes(e) || c?.admins.includes(e)) return void toast.info("Este e-mail já recebe o aviso");
    salvar.mutate({ emails_extras: [...extras, e] });
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Avisos por e-mail"
        description="Toda segunda-feira às 7h (Brasília) sai um e-mail com documentos, CNHs e contas que vencem nos próximos 30 dias — inclusive os já vencidos."
        actions={
          <Button onClick={() => enviar.mutate()} disabled={enviar.isPending || !c?.destinatarios.length} data-testid="avisos-enviar-agora">
            <Send className="size-4" /> {enviar.isPending ? "Enviando…" : "Enviar agora"}
          </Button>
        }
      />

      <div className="grid gap-6 xl:grid-cols-12">
        <section className="glass rounded-2xl p-5 xl:col-span-5" data-testid="avisos-destinatarios">
          <h2 className="mb-1 flex items-center gap-2 text-lg font-semibold"><Mail className="size-4 text-sky-400" /> Destinatários</h2>
          <p className="mb-4 text-xs text-slate-500">Administradores ativos recebem automaticamente. Adicione outros e-mails (contador, gerente de frota…).</p>

          <p className="mb-1.5 text-xs uppercase tracking-wider text-slate-500">Administradores</p>
          <ul className="mb-4 flex flex-wrap gap-1.5">
            {(c?.admins ?? []).map((a) => <li key={a}><StatusBadge tone="info">{a}</StatusBadge></li>)}
          </ul>

          <p className="mb-1.5 text-xs uppercase tracking-wider text-slate-500">E-mails adicionais</p>
          <ul className="mb-3 flex flex-wrap gap-1.5" data-testid="avisos-extras-lista">
            {extras.length === 0 && <li className="text-xs text-slate-500">Nenhum.</li>}
            {extras.map((e) => (
              <li key={e} className="inline-flex items-center gap-1 rounded-md border border-slate-700 bg-slate-800/70 py-0.5 pl-2 pr-1 text-xs text-slate-200">
                {e}
                <button type="button" aria-label={`Remover ${e}`} onClick={() => salvar.mutate({ emails_extras: extras.filter((x) => x !== e) })}
                  className="rounded p-0.5 text-slate-400 transition-colors hover:bg-slate-700 hover:text-red-300" data-testid={`avisos-extra-remover-${e}`}>
                  <X className="size-3" />
                </button>
              </li>
            ))}
          </ul>
          <form className="flex gap-2" onSubmit={(ev) => { ev.preventDefault(); adicionar(); }}>
            <Input type="email" value={novo} onChange={(e) => setNovo(e.target.value)} placeholder="nome@empresa.com.br" data-testid="avisos-extra-input" />
            <Button type="submit" variant="outline" disabled={salvar.isPending || !novo.trim()} data-testid="avisos-extra-add"><Plus className="size-4" /> Adicionar</Button>
          </form>
          <p className="mt-3 text-xs text-slate-500">Total: <span className="text-slate-300" data-testid="avisos-total-destinatarios">{c?.destinatarios.length ?? 0}</span> destinatário(s)</p>
        </section>

        <section className="glass rounded-2xl p-5 xl:col-span-7" data-testid="avisos-previa">
          <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-lg font-semibold">Prévia do próximo e-mail</h2>
            {p && <p className="text-xs text-slate-500">janela até {dataBR(p.ate)} · a pagar {brl(p.total_pagar)} · a receber {brl(p.total_receber)}</p>}
          </div>
          {p ? (
            <div className="grid gap-5 md:grid-cols-3">
              <Lista titulo="Documentos e CNH" itens={p.documentos} testId="avisos-previa-documentos" />
              <Lista titulo="Contas a pagar" itens={p.contas_pagar} testId="avisos-previa-pagar" />
              <Lista titulo="Contas a receber" itens={p.contas_receber} testId="avisos-previa-receber" />
            </div>
          ) : (
            <div className="h-40 animate-pulse rounded-xl bg-slate-900/50" />
          )}
        </section>

        <section className="glass rounded-2xl p-5 xl:col-span-12" data-testid="avisos-historico">
          <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold"><CalendarClock className="size-4 text-emerald-400" /> Últimos envios</h2>
          {(envios.data ?? []).length === 0 ? (
            <p className="text-sm text-slate-500">Nenhum envio ainda. O primeiro automático sai na próxima segunda às 7h.</p>
          ) : (
            <ul className="divide-y divide-slate-800">
              {(envios.data ?? []).map((e) => (
                <li key={e.id} className="flex flex-wrap items-center gap-3 py-2.5 text-sm" data-testid="avisos-envio-item">
                  <span className="font-mono text-xs text-slate-400">{dataHoraBR(e.enviado_em)}</span>
                  <StatusBadge tone={e.origem === "agendado" ? "info" : "acoplado"}>{e.origem === "agendado" ? "Automático" : `Manual · ${e.usuario ?? ""}`}</StatusBadge>
                  <span className="text-slate-300">{e.itens} itens · {e.enviados}/{e.destinatarios.length} entregues</span>
                  {e.falhas.length > 0 && <span className="truncate text-xs text-red-300" title={e.falhas.join("\n")}>{e.falhas.length} falha(s)</span>}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

export default function Avisos() {
  return <AdminOnly><AvisosConteudo /></AdminOnly>;
}
