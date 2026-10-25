import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Package, Search, AlertTriangle, CheckCircle2 } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function RelatorioEstoque() {
  const [busca, setBusca] = useState("");
  const [filtroFornecedor, setFiltroFornecedor] = useState("__all__");
  const [filtroStatus, setFiltroStatus] = useState("__all__");

  const { data: pecas = [] } = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas") });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });

  const filtradas = useMemo(() => {
    return pecas.filter((p: any) => {
      if (busca && !p.nome.toLowerCase().includes(busca.toLowerCase())) return false;
      if (filtroFornecedor !== "__all__" && p.fornecedor_id !== filtroFornecedor) return false;
      
      const baixo = p.quantidade_estoque <= p.estoque_minimo;
      if (filtroStatus === "baixo" && !baixo) return false;
      if (filtroStatus === "ok" && baixo) return false;
      
      return true;
    });
  }, [pecas, busca, filtroFornecedor, filtroStatus]);

  return (
    <div>
      <PageHeader eyebrow="Relatórios" title="Relatório de Estoque" description="Análise detalhada de peças, fornecedores e status." />

      <div className="mb-6 flex flex-wrap gap-3 glass p-4 rounded-xl items-end">
        <div className="w-64">
          <Label>Buscar Peça</Label>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 size-4 text-slate-500" />
            <Input placeholder="Nome da peça..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-8" />
          </div>
        </div>
        <div className="w-56">
          <Label>Fornecedor</Label>
          <FieldSelect value={filtroFornecedor} onChange={setFiltroFornecedor} options={[{ value: "__all__", label: "Todos os Fornecedores" }, ...fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))]} testId="filtro-relatorio-fornecedor" />
        </div>
        <div className="w-48">
          <Label>Status</Label>
          <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: "__all__", label: "Todos" }, { value: "ok", label: "Estoque OK" }, { value: "baixo", label: "Estoque Baixo" }]} testId="filtro-relatorio-status" />
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Peça</TableHead>
              <TableHead>Fornecedor</TableHead>
              <TableHead className="text-center">Qtd. Atual</TableHead>
              <TableHead className="text-center">Qtd. Mín.</TableHead>
              <TableHead className="text-right">Preço Custo</TableHead>
              <TableHead className="text-right">Total em Estoque</TableHead>
              <TableHead className="text-center">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtradas.map((r: any) => {
              const baixo = r.quantidade_estoque <= r.estoque_minimo;
              const forn = fornecedores.find((f: any) => f.id === r.fornecedor_id);
              return (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">
                    {r.nome}
                    <div className="text-xs text-slate-500 font-mono">{r.codigo || "—"}</div>
                  </TableCell>
                  <TableCell className="text-slate-400 text-xs">{forn ? `${forn.nome} ${forn.estado ? `(${forn.estado})` : ''}` : "—"}</TableCell>
                  <TableCell className="text-center font-bold">{r.quantidade_estoque}</TableCell>
                  <TableCell className="text-center">{r.estoque_minimo}</TableCell>
                  <TableCell className="text-right">{brl(r.preco_custo)}</TableCell>
                  <TableCell className="text-right font-bold text-amber-400">{brl(r.preco_custo * r.quantidade_estoque)}</TableCell>
                  <TableCell className="text-center">
                    {baixo ? <span className="text-[10px] font-bold bg-red-500/20 text-red-400 px-2 py-0.5 rounded inline-flex gap-1 items-center"><AlertTriangle className="size-3"/> Baixo</span> : <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded inline-flex gap-1 items-center"><CheckCircle2 className="size-3"/> OK</span>}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
