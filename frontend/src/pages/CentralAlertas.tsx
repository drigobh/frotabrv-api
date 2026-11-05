import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BellRing, CalendarClock, CheckCircle2, ChevronRight, ShieldAlert } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function CentralAlertas() {
  // Simulando a busca de alertas (num sistema real, viria do backend)
  const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });

  // Filtra os dados para criar os alertas reais
  const pneusCriticos = pneus.filter((p: any) => p.status === "Aplicado" && Number(p.profundidade_atual) <= 3);
  const osPendentes = manutencoes.filter((m: any) => m.status === "Aguardando aprovação");

  // Mocks de documentos (para o visual ficar completo como no 2.0)
  const documentosVencendo = [
    { id: 1, titulo: "CRLV do QPV1G90 vence em 15 dias", detalhe: "Documento digital disponível no Detran-SP", dias: 15, tipo: "Crítico" },
    { id: 2, titulo: "CNH do motorista Sérgio Nunes vence em 9 dias", detalhe: "Exame toxicológico vencido", dias: 9, tipo: "Crítico" },
    { id: 3, titulo: "Tacógrafo do QPL7D03 aferido há 22 meses", detalhe: "Aferição obrigatória a cada 24 meses", dias: 61, tipo: "Informativo" },
  ];

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Central de Alertas"
        description="Um só lugar para vencimentos de documento, CNH, pneu e manutenção."
        actions={
          <Button className="bg-sky-600 hover:bg-sky-500 h-9">
            <CalendarClock className="size-4 mr-2" /> Configurar Regras
          </Button>
        }
      />

      <div className="grid gap-4 xl:grid-cols-[1fr_360px]">
        {/* Lista Principal de Alertas */}
        <div className="glass rounded-2xl overflow-hidden border border-slate-800">
          <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4 bg-slate-900/50">
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <BellRing className="size-4 text-sky-400" /> Pendências Abertas
            </h2>
            <span className="text-xs text-slate-400">{documentosVencendo.length + pneusCriticos.length + osPendentes.length} alertas</span>
          </div>

          <ul className="divide-y divide-slate-800">
            {/* Alertas de Documentos */}
            {documentosVencendo.map((a) => (
              <li key={a.id} className="group flex items-start gap-3 px-5 py-4 transition-colors hover:bg-slate-800/30">
                <span className={cn("mt-1 grid size-7 shrink-0 place-items-center rounded-full", a.tipo === "Crítico" ? "bg-rose-500/10 text-rose-400" : "bg-sky-500/10 text-sky-400")}>
                  <CalendarClock className="size-3.5" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-bold text-slate-200">{a.titulo}</p>
                    <span className={cn("px-2 py-0.5 rounded text-[10px] font-bold uppercase", a.tipo === "Crítico" ? "bg-rose-500/20 text-rose-400" : "bg-sky-500/20 text-sky-400")}>{a.tipo}</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{a.detalhe}</p>
                  <div className="mt-1.5 flex items-center gap-3 text-[11px] text-slate-500">
                    <span>Documento</span> <span>·</span> <span>em {a.dias} dias</span>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="text-xs text-sky-400 hover:text-sky-300 hover:bg-sky-500/10">Resolver</Button>
              </li>
            ))}

            {/* Alertas de Pneus Críticos */}
            {pneusCriticos.map((p: any) => (
              <li key={p.id} className="group flex items-start gap-3 px-5 py-4 transition-colors hover:bg-slate-800/30">
                <span className="mt-1 grid size-7 shrink-0 place-items-center rounded-full bg-rose-500/10 text-rose-400">
                  <ShieldAlert className="size-3.5" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-bold text-slate-200">Pneu {p.numero_fogo} com sulco crítico</p>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/20 text-rose-400">Crítico</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">Profundidade: {p.profundidade_atual}mm (mínimo 3mm)</p>
                  <div className="mt-1.5 flex items-center gap-3 text-[11px] text-slate-500">
                    <span>Pneu</span> <span>·</span> <span>Troca Imediata</span>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="text-xs text-sky-400 hover:text-sky-300 hover:bg-sky-500/10">Trocar</Button>
              </li>
            ))}

            {/* Alertas de Manutenção */}
            {osPendentes.map((m: any) => (
              <li key={m.id} className="group flex items-start gap-3 px-5 py-4 transition-colors hover:bg-slate-800/30">
                <span className="mt-1 grid size-7 shrink-0 place-items-center rounded-full bg-amber-500/10 text-amber-400">
                  <AlertTriangle className="size-3.5" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm font-bold text-slate-200">OS {m.id.slice(0,6).toUpperCase()} aguardando aprovação</p>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-400">Atenção</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-400">Valor: {m.valor} · Requer aprovação do gestor</p>
                  <div className="mt-1.5 flex items-center gap-3 text-[11px] text-slate-500">
                    <span>Manutenção</span> <span>·</span> <span>Aguardando há 1 dia</span>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="text-xs text-sky-400 hover:text-sky-300 hover:bg-sky-500/10">Aprovar</Button>
              </li>
            ))}

            {documentosVencendo.length + pneusCriticos.length + osPendentes.length === 0 && (
              <li className="flex flex-col items-center justify-center py-12 text-slate-500">
                <CheckCircle2 className="size-10 text-emerald-500 mb-2" />
                <p className="text-sm font-medium">Tudo em dia!</p>
                <p className="text-xs">Nenhum alerta crítico no momento.</p>
              </li>
            )}
          </ul>
        </div>

        {/* Painel Lateral de Regras */}
        <div className="space-y-4">
          <div className="glass rounded-2xl border border-slate-800 p-5">
            <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
              <CheckCircle2 className="size-4 text-sky-400" /> Regras de Antecedência
            </h3>
            <ul className="space-y-3 text-sm">
              {[
                { nome: "Documento do veículo (CRLV)", dias: 45, ativo: true },
                { nome: "CNH do motorista", dias: 60, ativo: true },
                { nome: "Revisão preventiva por km", dias: 1000, ativo: true },
                { nome: "Pneu abaixo de 3 mm", dias: 0, ativo: true },
                { nome: "Tacógrafo e aferição", dias: 90, ativo: false },
              ].map((r, i) => (
                <li key={i} className="flex items-center justify-between gap-3 border-b border-slate-800 pb-3 last:border-0 last:pb-0">
                  <div>
                    <p className="text-slate-300 font-medium">{r.nome}</p>
                    <p className="text-[10px] text-slate-500">{r.dias === 0 ? "Avisar ao detectar" : `Avisar ${r.dias} dias antes`}</p>
                  </div>
                  <div className={cn("w-8 h-4 rounded-full relative transition-colors", r.ativo ? "bg-sky-500" : "bg-slate-700")}>
                    <div className={cn("absolute top-0.5 size-3 rounded-full bg-white transition-all", r.ativo ? "left-[18px]" : "left-0.5")} />
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
