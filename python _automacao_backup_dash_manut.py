import os

def fix_backend_dashboard(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "dashboard.py")
    if not os.path.exists(caminho):
        print("❌ Arquivo dashboard.py não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona a busca de manutenções no resumo do dashboard
    if 'custos_manutencao' not in c:
        # Encontra onde ele monta a lista de custos e adiciona a lógica
        codigo_novo = '''
    # Soma os custos de manutenção por mês
    pipeline_manut = [
        {"$group": {"_id": {"$substr": ["$data", 0, 7]}, "total": {"$sum": "$custo"}}}
    ]
    manutencoes = await db.manutencoes.aggregate(pipeline_manut).to_list(None)
    custos_manutencao = {m["_id"]: m["total"] for m in manutencoes if m["_id"]}
'''
        # Injeta antes do retorno final (buscando pelo 'return {')
        c = c.replace('    return {', codigo_novo + '    return {')
        # Adiciona a chave no dicionário de retorno
        c = c.replace('"abastecimentos":', '"custos_manutencao": custos_manutencao,\n        "abastecimentos":')

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota do dashboard agora retorna os custos de manutenção.")
    else:
        print("ℹ️ Rota do dashboard já está atualizada.")

def criar_relatorio_custos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "RelatorioCustosVeiculo.tsx")
    codigo = r'''import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Truck, Fuel, Wrench, TrendingUp, Search } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, dataBR } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { Input } from "@/components/ui/input";

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

  // Histórico combinado ordenado por data
  const historicoCombinado = useMemo(() => {
    const ab = filtroAbast.map((a: any) => ({
      id: a.id, tipo: "combustivel", data: a.data, descricao: `${a.litros}L de ${a.produto || "Diesel"}`, valor: a.valor_total, veiculo: a.veiculo_label?.split(" · ")[0]
    }));
    const ma = filtroManut.map((m: any) => ({
      id: m.id, tipo: "manutencao", data: m.data, descricao: m.descricao, valor: m.custo, veiculo: m.veiculo_label?.split(" · ")[0]
    }));
    return [...ab, ...ma].sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());
  }, [filtroAbast, filtroManut]);

  return (
    <div>
      <PageHeader eyebrow="Relatórios" title="Custos por Veículo" description="Análise detalhada de gastos com combustível e manutenção." />

      <div className="mb-6 w-72">
        <FieldSelect value={veiculoId} onChange={setVeiculoId} options={[{ value: "__all__", label: "Todos os Veículos" }, ...veiculos.map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))]} testId="filtro-veiculo" />
      </div>

      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-sky-500">
          <div className="size-12 rounded-full bg-sky-500/10 flex items-center justify-center"><Fuel className="size-6 text-sky-400" /></div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Gasto com Combustível</p>
            <p className="text-2xl font-bold text-slate-100">{brl(totalAbast)}</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-amber-500">
          <div className="size-12 rounded-full bg-amber-500/10 flex items-center justify-center"><Wrench className="size-6 text-amber-400" /></div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Gasto com Manutenção</p>
            <p className="text-2xl font-bold text-slate-100">{brl(totalManut)}</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-4 border-l-4 border-emerald-500">
          <div className="size-12 rounded-full bg-emerald-500/10 flex items-center justify-center"><TrendingUp className="size-6 text-emerald-400" /></div>
          <div>
            <p className="text-sm text-slate-400 font-medium">Custo Total</p>
            <p className="text-2xl font-bold text-slate-100">{brl(totalGeral)}</p>
          </div>
        </div>
      </div>

      <div className="glass rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-slate-900/30">
          <h3 className="text-sm font-semibold text-slate-200">Histórico de Gastos</h3>
        </div>
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Data</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Descrição</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-right">Valor</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {historicoCombinado.length === 0 && <TableRow><TableCell colSpan={5} className="text-center py-8 text-slate-500">Nenhum gasto registrado para o filtro selecionado.</TableCell></TableRow>}
            {historicoCombinado.slice(0, 50).map((h: any) => (
              <TableRow key={h.id} className="border-slate-800/70">
                <TableCell className="text-xs font-mono text-slate-400">{dataBR(h.data)}</TableCell>
                <TableCell className="text-xs font-mono text-slate-200">{h.veiculo}</TableCell>
                <TableCell>
                  {h.tipo === "combustivel" ? <span className="text-[10px] font-bold bg-sky-500/20 text-sky-400 px-2 py-0.5 rounded">Combustível</span> : <span className="text-[10px] font-bold bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded">Manutenção</span>}
                </TableCell>
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
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Tela de Relatório de Custos por Veículo criada.")

    # Adicionar Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'RelatorioCustosVeiculo' not in c:
        c = c.replace("import RelatorioEstoque from", "import RelatorioCustosVeiculo from '@/pages/RelatorioCustosVeiculo';\nimport RelatorioEstoque from")
        c = c.replace('<Route path="/relatorios/estoque"', '<Route path="/relatorios/custos-veiculo" element={<RelatorioCustosVeiculo />} />\n              <Route path="/relatorios/estoque"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c)

    # Adicionar no Sidebar
    sidebar_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if '/relatorios/custos-veiculo' not in c:
        c = c.replace('{ label: "Relatório de Estoque", icon: Package, path: "/relatorios/estoque" },', '{ label: "Relatório de Estoque", icon: Package, path: "/relatorios/estoque" },\n      { label: "Custos por Veículo", icon: DollarSign, path: "/relatorios/custos-veiculo" },')
        with open(sidebar_path, 'w', encoding='utf-8') as f:
            f.write(c)
    print("✅ Rota e Menu do Relatório de Custos criados.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend_dashboard(raiz)
    criar_relatorio_custos(raiz)