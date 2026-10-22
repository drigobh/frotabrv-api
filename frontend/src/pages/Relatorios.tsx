import { useState } from "react";
import { FileSpreadsheet, FileText, Fuel, Link2, Wrench } from "lucide-react";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";
import { PageHeader } from "@/components/common/PageHeader";
import { PeriodoFilter } from "@/components/common/PeriodoFilter";
import { useHoje } from "@/hooks/useSession";
import { inicioMes } from "@/lib/periodo";
import { dataBR } from "@/lib/format";

type TipoRelatorio = "abastecimentos" | "manutencoes" | "acoplamentos";

const RELATORIOS: { tipo: TipoRelatorio; titulo: string; descricao: string; icon: typeof Fuel; cor: string }[] = [
  { tipo: "abastecimentos", titulo: "Abastecimentos", descricao: "Litros, valores, KM rodados e média KM/L por lançamento, com totais.", icon: Fuel, cor: "text-sky-400" },
  { tipo: "manutencoes", titulo: "Manutenções", descricao: "Preventivas e corretivas com oficina, status, próxima revisão e custo total.", icon: Wrench, cor: "text-amber-400" },
  { tipo: "acoplamentos", titulo: "Acoplamentos", descricao: "Histórico de movimentações: novos conjuntos, trocas, liberações e exclusões.", icon: Link2, cor: "text-emerald-400" },
];

export default function Relatorios() {
  const hoje = useHoje();
  const [periodo, setPeriodo] = useState<[string, string] | null>(null);
  const [inicio, fim] = periodo ?? (hoje ? [inicioMes(hoje), hoje] : ["", ""]);
  const valido = Boolean(inicio && fim && inicio <= fim);
  // Download direto pelo navegador: mesma origem, o cookie de sessão acompanha a requisição.
  const href = (tipo: TipoRelatorio, formato: "pdf" | "csv") => `/api/relatorios/${tipo}?inicio=${inicio}&fim=${fim}&formato=${formato}`;

  return (
    <div>
      <PageHeader eyebrow="Gestão" title="Relatórios" description="Escolha o período e baixe em PDF (para imprimir/enviar) ou CSV (para abrir no Excel)." />
      <div className="glass mb-6 rounded-2xl p-5">
        <p className="mb-3 text-sm text-slate-400">Período {valido && <span className="text-slate-200">· {dataBR(inicio)} a {dataBR(fim)}</span>}</p>
        <PeriodoFilter hoje={hoje} inicio={inicio} fim={fim} onChange={(i, f) => setPeriodo([i, f])} testId="relatorio-periodo" />
        {!valido && inicio && fim && <p className="mt-2 text-xs text-red-300">A data inicial deve ser anterior à final.</p>}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {RELATORIOS.map((r) => (
          <article key={r.tipo} className="glass flex flex-col rounded-2xl p-5 transition-transform duration-200 hover:-translate-y-0.5" data-testid={`relatorio-card-${r.tipo}`}>
            <r.icon className={cn("size-6", r.cor)} />
            <h2 className="mt-3 text-lg font-semibold">{r.titulo}</h2>
            <p className="mt-1 flex-1 text-sm text-slate-400">{r.descricao}</p>
            <div className={cn("mt-5 flex gap-2", !valido && "pointer-events-none opacity-50")}>
              <a href={href(r.tipo, "pdf")} download className={buttonVariants({ variant: "default" })} data-testid={`relatorio-${r.tipo}-pdf`}>
                <FileText className="size-4" /> PDF
              </a>
              <a href={href(r.tipo, "csv")} download className={buttonVariants({ variant: "outline" })} data-testid={`relatorio-${r.tipo}-csv`}>
                <FileSpreadsheet className="size-4" /> CSV
              </a>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
