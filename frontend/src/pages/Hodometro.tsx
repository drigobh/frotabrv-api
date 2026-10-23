import { useQuery } from "@tanstack/react-query";
import { Gauge, Info, TrendingUp, DollarSign, Droplets } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, num } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

export default function Hodometro() {
  const { data, isLoading } = useQuery({
    queryKey: ["hodometro-atual"],
    queryFn: () => apiGet<any[]>("/abastecimentos/hodometro-atual"),
  });

  const rows = data ?? [];

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Hodômetro Atual"
        description="Acompanhamento em tempo real do último KM registrado e estatísticas por veículo."
      />

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs">Veículo</TableHead>
              <TableHead className="text-xs text-right">Último KM</TableHead>
              <TableHead className="text-xs text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && <TableRow><TableCell colSpan={3} className="text-center py-10">Carregando...</TableCell></TableRow>}
            {rows.map((v) => (
              <TableRow key={v.veiculo_id} className="border-slate-800/70">
                <TableCell>
                  <p className="font-mono font-medium text-slate-200">{v.placa}</p>
                  <p className="text-xs text-slate-500">{v.modelo}</p>
                </TableCell>
                <TableCell className="text-right font-mono text-sky-300 font-bold">{num(v.ultimo_km)} km</TableCell>
                <TableCell className="text-center">
                  <Dialog>
                    <DialogTrigger render={<Button variant="ghost" size="icon-sm" className="text-sky-400 hover:bg-sky-500/10" />}>
                      <Info className="size-5" />
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-md bg-[#0F172A] border-slate-800 text-slate-200">
                      <DialogHeader>
                        <DialogTitle className="flex items-center gap-2"><Gauge className="size-5 text-sky-400" /> Detalhes - {v.placa}</DialogTitle>
                      </DialogHeader>
                      <div className="grid grid-cols-2 gap-4 py-4">
                        <div className="p-3 bg-slate-900 rounded-lg">
                          <p className="text-xs text-slate-400 mb-1 flex items-center gap-1"><TrendingUp className="size-3" /> Abastecimentos</p>
                          <p className="text-lg font-bold">{v.qtd_geral} <span className="text-xs font-normal text-slate-500">total</span></p>
                          <p className="text-sm text-slate-300">{v.qtd_mes} este mês / {v.qtd_mes_anterior} mês ant.</p>
                        </div>
                        <div className="p-3 bg-slate-900 rounded-lg">
                          <p className="text-xs text-slate-400 mb-1 flex items-center gap-1"><Droplets className="size-3" /> Média KM/L</p>
                          <p className="text-lg font-bold text-sky-400">{num(v.media_ultimo, 2)} <span className="text-xs font-normal text-slate-500">último</span></p>
                          <p className="text-sm text-slate-300">{num(v.media_mes, 2)} este mês / {num(v.media_mes_anterior, 2)} mês ant.</p>
                        </div>
                        <div className="p-3 bg-slate-900 rounded-lg col-span-2 flex justify-between">
                          <div>
                            <p className="text-xs text-slate-400 mb-1 flex items-center gap-1"><DollarSign className="size-3" /> Custos</p>
                            <p className="text-lg font-bold">{brl(v.total_mes)} <span className="text-xs font-normal text-slate-500">este mês</span></p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-slate-400 mb-1">Mês Anterior</p>
                            <p className="text-lg font-bold text-slate-400">{brl(v.total_mes_anterior)}</p>
                          </div>
                        </div>
                        <div className="col-span-2 text-center text-sm text-slate-400">
                          Preço médio pago este mês: <strong className="text-slate-200">{brl(v.media_preco_mes)}/L</strong>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
