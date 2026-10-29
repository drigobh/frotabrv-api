import { useQuery } from "@tanstack/react-query";
import { CalendarClock, Wrench } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useVeiculos } from "@/hooks/useCadastros";

export default function Agendamento() {
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: veiculos = [] } = useVeiculos();

  // Filtra apenas as manutenções que têm próxima revisão e ainda não chegaram lá
  const agendadas = manutencoes
    .filter(m => m.proxima_revisao_km)
    .map(m => {
      const v = veiculos.find((x: any) => x.id === m.veiculo_id);
      const kmAtual = v?.hodometro_km || 0;
      const falta = m.proxima_revisao_km - kmAtual;
      return { ...m, kmAtual, falta };
    })
    .sort((a, b) => a.falta - b.falta);

  return (
    <div>
      <PageHeader eyebrow="Operação" title="Agendamento de Manutenções" description="Controle de revisões preventivas por KM." />
      
      <div className="glass rounded-2xl overflow-hidden mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">KM Atual</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Próx. Revisão</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status do Prazo</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {agendadas.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-slate-500 py-8">Nenhuma revisão agendada.</TableCell>
              </TableRow>
            ) : (
              agendadas.map((m, i) => (
                <TableRow key={i} className="border-slate-800">
                  <TableCell className="text-slate-200 font-medium">{m.veiculo_label}</TableCell>
                  <TableCell className="text-slate-400">{m.kmAtual.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell className="text-slate-400">{m.proxima_revisao_km.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell>
                    {m.falta <= 0 ? (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-rose-500/20 text-rose-400 text-xs font-bold">
                        <Wrench className="size-3" /> Atrasada ({Math.abs(m.falta).toLocaleString('pt-BR')} km)
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-amber-500/20 text-amber-400 text-xs font-bold">
                        <CalendarClock className="size-3" /> Faltam {m.falta.toLocaleString('pt-BR')} km
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}