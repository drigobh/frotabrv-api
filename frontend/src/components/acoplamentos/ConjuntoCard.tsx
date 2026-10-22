import { useState } from "react";
import { ArrowLeftRight, Trash2, Unlink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { FieldSelect, type Option } from "@/components/common/FieldSelect";
import { StatusBadge } from "@/components/common/StatusBadge";
import { dataHoraBR } from "@/lib/format";
import type { Acoplamento, Campo } from "@/types/acoplamentos";
import { ICONE } from "./HistoricoTimeline";

export const NENHUM = "__none__";
const NOMES: Record<Campo, string> = { veiculo: "Cavalo", carreta: "Carreta", motorista: "Motorista" };

interface Props {
  acop: Acoplamento;
  disponiveis: Record<Campo, Option[]>;
  isAdmin: boolean;
  pending: boolean;
  onTrocar: (campo: Campo, novoId: string | null) => Promise<unknown>;
  onLiberar: () => void;
  onExcluir: () => void;
}

export function ConjuntoCard({ acop, disponiveis, isAdmin, pending, onTrocar, onLiberar, onExcluir }: Props) {
  const [troca, setTroca] = useState<Campo | null>(null);
  const [novo, setNovo] = useState("");
  const [confirm, setConfirm] = useState<"liberar" | "excluir" | null>(null);
  const slots: { campo: Campo; label: string | null }[] = [
    { campo: "veiculo", label: acop.veiculo_label },
    { campo: "carreta", label: acop.carreta_label },
    { campo: "motorista", label: acop.motorista_label },
  ];
  const placa = acop.veiculo_label.split(" · ")[0];
  const opcoesTroca = troca
    ? troca === "veiculo"
      ? disponiveis.veiculo
      : [{ value: NENHUM, label: "— Remover (desacoplar) —" }, ...disponiveis[troca]]
    : [];

  return (
    <article className="glass lift rounded-2xl p-4" data-testid={`conjunto-card-${placa}`}>
      <header className="mb-3 flex items-center justify-between gap-2">
        <div>
          <p className="font-mono text-lg font-medium text-slate-50">{placa}</p>
          <p className="text-xs text-slate-500">desde {dataHoraBR(acop.created_at)}</p>
        </div>
        {acop.completo ? (
          <StatusBadge tone="acoplado">Conjunto completo</StatusBadge>
        ) : (
          <StatusBadge tone="desacoplado">Incompleto</StatusBadge>
        )}
      </header>

      <ul className="space-y-1.5">
        {slots.map((s) => (
          <li key={s.campo} className="flex items-center justify-between gap-2 rounded-lg bg-slate-950/50 px-3 py-2">
            <div className="min-w-0">
              <p className="text-[10px] uppercase tracking-wider text-slate-500">{NOMES[s.campo]}</p>
              <p className={s.label ? "truncate text-sm text-slate-100" : "text-sm italic text-slate-500"}>
                <span className="mr-1.5" aria-hidden>{ICONE[s.campo]}</span>
                {s.label ?? "Não acoplado"}
              </p>
            </div>
            <Button
              size="xs"
              variant="ghost"
              className="text-sky-300 hover:text-sky-200"
              onClick={() => { setTroca(s.campo); setNovo(""); }}
              data-testid={`conjunto-${placa}-trocar-${s.campo}`}
            >
              <ArrowLeftRight className="size-3.5" /> {s.label ? "Trocar" : "Acoplar"}
            </Button>
          </li>
        ))}
      </ul>

      <footer className="mt-3 flex justify-end gap-2">
        {isAdmin && (
          <Button size="sm" variant="ghost" className="text-red-300 hover:text-red-200" onClick={() => setConfirm("excluir")} data-testid={`conjunto-${placa}-excluir`}>
            <Trash2 className="size-4" /> Excluir
          </Button>
        )}
        <Button size="sm" variant="outline" onClick={() => setConfirm("liberar")} data-testid={`conjunto-${placa}-liberar`}>
          <Unlink className="size-4" /> Liberar acoplamento
        </Button>
      </footer>

      <Dialog open={troca !== null} onOpenChange={(o) => !o && setTroca(null)}>
        <DialogContent data-testid="troca-dialog">
          <DialogHeader>
            <DialogTitle>{troca ? `${NOMES[troca]} do conjunto ${placa}` : ""}</DialogTitle>
            <DialogDescription>
              A troca registra o desacoplamento do item atual e o acoplamento do novo no histórico.
            </DialogDescription>
          </DialogHeader>
          <FieldSelect value={novo} onChange={setNovo} options={opcoesTroca} placeholder="Selecione o novo item" testId="troca-select" />
          {opcoesTroca.length === 0 && <p className="text-sm text-amber-300">Nenhum item disponível (todos acoplados ou inativos).</p>}
          <DialogFooter>
            <Button
              disabled={!novo || pending}
              onClick={() => troca && void onTrocar(troca, novo === NENHUM ? null : novo).then(() => setTroca(null))}
              data-testid="troca-confirm"
            >
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={confirm === "liberar"}
        onOpenChange={(o) => !o && setConfirm(null)}
        title={`Liberar conjunto ${placa}?`}
        description="Cavalo, carreta e motorista ficam disponíveis para novos acoplamentos. A operação fica registrada no histórico."
        confirmLabel="Liberar"
        pending={pending}
        onConfirm={() => { onLiberar(); setConfirm(null); }}
        testId="liberar"
      />
      <ConfirmDialog
        open={confirm === "excluir"}
        onOpenChange={(o) => !o && setConfirm(null)}
        title={`Excluir conjunto ${placa}?`}
        description="O acoplamento será marcado como Excluído (não é apagado do histórico)."
        confirmLabel="Excluir"
        destructive
        pending={pending}
        onConfirm={() => { onExcluir(); setConfirm(null); }}
        testId="excluir-acoplamento"
      />
    </article>
  );
}
