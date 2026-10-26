import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Fuel, Wrench, TrendingUp } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, dataBR } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function RelatorioCustosVeiculo() {
  const [veiculoId, setVeiculoId] = useState("__all__");

  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: abastecimentos = [] } = useQuery({ queryKey: ["abastecimentos"], queryFn: () => apiGet<any[]>("/abastecimentos") });
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });

  const filtroAbast = useMemo(() => veiculoId === "__all__" ? abastecimentos : abastecimentos.filter(a => a.veiculo_id === veiculoId), [abastecimentos, veiculoId]);
  const filtroManut = useMemo(() => veiculoId === "__all__" ? manutencoes : manutencoes.filter(m => m.veiculo_id === veiculoId), [manutencoes, veiculoId]);

  const totalAbast = filtroAbast.reduce((s, a) => s + (a.valor_total || 0), 0);
  const totalManut = filtroManut.reduce((s, m) => s + (m.custo || 0), 0);
  const totalGeral = totalAbast + totalManut;

  const historicoCombinado = useMemo(() => {
    const ab = filtroAbast.map((a: any) => ({
      id: a.id, tipo: "combustivel", data: a.data, descricao: a.litros + "L de " + (a.produto || "Diesel"), valor: a.valor_total, veiculo: a.veiculo_label?.split(" \u00b7 ")[0]
    }));
    const ma = filtroManut.map((m: any) => ({
      id: m.id, tipo: "manutencao", data: m.data, descricao: m.descricao, valor: m.custo, veiculo: m.veiculo_label?.split(" \u00b7 ")[0]
    }));
    return [...ab, ...ma].sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
  }, [filtroAbast, filtroManut]);

  return (
    <div>
      <PageHeader eyebrow="Relatorios" title="Custos por Veiculo" description="Analise detalhada de gastos com combustivel e manutencao." />
      <div className="mb-6 w-72">
        <FieldSelect value={veiculoId} onChange={setVeiculoId} options={[{ value: "__all__", label: "Todos os Veiculos" }, ...veiculos.map((v: any) => ({ value: v.id, label: v.placa + " - " + v.modelo }))]} testId="filtro-veiculo" />
      </div>
      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-sky-500">
          <div className="size-12 rounded-full bg-sky-500/10 flex items-center justify-center"><Fuel className="size-6 text-sky-400" /></div>
          <div><p className="text-sm text-slate-400 font-medium">Combustivel</p><p className="text-2xl font-bold text-slate-100">{brl(totalAbast)}</p></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-amber-500">
          <div className="size-12 rounded-full bg-amber-500/10 flex items-center justify-center"><Wrench className="size-6 text-amber-400" /></div>
          <div><p className="text-sm text-slate-400 font-medium">Manutencao</p><p className="text-2xl font-bold text-slate-100">{brl(totalManut)}</p></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-emerald-500">
          <div className="size-12 rounded-full bg-emerald-500/10 flex items-center justify-center"><TrendingUp className="size-6 text-emerald-400" /></div>
          <div><p className="text-sm text-slate-400 font-medium">Total</p><p className="text-2xl font-bold text-slate-100">{brl(totalGeral)}</p></div>
        </div>
      </div>
      <div className="glass rounded-xl overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow><TableHead>Data</TableHead><TableHead>Veiculo</TableHead><TableHead>Tipo</TableHead><TableHead>Descricao</TableHead><TableHead className="text-right">Valor</TableHead></TableRow>
          </TableHeader>
          <TableBody>
            {historicoCombinado.length === 0 && <TableRow><TableCell colSpan={5} className="text-center py-8 text-slate-500">Nenhum gasto registrado.</TableCell></TableRow>}
            {historicoCombinado.slice(0, 50).map((h: any) => (
              <TableRow key={h.id}>
                <TableCell className="text-xs font-mono text-slate-400">{dataBR(h.data)}</TableCell>
                <TableCell className="text-xs font-mono text-slate-200">{h.veiculo}</TableCell>
                <TableCell>{h.tipo === "combustivel" ? <span className="text-[10px] bg-sky-500/20 text-sky-400 px-2 py-0.5 rounded font-bold">Combustivel</span> : <span className="text-[10px] bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded font-bold">Manutencao</span>}</TableCell>
                <TableCell className="text-xs text-slate-300">{h.descricao}</TableCell>
                <TableCell className="text-right font-medium text-slate-100">{brl(h.valor)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
