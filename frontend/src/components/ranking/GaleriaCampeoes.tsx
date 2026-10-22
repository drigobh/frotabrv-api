import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Crown, MailCheck, Send, Trophy } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";
import { dataHoraBR, errMsg, mesCurto, num } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useMe } from "@/hooks/useSession";
import type { HistoricoCampeoes, ParabensEnvio } from "@/types/ranking";

const MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
const mesLongo = (ym: string) => `${MESES[Number(ym.slice(5, 7)) - 1]} ${ym.slice(0, 4)}`;

export function GaleriaCampeoes() {
  const qc = useQueryClient();
  const { data: me } = useMe();
  const q = useQuery({ queryKey: ["ranking", "campeoes"], queryFn: () => apiGet<HistoricoCampeoes>("/ranking/campeoes") });
  const d = q.isError ? undefined : q.data;
  const enviar = useMutation({
    mutationFn: () => apiPost<ParabensEnvio>("/ranking/parabens/enviar"),
    onSuccess: (r) => {
      void qc.invalidateQueries({ queryKey: ["ranking", "campeoes"] });
      if (r.falhas.length) toast.warning(`Parabéns enviado a ${r.enviados} de ${r.destinatarios.length}`);
      else toast.success(`Parabéns enviado a ${r.enviados} destinatário(s)${r.motorista_email ? "" : " — campeão sem e-mail cadastrado"}`);
    },
    onError: (e) => toast.error(errMsg(e)),
  });
  const maxVit = Math.max(1, ...(d?.placar.map((p) => p.vitorias) ?? [1]));

  return (
    <section className="mt-8" data-testid="galeria-campeoes">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-amber-300">Hall da fama</p>
          <h2 className="mt-1 font-heading text-2xl font-semibold">Campeões de cada mês</h2>
          <p className="text-sm text-slate-400">No dia 1º às 7h o campeão do mês que fechou recebe um e-mail de parabéns, com cópia para os admins.</p>
        </div>
        {me?.perfil === "admin" && d && d.meses.length > 0 && (
          <Button variant="outline" onClick={() => enviar.mutate()} disabled={enviar.isPending} data-testid="parabens-enviar-agora">
            <Send className="size-4" /> {enviar.isPending ? "Enviando…" : `Reenviar parabéns de ${mesCurto(d.meses[0].mes)}`}
          </Button>
        )}
      </div>

      {d && d.meses.length === 0 && <p className="glass rounded-2xl p-8 text-center text-sm text-slate-500" data-testid="galeria-vazia">Ainda não há meses fechados com abastecimentos para eleger campeões.</p>}

      {d && d.meses.length > 0 && (
        <div className="grid gap-6 xl:grid-cols-12">
          <div className="glass rounded-2xl p-5 xl:col-span-4" data-testid="placar-vitorias">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold"><Crown className="size-4 text-amber-400" /> Placar de títulos</h3>
            <ol className="space-y-3">
              {d.placar.map((p, i) => (
                <li key={p.motorista_id} data-testid={`placar-item-${i + 1}`}>
                  <div className="mb-1 flex items-center justify-between gap-2 text-sm">
                    <span className={cn("truncate", i === 0 ? "font-semibold text-amber-200" : "text-slate-200")}>{p.motorista_nome}</span>
                    <span className="flex shrink-0 items-center gap-1 font-mono text-slate-100" data-testid={`placar-vitorias-${i + 1}`}>
                      {Array.from({ length: Math.min(p.vitorias, 6) }).map((_, k) => <Trophy key={k} className="size-3.5 text-amber-400" />)}
                      <span className="ml-1">{p.vitorias}×</span>
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-slate-800">
                    <div className="h-full rounded-full bg-gradient-to-r from-amber-500 to-orange-500 transition-[width] duration-700" style={{ width: `${(p.vitorias / maxVit) * 100}%` }} />
                  </div>
                  <p className="mt-1 text-[11px] text-slate-500">{p.meses.map(mesCurto).join(" · ")} · melhor {num(p.melhor_media, 2)} km/L</p>
                </li>
              ))}
            </ol>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:col-span-8 xl:grid-cols-3">
            {d.meses.map((c, i) => (
              <motion.article
                key={c.mes}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(i, 8) * 0.05, duration: 0.3 }}
                className={cn("glass relative overflow-hidden rounded-2xl p-4", i === 0 && "ring-1 ring-amber-400/40")}
                data-testid={`galeria-mes-${c.mes}`}
              >
                <div className="pointer-events-none absolute -right-8 -top-8 size-24 rounded-full bg-amber-400/10 blur-2xl" />
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-slate-400">{mesLongo(c.mes)}</span>
                  <div className="grid size-8 place-items-center rounded-full bg-gradient-to-br from-amber-300 to-orange-600"><Trophy className="size-4 text-amber-950" /></div>
                </div>
                <p className="mt-2 truncate text-base font-semibold text-slate-50" data-testid={`galeria-campeao-${c.mes}`}>{c.motorista_nome}</p>
                <p className="font-heading text-2xl font-semibold tabular-nums">{num(c.media_km_l, 2)} <span className="text-xs text-slate-500">km/L</span></p>
                <p className="mt-1 text-xs text-slate-400">{num(c.km_rodados)} km · {c.atingiu_meta ? "meta batida" : `meta ${num(c.meta_km_l, 2)}`}</p>
                {c.vice_nome && <p className="mt-1 truncate text-[11px] text-slate-500">Vice: {c.vice_nome} ({num(c.vice_media ?? 0, 2)})</p>}
                {c.parabens && (
                  <p className="mt-2 flex items-center gap-1 text-[11px] text-emerald-300" title={c.parabens.destinatarios.join(", ")} data-testid={`galeria-parabens-${c.mes}`}>
                    <MailCheck className="size-3.5" /> Parabéns enviado {dataHoraBR(c.parabens.enviado_em)}
                  </p>
                )}
              </motion.article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
