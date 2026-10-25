import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Package, AlertTriangle, TrendingUp, DollarSign, Building2 } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function RelatorioEstoque() {
  // Forçamos o staleTime: 0 para ele sempre buscar do banco ao entrar na tela
  const { data: pecas = [] } = useQuery({ 
    queryKey: ["pecas"], 
    queryFn: () => apiGet<any[]>("/pecas"),
    staleTime: 0,
    refetchOnMount: true
  });
  
  const { data: fornecedores = [] } = useQuery({ 
    queryKey: ["fornecedores"], 
    queryFn: () => apiGet<any[]>("/fornecedores"),
    staleTime: 0,
    refetchOnMount: true
  });

  const analise = useMemo(() => {
    let valorTotal = 0;
    const topPecas: any[] = [];
    const topFornecedoresMap: Record<string, { nome: string, valor: number }> = {};

    pecas.forEach((p: any) => {
      // Matemática Correta: Pega o preço do fornecedor_atual_id
      const fp = (p.fornecedores_precos || []).find((f: any) => f.fornecedor_id === p.fornecedor_atual_id);
      const precoAtual = fp ? fp.preco_atual : 0;
      const valorPeca = precoAtual * p.quantidade_estoque;
      
      valorTotal += valorPeca;
      
      if (valorPeca > 0) {
        topPecas.push({ ...p, precoAtual, valorPeca });
      }

      // Ranking de fornecedores: apenas quem forneceu o estoque atual
      if (p.fornecedor_atual_id && valorPeca > 0) {
        const f = fornecedores.find((x: any) => x.id === p.fornecedor_atual_id);
        if (f) {
          if (!topFornecedoresMap[f.id]) topFornecedoresMap[f.id] = { nome: f.nome, valor: 0 };
          topFornecedoresMap[f.id].valor += valorPeca;
        }
      }
    });

    return {
      valorTotal,
      topPecas: topPecas.sort((a, b) => b.valorPeca - a.valorPeca).slice(0, 5),
      topFornecedores: Object.values(topFornecedoresMap).sort((a, b) => b.valor - a.valor).slice(0, 5),
      criticos: pecas.filter((p: any) => p.quantidade_estoque < p.estoque_minimo).sort((a: any, b: any) => a.quantidade_estoque - b.quantidade_estoque)
    };
  }, [pecas, fornecedores]);

  const maxPeca = analise.topPecas[0]?.valorPeca || 1;
  const maxForn = analise.topFornecedores[0]?.valor || 1;

  return (
    <div>
      <PageHeader eyebrow="Relatórios" title="Inteligência de Estoque" description="Análise de valor imobilizado, fornecedores e reposição." />

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-amber-500">
          <div className="size-12 rounded-full bg-amber-500/10 flex items-center justify-center"><DollarSign className="size-6 text-amber-400" /></div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Valor Total Imobilizado</p>
            <p className="text-2xl font-bold text-slate-100">{brl(analise.valorTotal)}</p>
            <p className="text-[10px] text-slate-500">Calculado pelo preço do fornecedor atual</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-red-500">
          <div className="size-12 rounded-full bg-red-500/10 flex items-center justify-center"><AlertTriangle className="size-6 text-red-400" /></div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Itens Críticos p/ Compra</p>
            <p className="text-2xl font-bold text-slate-100">{analise.criticos.length} itens</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-sky-500">
          <div className="size-12 rounded-full bg-sky-500/10 flex items-center justify-center"><Package className="size-6 text-sky-400" /></div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Total de SKUs (Peças)</p>
            <p className="text-2xl font-bold text-slate-100">{pecas.length}</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2"><TrendingUp className="size-4 text-emerald-400" /> Top 5 - Peças com Maior Valor Imobilizado</h3>
          <div className="space-y-4">
            {analise.topPecas.length === 0 && <p className="text-xs text-slate-500 italic">Nenhum valor calculado (verifique o fornecedor atual das peças).</p>}
            {analise.topPecas.map((p, i) => (
              <div key={p.id}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-300">{i + 1}º {p.nome}</span>
                  <span className="font-bold text-emerald-400">{brl(p.valorPeca)}</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full" style={{ width: `${(p.valorPeca / maxPeca) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass rounded-xl p-5">
          <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2"><Building2 className="size-4 text-sky-400" /> Top 5 - Fornecedores com Maior Valor em Estoque</h3>
          <div className="space-y-4">
            {analise.topFornecedores.length === 0 && <p className="text-xs text-slate-500 italic">Nenhum valor calculado.</p>}
            {analise.topFornecedores.map((f, i) => (
              <div key={i}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-300">{i + 1}º {f.nome}</span>
                  <span className="font-bold text-sky-400">{brl(f.valor)}</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-sky-600 to-sky-400 rounded-full" style={{ width: `${(f.valor / maxForn) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="glass rounded-xl overflow-hidden border border-red-900/30">
        <div className="p-4 border-b border-slate-800 bg-red-950/20">
          <h3 className="text-sm font-bold text-red-400 flex items-center gap-2"><AlertTriangle className="size-4" /> Lista de Reposição Urgente (Abaixo do Mínimo)</h3>
        </div>
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs text-slate-500">Peça</TableHead>
              <TableHead className="text-xs text-slate-500 text-center">Qtd Atual</TableHead>
              <TableHead className="text-xs text-slate-500 text-center">Mínimo Exigido</TableHead>
              <TableHead className="text-xs text-slate-500 text-center">Comprar</TableHead>
              <TableHead className="text-xs text-slate-500">Melhor Fornecedor (Catálogo)</TableHead>
              <TableHead className="text-xs text-slate-500 text-right">Custo Estimado</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {analise.criticos.length === 0 ? (
              <TableRow><TableCell colSpan={6} className="text-center py-6 text-slate-500">Nenhuma peça em nível crítico. Estoque saudável!</TableCell></TableRow>
            ) : (
              analise.criticos.map((p: any) => {
                // Pega o mais barato do catálogo, independente do fornecedor atual
                const validos = (p.fornecedores_precos || []).filter((f:any) => f.fornecedor_id && f.preco_atual > 0);
                const fornecedorBarato = validos.sort((a: any, b: any) => a.preco_atual - b.preco_atual)[0];
                
                const fornNome = fornecedorBarato ? fornecedores.find((f: any) => f.id === fornecedorBarato.fornecedor_id)?.nome : "—";
                const qtdComprar = p.estoque_minimo - p.quantidade_estoque; // Margem de 5
                const custoEstimado = fornecedorBarato && qtdComprar > 0 ? fornecedorBarato.preco_atual * qtdComprar : 0;
                
                return (
                  <TableRow key={p.id} className="border-slate-800/70">
                    <TableCell className="font-medium text-slate-200">{p.nome}</TableCell>
                    <TableCell className="text-center font-bold text-red-400">{p.quantidade_estoque}</TableCell>
                    <TableCell className="text-center text-slate-400">{p.estoque_minimo}</TableCell>
                    <TableCell className="text-center font-bold text-amber-400">{qtdComprar} un</TableCell>
                    <TableCell className="text-xs text-sky-300">{fornNome} {fornecedorBarato && `(${brl(fornecedorBarato.preco_atual)})`}</TableCell>
                    <TableCell className="text-right font-bold text-slate-300">{fornecedorBarato ? brl(custoEstimado) : "—"}</TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
