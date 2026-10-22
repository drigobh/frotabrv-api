import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api";
import { errMsg } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect, type Option } from "@/components/common/FieldSelect";
import { ConjuntoCard, NENHUM } from "@/components/acoplamentos/ConjuntoCard";
import { HistoricoTimeline } from "@/components/acoplamentos/HistoricoTimeline";
import { useCarretas, useMotoristas, useVeiculos } from "@/hooks/useCadastros";
import { useMe } from "@/hooks/useSession";
import type { Acoplamento, Campo, HistoricoItem } from "@/types/acoplamentos";

export default function Acoplamentos() {
  const qc = useQueryClient();
  const { data: me } = useMe();
  const acops = useQuery({ queryKey: ["acoplamentos"], queryFn: () => apiGet<Acoplamento[]>("/acoplamentos") });
  const hist = useQuery({ queryKey: ["historico"], queryFn: () => apiGet<HistoricoItem[]>("/acoplamentos/historico?limit=100") });
  const veiculos = useVeiculos();
  const carretas = useCarretas();
  const motoristas = useMotoristas();

  const [novo, setNovo] = useState({ veiculo: "", carreta: NENHUM, motorista: NENHUM });

  const disponiveis: Record<Campo, Option[]> = useMemo(
    () => ({
      veiculo: (veiculos.data ?? []).filter((v) => !v.acoplado).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` })),
      carreta: (carretas.data ?? []).filter((c) => !c.acoplado).map((c) => ({ value: c.id, label: `${c.codigo} · ${c.tipo}` })),
      motorista: (motoristas.data ?? []).filter((m) => !m.acoplado).map((m) => ({ value: m.id, label: m.nome })),
    }),
    [veiculos.data, carretas.data, motoristas.data],
  );

  // Toda operação de acoplamento afeta cadastros (badge Acoplado), histórico e dashboard.
  const refresh = () => void qc.invalidateQueries();
  const onError = (e: unknown) => toast.error(errMsg(e));

  const criar = useMutation({
    mutationFn: () =>
      apiPost<Acoplamento>("/acoplamentos", {
        veiculo_id: novo.veiculo,
        carreta_id: novo.carreta === NENHUM ? null : novo.carreta,
        motorista_id: novo.motorista === NENHUM ? null : novo.motorista,
      }),
    onSuccess: (a) => {
      toast.success(a.completo ? "Novo conjunto acoplado" : "Acoplamento parcial criado");
      setNovo({ veiculo: "", carreta: NENHUM, motorista: NENHUM });
      refresh();
    },
    onError,
  });
  const trocar = useMutation({
    mutationFn: ({ id, campo, novoId }: { id: string; campo: Campo; novoId: string | null }) =>
      apiPatch<Acoplamento>(`/acoplamentos/${id}`, { campo, novo_id: novoId }),
    onSuccess: () => { toast.success("Troca registrada"); refresh(); },
    onError,
  });
  const liberar = useMutation({
    mutationFn: (id: string) => apiPost<Acoplamento>(`/acoplamentos/${id}/liberar`),
    onSuccess: () => { toast.success("Acoplamento liberado"); refresh(); },
    onError,
  });
  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<Acoplamento>(`/acoplamentos/${id}`),
    onSuccess: () => { toast.success("Acoplamento excluído"); refresh(); },
    onError,
  });

  const lista = acops.isError ? [] : (acops.data ?? []);
  const pending = trocar.isPending || liberar.isPending || excluir.isPending;

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Acoplamentos"
        description="Monte conjuntos cavalo + carreta + motorista. Itens já acoplados não podem ser usados em outro conjunto."
      />

      <section className="glass mb-6 rounded-2xl p-5" data-testid="novo-acoplamento-form">
        <h2 className="mb-3 text-lg font-semibold">Novo acoplamento</h2>
        <div className="grid gap-3 md:grid-cols-[1fr_1fr_1fr_auto] md:items-end">
          <div className="grid gap-1.5">
            <Label>🚛 Cavalo *</Label>
            <FieldSelect value={novo.veiculo} onChange={(v) => setNovo((s) => ({ ...s, veiculo: v }))} options={disponiveis.veiculo} placeholder="Selecione o cavalo" testId="novo-acop-veiculo" />
          </div>
          <div className="grid gap-1.5">
            <Label>🚚 Carreta</Label>
            <FieldSelect value={novo.carreta} onChange={(v) => setNovo((s) => ({ ...s, carreta: v }))} options={[{ value: NENHUM, label: "— Nenhuma —" }, ...disponiveis.carreta]} testId="novo-acop-carreta" />
          </div>
          <div className="grid gap-1.5">
            <Label>👤 Motorista</Label>
            <FieldSelect value={novo.motorista} onChange={(v) => setNovo((s) => ({ ...s, motorista: v }))} options={[{ value: NENHUM, label: "— Nenhum —" }, ...disponiveis.motorista]} testId="novo-acop-motorista" />
          </div>
          <Button disabled={!novo.veiculo || criar.isPending} onClick={() => criar.mutate()} data-testid="novo-acop-submit">
            <Link2 className="size-4" /> Acoplar
          </Button>
        </div>
        <p className="mt-2 text-xs text-slate-500">O evento “Novo Conjunto” só é registrado quando cavalo, carreta e motorista estão preenchidos.</p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]">
        <section>
          <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
            Conjuntos ativos <span className="font-mono text-sm text-slate-500" data-testid="conjuntos-count">{lista.length}</span>
          </h2>
          {lista.length === 0 && (
            <p className="glass rounded-2xl p-8 text-center text-sm text-slate-500" data-testid="conjuntos-empty">
              {acops.isPending ? "Carregando…" : "Nenhum conjunto ativo."}
            </p>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            {lista.map((a) => (
              <ConjuntoCard
                key={a.id}
                acop={a}
                disponiveis={disponiveis}
                isAdmin={me?.perfil === "admin"}
                pending={pending}
                onTrocar={(campo, novoId) => trocar.mutateAsync({ id: a.id, campo, novoId })}
                onLiberar={() => liberar.mutate(a.id)}
                onExcluir={() => excluir.mutate(a.id)}
              />
            ))}
          </div>
        </section>
        <section className="glass h-fit rounded-2xl p-5">
          <h2 className="mb-4 text-lg font-semibold">Histórico de movimentações</h2>
          <div className="max-h-[720px] overflow-y-auto pr-1">
            <HistoricoTimeline items={hist.isError ? [] : (hist.data ?? [])} />
          </div>
        </section>
      </div>
    </div>
  );
}
