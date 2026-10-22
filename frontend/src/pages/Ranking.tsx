import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "motion/react";
import { Award, Medal, Pencil, Target, Trophy } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPut } from "@/lib/api";
import { errMsg, mesCurto, num } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";
import { GaleriaCampeoes } from "@/components/ranking/GaleriaCampeoes";
import { useHoje, useMe } from "@/hooks/useSession";
import type { MetaIn, Ranking as RankingData, RankingItem } from "@/types/ranking";

const PODIO = [
  { icon: Trophy, cor: "text-amber-300", ring: "ring-amber-400/40", bg: "from-amber-500/15" },
  { icon: Medal, cor: "text-slate-200", ring: "ring-slate-300/30", bg: "from-slate-400/10" },
  { icon: Award, cor: "text-orange-300", ring: "ring-orange-400/30", bg: "from-orange-500/10" },
];

function Barra({ item }: { item: RankingItem }) {
  const pct = Math.min(item.percentual_meta, 130) / 1.3;
  return (
    <div className="relative h-2 w-40 overflow-hidden rounded-full bg-slate-800">
      <div className={cn("h-full rounded-full transition-[width] duration-700", item.atingiu_meta ? "bg-emerald-500" : "bg-amber-500")} style={{ width: `${pct}%` }} />
      <div className="absolute inset-y-0 w-px bg-slate-300/70" style={{ left: `${100 / 1.3}%` }} title="Meta" />
    </div>
  );
}

export default function Ranking() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const [mesSel, setMesSel] = useState<string | null>(null);
  const mes = mesSel ?? hoje.slice(0, 7);
  const [editMeta, setEditMeta] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["ranking", mes], queryFn: () => apiGet<RankingData>(`/ranking?mes=${mes}`), enabled: Boolean(mes) });
  const d = q.isError ? undefined : q.data;
  const salvarMeta = useMutation({
    mutationFn: (body: MetaIn) => apiPut<MetaIn>("/ranking/meta", body),
    onSuccess: () => { toast.success("Meta atualizada"); setEditMeta(null); void qc.invalidateQueries({ queryKey: ["ranking"] }); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const batidas = d?.itens.filter((i) => i.atingiu_meta).length ?? 0;

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Ranking de motoristas"
        description="Média KM/L do mês por motorista, calculada a partir dos abastecimentos. Quem bate a meta da frota ganha destaque."
        actions={
          <Input type="month" value={mes} max={hoje.slice(0, 7) || undefined} onChange={(e) => e.target.value && setMesSel(e.target.value)} className="w-44" aria-label="Mês" data-testid="ranking-mes-input" />
        }
      />

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center justify-between text-sm text-slate-400"><span className="flex items-center gap-2"><Target className="size-4 text-sky-400" /> Meta da frota</span>
            {me?.perfil === "admin" && editMeta === null && (
              <Button size="icon-sm" variant="ghost" aria-label="Editar meta" onClick={() => setEditMeta(String(d?.meta_km_l ?? ""))} data-testid="ranking-meta-edit"><Pencil className="size-4" /></Button>
            )}
          </div>
          {editMeta === null ? (
            <p className="mt-2 font-heading text-3xl font-semibold tabular-nums" data-testid="ranking-meta-valor">{d ? num(d.meta_km_l, 2) : "…"} <span className="text-base text-slate-500">km/L</span></p>
          ) : (
            <form className="mt-2 flex gap-2" onSubmit={(e) => { e.preventDefault(); salvarMeta.mutate({ meta_km_l: Number(editMeta.replace(",", ".")) }); }}>
              <Input autoFocus inputMode="decimal" value={editMeta} onChange={(e) => setEditMeta(e.target.value)} className="w-28" data-testid="ranking-meta-input" />
              <Button type="submit" disabled={salvarMeta.isPending} data-testid="ranking-meta-save">Salvar</Button>
              <Button type="button" variant="ghost" onClick={() => setEditMeta(null)} data-testid="ranking-meta-cancel">Cancelar</Button>
            </form>
          )}
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-sm text-slate-400">Média da frota em {mes ? mesCurto(mes) : "…"}</p>
          <p className="mt-2 font-heading text-3xl font-semibold tabular-nums" data-testid="ranking-media-frota">{d?.media_frota != null ? num(d.media_frota, 2) : "—"} <span className="text-base text-slate-500">km/L</span></p>
        </div>
        <div className="glass rounded-2xl p-5">
          <p className="text-sm text-slate-400">Bateram a meta</p>
          <p className="mt-2 font-heading text-3xl font-semibold tabular-nums" data-testid="ranking-batidas">{batidas}<span className="text-base text-slate-500"> / {d?.itens.length ?? 0} motoristas</span></p>
        </div>
      </div>

      {d && d.itens.length > 0 && (
        <div className="mb-6 grid gap-4 md:grid-cols-3" data-testid="ranking-podio">
          {d.itens.slice(0, 3).map((it, i) => {
            const P = PODIO[i];
            return (
              <motion.div
                key={it.motorista_id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08, duration: 0.35 }}
                className={cn("glass relative overflow-hidden rounded-2xl bg-gradient-to-br to-transparent p-5 ring-1", P.bg, P.ring)}
                data-testid={`ranking-podio-${i + 1}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs uppercase tracking-[0.2em] text-slate-500">{i + 1}º lugar</span>
                  <P.icon className={cn("size-6", P.cor)} />
                </div>
                <p className="mt-3 text-lg font-semibold text-slate-50">{it.motorista_nome}</p>
                <p className="mt-1 font-heading text-3xl font-semibold tabular-nums text-slate-50">{num(it.media_km_l, 2)} <span className="text-sm text-slate-500">km/L</span></p>
                <p className="mt-2 text-xs text-slate-400">{num(it.km_rodados)} km · {num(it.litros, 0)} L · {num(it.percentual_meta, 0)}% da meta</p>
              </motion.div>
            );
          })}
        </div>
      )}

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="ranking-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["#", "Motorista", "Abastec.", "KM rodados", "Litros", "Média KM/L", "Meta", ""].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {d && d.itens.length === 0 && (
              <TableRow><TableCell colSpan={8} className="py-10 text-center text-slate-500">Sem abastecimentos com motorista e KM neste mês.</TableCell></TableRow>
            )}
            {d?.itens.map((it) => (
              <TableRow key={it.motorista_id} className="border-slate-800/70" data-testid={`ranking-row-${it.posicao}`}>
                <TableCell className="font-mono text-slate-400">{it.posicao}º</TableCell>
                <TableCell className="font-medium text-slate-100">{it.motorista_nome}</TableCell>
                <TableCell className="tabular-nums">{it.abastecimentos}</TableCell>
                <TableCell className="tabular-nums">{num(it.km_rodados)}</TableCell>
                <TableCell className="tabular-nums">{num(it.litros, 1)}</TableCell>
                <TableCell className="font-semibold tabular-nums">{num(it.media_km_l, 2)}</TableCell>
                <TableCell><Barra item={it} /></TableCell>
                <TableCell>
                  <StatusBadge tone={it.atingiu_meta ? "ativo" : "desacoplado"} testId={`ranking-status-${it.posicao}`}>
                    {it.atingiu_meta ? "Meta batida" : `${num(it.percentual_meta, 0)}%`}
                  </StatusBadge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <GaleriaCampeoes />
    </div>
  );
}
