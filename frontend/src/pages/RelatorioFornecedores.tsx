import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DollarSign, Wrench, Trophy, TrendingUp } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function RelatorioFornecedores() {
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");

  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });

  const ranking = useMemo(() => {
    const map = new Map<string, { id: string, nome: string, totalGasto: number, qtdServicos: number }>();
    manutencoes.forEach((m: any) => {
      if (!m.fornecedor_id) return;
      if (dataInicio && m.data < dataInicio) return;
      if (dataFim && m.data > dataFim) return;
      const f = fornecedores.find((x: any) => x.id === m.fornecedor_id);
      if (!f) return;
      if (!map.has(f.id)) map.set(f.id, { id: f.id, nome: f.nome, totalGasto: 0, qtdServicos: 0 });
      const item = map.get(f.id)!;
      item.totalGasto += (m.custo || 0);
      item.qtdServicos += 1;
    });
    return Array.from(map.values()).sort((a, b) => b.totalGasto - a.totalGasto);
  }, [manutencoes, fornecedores, dataInicio, dataFim]);

  return (
    <div>
      <PageHeader eyebrow="Relatórios" title="Performance de Fornecedores" description="Ranking de gastos." />
      <div className="flex gap-3 mb-6">
        <div className="grid gap-1.5"><Label>Início</Label><Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} className="w-40" /></div>
        <div className="grid gap-1.5"><Label>Fim</Label><Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} className="w-40" /></div>
      </div>
      <div className="glass rounded-2xl overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Posição</TableHead><TableHead>Fornecedor</TableHead><TableHead>Serviços</TableHead><TableHead>Total Gasto</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {ranking.map((r, i) => (
              <TableRow key={r.id}>
                <TableCell>{i + 1}º</TableCell>
                <TableCell className="font-medium">{r.nome}</TableCell>
                <TableCell>{r.qtdServicos}</TableCell>
                <TableCell className="text-amber-400 font-bold">{brl(r.totalGasto)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
