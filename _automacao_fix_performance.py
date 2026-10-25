import os

def fix_backend(raiz):
    # 1. Adicionar datas de contrato no modelo
    model_path = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel, Field
from typing import Optional

class FornecedorCreate(BaseModel):
    tipo_pessoa: str = "PJ"
    nome: str = Field(min_length=2)
    documento: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    atividade: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    avaliacao: Optional[int] = 0
    contrato_inicio: Optional[str] = None
    contrato_fim: Optional[str] = None
    ativo: bool = True

class Fornecedor(FornecedorCreate):
    id: str
''')
    print("✅ Backend: Modelo de Fornecedor atualizado com datas de contrato.")

def criar_tela_performance(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "RelatorioFornecedores.tsx")
    
    codigo = r'''import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, Trophy, DollarSign, Wrench, Calendar, TrendingUp } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl, num } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function RelatorioFornecedores() {
  const [dataInicio, setDataInicio] = useState("");
  const [dataFim, setDataFim] = useState("");

  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });

  // Filtra as manutenções pelo período
  const manutencoesFiltradas = useMemo(() => {
    return manutencoes.filter((m: any) => {
      if (dataInicio && m.data < dataInicio) return false;
      if (dataFim && m.data > dataFim) return false;
      return true;
    });
  }, [manutencoes, dataInicio, dataFim]);

  // Agrupa os dados por fornecedor
  const ranking = useMemo(() => {
    const map = new Map<string, { id: string, nome: string, totalGasto: number, qtdServicos: number }>();
    
    manutencoesFiltradas.forEach((m: any) => {
      if (!m.fornecedor_id) return;
      const f = fornecedores.find((x: any) => x.id === m.fornecedor_id);
      if (!f) return;

      if (!map.has(f.id)) {
        map.set(f.id, { id: f.id, nome: f.nome, totalGasto: 0, qtdServicos: 0 });
      }
      
      const item = map.get(f.id)!;
      item.totalGasto += (m.custo || 0);
      item.qtdServicos += 1;
    });

    return Array.from(map.values()).sort((a, b) => b.totalGasto - a.totalGasto);
  }, [manutencoesFiltradas, fornecedores]);

  const topGasto = ranking.slice(0, 5);
  const topServicos = [...ranking].sort((a, b) => b.qtdServicos - a.qtdServicos).slice(0, 5);
  
  const totalGeral = ranking.reduce((s, r) => s + r.totalGasto, 0);
  const totalServicos = ranking.reduce((s, r) => s + r.qtdServicos, 0);

  const maxGasto = topGasto[0]?.totalGasto || 1;

  return (
    <div>
      <PageHeader eyebrow="Relatórios" title="Performance de Fornecedores" description="Ranking de gastos, volume de serviços e destaques do período." />

      {/* Filtros de Período */}
      <div className="mb-6 flex items-end gap-3 glass p-4 rounded-xl">
        <div className="grid gap-1.5">
          <Label>Data Inicial</Label>
          <Input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} className="w-40" />
        </div>
        <div className="grid gap-1.5">
          <Label>Data Final</Label>
          <Input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} className="w-40" />
        </div>
        {(dataInicio || dataFim) && (
          <button onClick={() => { setDataInicio(""); setDataFim(""); }} className="text-sm text-sky-400 hover:underline pb-2 ml-2">Limpar Filtro</button>
        )}
      </div>

      {/* Cards de Resumo Geral */}
      <div className="mb-6 grid gap-3 sm:grid-cols-2 md:grid-cols-4">
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center"><DollarSign className="size-5 text-amber-400" /></div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Total Gasto</p>
            <p className="text-xl font-bold text-amber-400">{brl(totalGeral)}</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><Wrench className="size-5 text-sky-400" /></div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Total de Serviços</p>
            <p className="text-xl font-bold text-sky-400">{totalServicos}</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="size-10 rounded-lg bg-emerald-500/10 flex items-center justify-center"><Trophy className="size-5 text-emerald-400" /></div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Maior Gasto</p>
            <p className="text-lg font-bold text-emerald-400 truncate max-w-[150px]">{topGasto[0]?.nome || "—"}</p>
          </div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center gap-3">
          <div className="size-10 rounded-lg bg-purple-500/10 flex items-center justify-center"><TrendingUp className="size-5 text-purple-400" /></div>
          <div>
            <p className="text-xs text-slate-500 font-medium">Mais Serviços</p>
            <p className="text-lg font-bold text-purple-400 truncate max-w-[150px]">{topServicos[0]?.nome || "—"}</p>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Ranking de Gasto */}
        <div className="glass rounded-xl p-4">
          <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2"><DollarSign className="size-4 text-amber-400" /> Top 5 - Fornecedores que mais receberam</h3>
          <div className="space-y-3">
            {topGasto.length === 0 && <p className="text-sm text-slate-500">Nenhum dado no período.</p>}
            {topGasto.map((r, i) => {
              const p = Math.min((r.totalGasto / maxGasto) * 100, 100);
              return (
                <div key={r.id} className="flex items-center gap-3">
                  <span className="w-6 text-xs text-slate-500 font-mono text-center">{i + 1}º</span>
                  <div className="flex-1">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium text-slate-300 truncate max-w-[180px]">{r.nome}</span>
                      <span className="font-bold text-amber-300">{brl(r.totalGasto)}</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-amber-600 to-amber-400 rounded-full" style={{ width: `${p}%` }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Ranking de Serviços */}
        <div className="glass rounded-xl p-4">
          <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2"><Wrench className="size-4 text-sky-400" /> Top 5 - Fornecedores com mais serviços</h3>
          <div className="space-y-3">
            {topServicos.length === 0 && <p className="text-sm text-slate-500">Nenhum dado no período.</p>}
            {topServicos.map((r, i) => {
              const maxQtd = topServicos[0]?.qtdServicos || 1;
              const p = Math.min((r.qtdServicos / maxQtd) * 100, 100);
              return (
                <div key={r.id} className="flex items-center gap-3">
                  <span className="w-6 text-xs text-slate-500 font-mono text-center">{i + 1}º</span>
                  <div className="flex-1">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="font-medium text-slate-300 truncate max-w-[180px]">{r.nome}</span>
                      <span className="font-bold text-sky-300">{r.qtdServicos} serv.</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-sky-600 to-sky-400 rounded-full" style={{ width: `${p}%` }} />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Tabela Completa */}
      <div className="mt-6 glass rounded-xl overflow-hidden">
        <div className="p-4 border-b border-slate-800 bg-slate-900/30">
          <h3 className="text-sm font-semibold text-slate-200">Todos os Fornecedores no Período</h3>
        </div>
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs text-slate-500 uppercase">Posição</TableHead>
              <TableHead className="text-xs text-slate-500 uppercase">Fornecedor</TableHead>
              <TableHead className="text-xs text-slate-500 uppercase text-center">Qtd Serviços</TableHead>
              <TableHead className="text-xs text-slate-500 uppercase text-right">Total Gasto</TableHead>
              <TableHead className="text-xs text-slate-500 uppercase text-right">Média por Serviço</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {ranking.map((r, i) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="text-center font-mono text-slate-500">{i + 1}º</TableCell>
                <TableCell className="font-medium text-slate-200">{r.nome}</TableCell>
                <TableCell className="text-center text-sky-300">{r.qtdServicos}</TableCell>
                <TableCell className="text-right font-bold text-amber-300">{brl(r.totalGasto)}</TableCell>
                <TableCell className="text-right text-slate-400">{brl(r.totalGasto / r.qtdServicos)}</TableCell>
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
    print("✅ Tela de Relatório de Fornecedores criada.")

    # Adicionar Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()
    if "RelatorioFornecedores" not in app_content:
        app_content = app_content.replace("import Fornecedores from", "import RelatorioFornecedores from '@/pages/RelatorioFornecedores';\nimport Fornecedores from")
        app_content = app_content.replace('<Route path="cadastros/fornecedores"', '<Route path="relatorios/fornecedores" element={<RelatorioFornecedores />} />\n          <Route path="cadastros/fornecedores"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_content)

    # Adicionar no Sidebar
    sidebar_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        sidebar_content = f.read()
    if "relatorios/fornecedores" not in sidebar_content:
        sidebar_content = sidebar_content.replace('{ label: "Fornecedores", icon: Truck, path: "/cadastros/fornecedores" },', '{ label: "Fornecedores", icon: Truck, path: "/cadastros/fornecedores" },\n        { label: "Performance Forn.", icon: BarChart3, path: "/relatorios/fornecedores" },')
        with open(sidebar_path, 'w', encoding='utf-8') as f:
            f.write(sidebar_content)
    print("✅ Rota e Menu do Relatório de Fornecedores criados.")

def add_contrato_fields(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar campos no estado vazio
    if 'contrato_inicio: "",' not in c:
        c = c.replace('avaliacao: 0, ativo: true', 'avaliacao: 0, contrato_inicio: "", contrato_fim: "", ativo: true')

    # 2. Adicionar campos no abrirEdicao
    if 'contrato_inicio: r.contrato_inicio || "",' not in c:
        c = c.replace('avaliacao: r.avaliacao || 0, ativo: r.ativo', 'avaliacao: r.avaliacao || 0, contrato_inicio: r.contrato_inicio || "", contrato_fim: r.contrato_fim || "", ativo: r.ativo')

    # 3. Adicionar os inputs no formulário (antes do campo de Avaliação)
    if 'Data Início Contrato' not in c:
        c = c.replace(
            '<div className="col-span-2 grid gap-1"><Label className="text-xs">Avaliação</Label>',
            '''<div className="col-span-2 grid grid-cols-2 gap-2 bg-slate-900/30 p-2 rounded border border-slate-800">
              <div className="grid gap-1"><Label className="text-[10px] text-slate-400">Início Contrato</Label><Input type="date" value={form.contrato_inicio || ""} onChange={(e) => setForm(s => ({ ...s, contrato_inicio: e.target.value }))} className="h-8 text-xs" /></div>
              <div className="grid gap-1"><Label className="text-[10px] text-slate-400">Fim Contrato</Label><Input type="date" value={form.contrato_fim || ""} onChange={(e) => setForm(s => ({ ...s, contrato_fim: e.target.value }))} className="h-8 text-xs" /></div>
            </div>

            <div className="col-span-2 grid gap-1"><Label className="text-xs">Avaliação</Label>'''
        )
    
    # 4. Adicionar Alerta de Contrato no Grid
    if 'Alerta de Vencimento' not in c:
        # Adiciona um pequeno alerta visual abaixo do nome no grid
        c = c.replace(
            '<div className="text-slate-500 font-mono text-xs">{r.documento || "—"}</div>',
            '''<div className="text-slate-500 font-mono text-xs">{r.documento || "—"}</div>
                      {r.contrato_fim && new Date(r.contrato_fim) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) && (
                        <div className="text-[9px] font-bold text-red-400 flex items-center gap-1 mt-0.5"><AlertTriangle className="size-3" /> Contrato Vencendo</div>
                      )}'''
        )
        # Importar AlertTriangle
        c = c.replace('import { Truck, Plus', 'import { Truck, Plus, AlertTriangle')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Campos de Contrato e Alerta adicionados.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    criar_tela_performance(raiz)
    add_contrato_fields(raiz)