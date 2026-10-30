import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell 
} from "recharts";
import { 
  Wrench, Clock, DollarSign, TrendingUp, CheckCircle2, Truck, 
  ShieldAlert, Users, Target, RotateCcw, AlertTriangle, Boxes, 
  Activity, Layers, MapPin, GitCompare
} from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";

const COLORS = ["#10b981", "#f59e0b", "#ef4444", "#0284c7", "#8b5cf6", "#06b6d4", "#ec4899", "#f97316"];

export default function RelatorioManutencao() {
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: abastecimentos = [] } = useQuery({ queryKey: ["abastecimentos"], queryFn: () => apiGet<any[]>("/abastecimentos") });
  const { data: planos = [] } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });
  const { data: empresas = [] } = useQuery({ queryKey: ["empresas"], queryFn: () => apiGet<any[]>("/empresa") });
  const { data: relatorios = {} } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });

  const [abaAtiva, setAbaAtiva] = useState("cpk");
  const [filtroDataInicio, setFiltroDataInicio] = useState("");
  const [filtroDataFim, setFiltroDataFim] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("__all__");
  const [filtroVeiculo, setFiltroVeiculo] = useState("__all__");
  const [filtroEmpresa, setFiltroEmpresa] = useState("__all__");
  const [filtroOficina, setFiltroOficina] = useState("__all__");

  const menuCategorias = [
    {
      titulo: "Indicadores de Custo",
      itens: [
        { id: "cpk", label: "CPK (Custo/KM)", icon: DollarSign },
        { id: "custoVeiculoTipo", label: "Custo por Tipo de Veículo", icon: Truck },
        { id: "centroCusto", label: "Custo por Filial/Base", icon: MapPin },
      ]
    },
    {
      titulo: "Eficiência Operacional",
      itens: [
        { id: "relatorio-ratio", label: "Ratio Preve. x Corret.", icon: TrendingUp },
        { id: "relatorio-faixa-km", label: "Faixa de Hodômetro", icon: Activity },
        { id: "relatorio-desvio-consumo", label: "Desvio de Consumo", icon: GitCompare },
        { id: "relatorio-previsao", label: "Previsão Orçamentária", icon: DollarSign },
        { id: "relatorio-oficina-tempo", label: "Tempo vs. Custo", icon: Clock },
        { id: "relatorio-oleo-atraso", label: "Óleo em Atraso", icon: RotateCcw },
        { id: "mtbf", label: "MTBF (Entre Falhas)", icon: ShieldAlert },
        { id: "mttr", label: "MTTR (Tempo Reparo)", icon: Clock },
        { id: "ociosidade", label: "Ociosidade (Downtime)", icon: AlertTriangle },
        { id: "corretivas", label: "Corretivas Emergenciais", icon: Activity },
        { id: "reincidencia", label: "Reincidência de Falhas", icon: RotateCcw },
      ]
    },
    {
      titulo: "Preventiva e Planejamento",
      itens: [
        { id: "aderencia", label: "Aderência Preventiva", icon: CheckCircle2 },
        { id: "vidaUtil", label: "Vida Útil de Componentes", icon: Layers },
      ]
    },
    {
      titulo: "Consumo e Fornecedores",
      itens: [
        { id: "pecas", label: "Curva ABC de Peças", icon: Boxes },
        { id: "combustivelManut", label: "Consumo vs. Manutenção", icon: TrendingUp },
        { id: "fornecedor", label: "Ranking Fornecedores", icon: Target },
        { id: "benchmarking", label: "Comparativo de Preços", icon: GitCompare },
        { id: "motorista", label: "Custo por Motorista", icon: Users },
      ]
    },
  ];

  // FILTRAGEM GLOBAL
  const manutencoesFiltradas = useMemo(() => {
    let filtered = manutencoes;
    if (filtroDataInicio) filtered = filtered.filter((m: any) => m.data >= filtroDataInicio);
    if (filtroDataFim) filtered = filtered.filter((m: any) => m.data <= filtroDataFim);
    if (filtroTipo !== "__all__") filtered = filtered.filter((m: any) => m.tipo === filtroTipo);
    if (filtroVeiculo !== "__all__") filtered = filtered.filter((m: any) => m.veiculo_id === filtroVeiculo);
    if (filtroOficina !== "__all__") filtered = filtered.filter((m: any) => m.oficina === filtroOficina);
    if (filtroEmpresa !== "__all__") {
      const veiculosEmpresa = veiculos.filter((v: any) => v.empresa_id === filtroEmpresa).map((v: any) => v.id);
      filtered = filtered.filter((m: any) => veiculosEmpresa.includes(m.veiculo_id));
    }
    return filtered;
  }, [manutencoes, filtroDataInicio, filtroDataFim, filtroTipo, filtroVeiculo, filtroEmpresa, filtroOficina, veiculos]);

  const listaOficinas = [...new Set(manutencoes.map((m: any) => m.oficina).filter(Boolean))].sort();

  // 1. CPK
  const cpkData = useMemo(() => {
    const custos: Record<string, { label: string, custo: number, km: number }> = {};
    manutencoesFiltradas.forEach((m: any) => {
      if (m.veiculo_id && m.custo) {
        const v = veiculos.find((x: any) => x.id === m.veiculo_id);
        if (!custos[m.veiculo_id]) custos[m.veiculo_id] = { label: m.veiculo_label, custo: 0, km: v?.hodometro_km || 1 };
        custos[m.veiculo_id].custo += m.custo;
      }
    });
    return Object.values(custos).map(item => ({ ...item, cpk: item.custo / item.km })).sort((a, b) => b.cpk - a.cpk);
  }, [manutencoesFiltradas, veiculos]);

  // 2. MTBF
  const mtbfData = useMemo(() => {
    const falhas: Record<string, number> = {};
    manutencoesFiltradas.filter((m: any) => m.tipo === "Corretiva").forEach((m: any) => {
      falhas[m.veiculo_id] = (falhas[m.veiculo_id] || 0) + 1;
    });
    return Object.entries(falhas).map(([id, count]) => ({ label: veiculos.find((v: any) => v.id === id)?.placa || id, falhas: count })).sort((a, b) => b.falhas - a.falhas);
  }, [manutencoesFiltradas, veiculos]);

  // 3. MTTR
  const mttrData = useMemo(() => {
    const reparos = manutencoesFiltradas.filter((m: any) => m.data_inicio && m.data_fim && m.data_inicio !== m.data_fim);
    let soma = 0;
    reparos.forEach((m: any) => { soma += (new Date(m.data_fim).getTime() - new Date(m.data_inicio).getTime()) / 86400000; });
    return { media: reparos.length > 0 ? soma / reparos.length : 0, total: reparos.length };
  }, [manutencoesFiltradas]);

  // 4. Peças
  const pecasData = useMemo(() => {
    const pecas: Record<string, { qtd: number, custo: number }> = {};
    manutencoesFiltradas.forEach((m: any) => {
      if (m.pecas_substituidas) {
        const peca = m.pecas_substituidas.split(',')[0].trim();
        if (!pecas[peca]) pecas[peca] = { qtd: 0, custo: 0 };
        pecas[peca].qtd += 1;
        pecas[peca].custo += (m.custo || 0) / 2;
      }
    });
    const arr = Object.entries(pecas).map(([nome, dados]) => ({ nome, ...dados })).sort((a, b) => b.custo - a.custo);
    const totalCusto = arr.reduce((acc, item) => acc + item.custo, 0);
    let acumulado = 0;
    return arr.map(item => {
      acumulado += item.custo;
      const perc = (acumulado / totalCusto) * 100;
      let classe = "C";
      if (perc <= 80) classe = "A";
      else if (perc <= 95) classe = "B";
      return { ...item, classe, percAcumulado: perc };
    }).slice(0, 10);
  }, [manutencoesFiltradas]);

  // 5. Aderência
  const aderenciaData = useMemo(() => {
    let ok = 0, atencao = 0, vencido = 0;
    planos.forEach((p: any) => {
      const v = veiculos.find((x: any) => x.id === p.veiculo_id);
      if (!v) return;
      const falta = (p.ultima_execucao_km || 0) + (p.intervalo || 1) - (v.hodometro_km || 0);
      if (falta < 0) vencido++;
      else if (falta <= 5000) atencao++;
      else ok++;
    });
    return [{ name: "Em Dia", value: ok }, { name: "Atenção", value: atencao }, { name: "Vencido", value: vencido }];
  }, [planos, veiculos]);

  // 6. Reincidência
  const reincidenciaData = useMemo(() => {
    const contagem: Record<string, number> = {};
    manutencoesFiltradas.forEach((m: any) => {
      const chave = `${m.veiculo_id}-${m.data?.slice(0, 7)}`;
      contagem[chave] = (contagem[chave] || 0) + 1;
    });
    return Object.entries(contagem).filter(([_, count]) => count > 1).map(([chave, count]) => {
      const [veiculoId, mes] = chave.split("-");
      return { veiculo: veiculos.find((v: any) => v.id === veiculoId)?.placa || veiculoId, mes, quantidade: count };
    });
  }, [manutencoesFiltradas, veiculos]);

  // 7. Custo por Motorista
  const custoMotoristaData = useMemo(() => {
    const custos: Record<string, number> = {};
    manutencoesFiltradas.forEach((m: any) => {
      if (m.veiculo_label && m.custo) {
        const motorista = m.veiculo_label.split(" ")[0];
        custos[motorista] = (custos[motorista] || 0) + m.custo;
      }
    });
    return Object.entries(custos).map(([nome, custo]) => ({ nome, custo })).sort((a, b) => b.custo - a.custo).slice(0, 5);
  }, [manutencoesFiltradas]);

  // 8. Fornecedores
  const fornecedorData = useMemo(() => {
    const custos: Record<string, number> = {};
    manutencoesFiltradas.forEach((m: any) => {
      if (m.oficina && m.custo) custos[m.oficina] = (custos[m.oficina] || 0) + m.custo;
    });
    return Object.entries(custos).map(([nome, custo]) => ({ nome, custo })).sort((a, b) => b.custo - a.custo).slice(0, 5);
  }, [manutencoesFiltradas]);

  // 9. Ociosidade
  const ociosidadeData = useMemo(() => {
    const emExecucao = manutencoesFiltradas.filter((m: any) => m.status === "Em execução");
    return emExecucao.map((m: any) => {
      const dias = m.data_inicio ? Math.floor((Date.now() - new Date(m.data_inicio).getTime()) / 86400000) : 0;
      return { veiculo: m.veiculo_label, dias, data: m.data_inicio };
    }).sort((a, b) => b.dias - a.dias);
  }, [manutencoesFiltradas]);

  // 10. Custo por Tipo
  const custoVeiculoTipoData = useMemo(() => {
    const custos: Record<string, { label: string, custo: number, count: number }> = {};
    manutencoesFiltradas.forEach((m: any) => {
      const v = veiculos.find((x: any) => x.id === m.veiculo_id);
      if (!v || !m.custo) return;
      const tipo = v.tipo_veiculo || "Cavalo";
      if (!custos[tipo]) custos[tipo] = { label: tipo, custo: 0, count: 0 };
      custos[tipo].custo += m.custo;
      custos[tipo].count += 1;
    });
    return Object.values(custos).map(i => ({ ...i, media: i.custo / i.count }));
  }, [manutencoesFiltradas, veiculos]);

  // 11. Centro de Custo
  const centroCustoData = useMemo(() => {
    const custos: Record<string, number> = {};
    manutencoesFiltradas.forEach((m: any) => {
      const v = veiculos.find((x: any) => x.id === m.veiculo_id);
      if (!v || !m.custo) return;
      const emp = empresas.find((e: any) => e.id === v.empresa_id);
      const nome = emp?.nome_fantasia || emp?.razao_social || "Sem Filial";
      custos[nome] = (custos[nome] || 0) + m.custo;
    });
    return Object.entries(custos).map(([nome, custo]) => ({ nome, custo })).sort((a, b) => b.custo - a.custo);
  }, [manutencoesFiltradas, veiculos, empresas]);

  // 12. Corretivas
  const corretivasData = useMemo(() => {
    return manutencoesFiltradas.filter((m: any) => m.tipo === "Corretiva").map((m: any) => ({
      veiculo: m.veiculo_label, descricao: m.descricao, data: m.data, custo: m.custo
    })).sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime()).slice(0, 20);
  }, [manutencoesFiltradas]);

  // 13. Vida Útil
  const vidaUtilData = useMemo(() => {
    const componentes: Record<string, number> = {};
    manutencoesFiltradas.forEach((m: any) => {
      if (m.descricao) {
        const comp = m.descricao.split(" ")[0];
        componentes[comp] = (componentes[comp] || 0) + 1;
      }
    });
    return Object.entries(componentes).map(([nome, qtd]) => ({ nome, qtd })).sort((a, b) => b.qtd - a.qtd).slice(0, 10);
  }, [manutencoesFiltradas]);

  // 14. Consumo vs. Manutenção
  const consumoManutData = useMemo(() => {
    return veiculos.map((v: any) => {
      const manuts = manutencoesFiltradas.filter((m: any) => m.veiculo_id === v.id);
      const abastecimentosVeic = abastecimentos.filter((a: any) => a.veiculo_id === v.id);
      const totalLitros = abastecimentosVeic.reduce((acc: any, a: any) => acc + (a.litros || 0), 0);
      const totalKm = abastecimentosVeic.reduce((acc: any, a: any) => acc + (a.km_rodados || 0), 0);
      const consumoMedio = totalLitros > 0 ? totalKm / totalLitros : 0;
      return { placa: v.placa, consumoMedio, custoManut: manuts.reduce((acc: any, m: any) => acc + (m.custo || 0), 0) };
    }).filter(v => v.consumoMedio > 0 && v.custoManut > 0).sort((a, b) => b.custoManut - a.custo).slice(0, 10);
  }, [veiculos, manutencoesFiltradas, abastecimentos]);

  // 15. Benchmarking
  const benchmarkingData = useMemo(() => {
    const descs: Record<string, { min: number, max: number, media: number, count: number }> = {};
    manutencoesFiltradas.forEach((m: any) => {
      if (m.descricao && m.custo) {
        if (!descs[m.descricao]) descs[m.descricao] = { min: Infinity, max: -Infinity, media: 0, count: 0 };
        descs[m.descricao].min = Math.min(descs[m.descricao].min, m.custo);
        descs[m.descricao].max = Math.max(descs[m.descricao].max, m.custo);
        descs[m.descricao].media = (descs[m.descricao].media * descs[m.descricao].count + m.custo) / (descs[m.descricao].count + 1);
        descs[m.descricao].count += 1;
      }
    });
    return Object.entries(descs).filter(([_, d]) => d.count > 1).map(([nome, d]) => ({ nome, ...d })).sort((a, b) => (b.max - b.min) - (a.max - a.min)).slice(0, 10);
  }, [manutencoesFiltradas]);

  const renderAba = () => {
    switch (abaAtiva) {
      case "cpk": return <AbaComGrafico titulo="Top 10 CPK (Custo por KM)" data={cpkData.slice(0, 10)} dataKey="cpk" xKey="label" cor="#0284c7" formatter={(v: any) => `R$ ${v.toFixed(3)}/km`} colunas={["Veículo", "KM", "Custo", "CPK"]} dados={cpkData.map(i => [i.label, `${i.km.toLocaleString('pt-BR')} km`, brl(i.custo), `R$ ${i.cpk.toFixed(3)}`])} />;
      case "mtbf": return <AbaComGrafico titulo="Veículos com Mais Falhas (MTBF)" data={mtbfData} dataKey="falhas" xKey="label" cor="#ef4444" colunas={["Veículo", "Qtd. Falhas"]} dados={mtbfData.map(i => [i.label, i.falhas])} />;
      case "mttr": return <AbaMTTR data={mttrData} />;
      case "pecas": return <AbaPecas data={pecasData} />;
      case "aderencia": return <AbaPizza titulo="Aderência ao Plano" data={aderenciaData} />;
      case "reincidencia": return <AbaTabela titulo="Reincidência de Falhas (mesmo mês)" colunas={["Veículo", "Mês", "Qtd."]} dados={reincidenciaData.map(i => [i.veiculo, i.mes, i.quantidade])} />;
      case "motorista": return <AbaComGrafico titulo="Custo por Motorista (Top 5)" data={custoMotoristaData} dataKey="custo" xKey="nome" cor="#f59e0b" formatter={(v: any) => brl(v)} colunas={["Motorista", "Custo"]} dados={custoMotoristaData.map(i => [i.nome, brl(i.custo)])} />;
      case "fornecedor": return <AbaComGrafico titulo="Ranking de Fornecedores (Top 5)" data={fornecedorData} dataKey="custo" xKey="nome" cor="#10b981" formatter={(v: any) => brl(v)} colunas={["Fornecedor", "Custo"]} dados={fornecedorData.map(i => [i.nome, brl(i.custo)])} />;
      case "ociosidade": return <AbaTabela titulo="Veículos Parados na Oficina (Ociosidade)" colunas={["Veículo", "Data Início", "Dias Parado"]} dados={ociosidadeData.map(i => [i.veiculo, i.data || "—", `${i.dias} dias`])} />;
      case "custoVeiculoTipo": return <AbaComGrafico titulo="Custo Médio por Tipo de Veículo" data={custoVeiculoTipoData} dataKey="media" xKey="label" cor="#8b5cf6" formatter={(v: any) => brl(v)} colunas={["Tipo", "Qtd. Manutenções", "Custo Médio"]} dados={custoVeiculoTipoData.map(i => [i.label, i.count, brl(i.media)])} />;
      case "centroCusto": return <AbaComGrafico titulo="Custo por Filial/Base" data={centroCustoData} dataKey="custo" xKey="nome" cor="#06b6d4" formatter={(v: any) => brl(v)} colunas={["Filial", "Custo Total"]} dados={centroCustoData.map(i => [i.nome, brl(i.custo)])} />;
      case "corretivas": return <AbaTabela titulo="Manutenções Corretivas Emergenciais" colunas={["Veículo", "Descrição", "Data", "Custo"]} dados={corretivasData.map(i => [i.veiculo, i.descricao, i.data, brl(i.custo || 0)])} />;
      case "vidaUtil": return <AbaComGrafico titulo="Componentes com Mais Trocas (Vida Útil)" data={vidaUtilData} dataKey="qtd" xKey="nome" cor="#ec4899" colunas={["Componente", "Qtd. Trocas"]} dados={vidaUtilData.map(i => [i.nome, i.qtd])} />;
      case "combustivelManut": return <AbaComGrafico titulo="Consumo (km/l) vs Custo Manutenção" data={consumoManutData} dataKey="custoManut" xKey="placa" cor="#f97316" formatter={(v: any) => brl(v)} colunas={["Veículo", "Consumo (km/l)", "Custo Manut."]} dados={consumoManutData.map(i => [i.placa, i.consumoMedio.toFixed(2), brl(i.custoManut)])} />;
      case "benchmarking": return <AbaTabela titulo="Comparativo de Preços (Benchmarking)" colunas={["Serviço", "Mín.", "Máx.", "Média"]} dados={benchmarkingData.map(i => [i.nome, brl(i.min), brl(i.max), brl(i.media)])} />;
      
      // NOVOS RELATÓRIOS
      case "relatorio-ratio": return <RelatorioRatio />;
      case "relatorio-faixa-km": return <RelatorioFaixaKm />;
      case "relatorio-desvio-consumo": return <RelatorioDesvioConsumo />;
      case "relatorio-previsao": return <RelatorioPrevisao />;
      case "relatorio-oficina-tempo": return <RelatorioOficinaTempo />;
      case "relatorio-oleo-atraso": return <RelatorioOleoAtraso />;
      default: return null;
    }
  };

  return (
    <div>
      <PageHeader eyebrow="Gestão" title="Relatórios de Manutenção" description="Painel completo com 22 indicadores estratégicos." />

      {/* Barra de Filtros */}
      <div className="glass p-4 rounded-xl mb-6 flex flex-wrap gap-3 items-end">
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Data Início</Label>
          <Input type="date" value={filtroDataInicio} onChange={(e) => setFiltroDataInicio(e.target.value)} className="h-9 w-36 bg-slate-950" />
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Data Fim</Label>
          <Input type="date" value={filtroDataFim} onChange={(e) => setFiltroDataFim(e.target.value)} className="h-9 w-36 bg-slate-950" />
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Tipo</Label>
          <select value={filtroTipo} onChange={(e) => setFiltroTipo(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-32">
            <option value="__all__">Todos</option>
            <option value="Preventiva">Preventiva</option>
            <option value="Corretiva">Corretiva</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Veículo</Label>
          <select value={filtroVeiculo} onChange={(e) => setFiltroVeiculo(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-44">
            <option value="__all__">Todos os Veículos</option>
            {veiculos.map((v: any) => <option key={v.id} value={v.id}>{v.placa} - {v.modelo}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Filial</Label>
          <select value={filtroEmpresa} onChange={(e) => setFiltroEmpresa(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-40">
            <option value="__all__">Todas</option>
            {empresas.map((e: any) => <option key={e.id} value={e.id}>{e.nome_fantasia || e.razao_social}</option>)}
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <Label className="text-[10px] uppercase text-slate-500">Oficina</Label>
          <select value={filtroOficina} onChange={(e) => setFiltroOficina(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 w-40">
            <option value="__all__">Todas</option>
            {listaOficinas.map((o: any) => <option key={o} value={o}>{o}</option>)}
          </select>
        </div>
        <Button variant="ghost" size="sm" onClick={() => { setFiltroDataInicio(""); setFiltroDataFim(""); setFiltroTipo("__all__"); setFiltroVeiculo("__all__"); setFiltroEmpresa("__all__"); setFiltroOficina("__all__"); }} className="text-xs text-red-400 hover:text-red-300 h-9">
          Limpar
        </Button>
      </div>

      <div className="flex gap-6">
        {/* MENU LATERAL */}
        <div className="w-64 shrink-0 glass rounded-2xl p-3 h-fit sticky top-4">
          {menuCategorias.map(cat => (
            <div key={cat.titulo} className="mb-4">
              <p className="text-[10px] uppercase font-bold text-slate-500 mb-1 px-2">{cat.titulo}</p>
              <div className="space-y-0.5">
                {cat.itens.map(item => {
                  const Icone = item.icon;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setAbaAtiva(item.id)}
                      className={`w-full flex items-center gap-2 px-2 py-2 rounded-lg text-xs font-medium transition-colors ${
                        abaAtiva === item.id ? "bg-sky-600/20 text-sky-400" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                      }`}
                    >
                      <Icone className="size-3.5 shrink-0" /> {item.label}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* CONTEÚDO */}
        <div className="flex-1 min-w-0">
          {renderAba()}
        </div>
      </div>
    </div>
  );
}

// COMPONENTES AUXILIARES
function AbaComGrafico({ titulo, data, dataKey, xKey, cor, formatter, colunas, dados }: any) {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-slate-100 mb-4">{titulo}</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey={xKey} stroke="#94a3b8" tick={{ fontSize: 10 }} />
              <YAxis stroke="#94a3b8" tickFormatter={formatter} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} formatter={formatter} />
              <Bar dataKey={dataKey} fill={cor} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <TabelaDados colunas={colunas} dados={dados} />
    </div>
  );
}

function AbaMTTR({ data }: any) {
  return (
    <div className="glass p-6 rounded-2xl text-center space-y-4">
      <h3 className="text-lg font-bold text-slate-100 mb-2 flex items-center justify-center gap-2"><Clock className="size-5 text-sky-400" /> MTTR (Tempo Médio de Reparo)</h3>
      <p className="text-6xl font-bold text-sky-400">{data.media.toFixed(1)} <span className="text-2xl text-slate-400">dias</span></p>
      <p className="text-sm text-slate-400">Calculado com base em {data.total} manutenções concluídas.</p>
    </div>
  );
}

function AbaPecas({ data }: any) {
  return (
    <div className="space-y-6">
      <div className="glass p-6 rounded-2xl">
        <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><Boxes className="size-5 text-indigo-400" /> Curva ABC de Peças (Top 10 Custos)</h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis type="number" stroke="#94a3b8" tickFormatter={(v: any) => brl(v)} />
              <YAxis dataKey="nome" type="category" width={150} stroke="#94a3b8" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} formatter={(v: any) => brl(v)} />
              <Bar dataKey="custo" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <TabelaDados colunas={["Peça", "Qtd.", "Custo", "Classe"]} dados={data.map((i: any) => [i.nome, i.qtd, brl(i.custo), i.classe])} />
    </div>
  );
}

function AbaPizza({ titulo, data }: any) {
  return (
    <div className="glass p-6 rounded-2xl flex flex-col items-center">
      <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2"><CheckCircle2 className="size-5 text-emerald-400" /> {titulo}</h3>
      <div className="h-72 w-full max-w-md">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5}>
              {data.map((entry: any, index: number) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="flex gap-6 mt-4 text-sm">
        {data.map((item: any, i: number) => (
          <span key={i} className="flex items-center gap-2" style={{ color: COLORS[i] }}><div className="size-3 rounded-full" style={{ backgroundColor: COLORS[i] }} /> {item.name}: {item.value}</span>
        ))}
      </div>
    </div>
  );
}

function AbaTabela({ titulo, colunas, dados, vazio = "Nenhum dado encontrado." }: any) {
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">{titulo}</h3>
      <TabelaDados colunas={colunas} dados={dados} vazio={vazio} />
    </div>
  );
}

function TabelaDados({ colunas, dados, vazio = "Nenhum dado encontrado." }: any) {
  if (dados.length === 0) return <div className="text-center py-6 text-slate-500 text-sm">{vazio}</div>;
  return (
    <div className="overflow-hidden rounded-lg border border-slate-800">
      <Table>
        <TableHeader>
          <TableRow className="border-slate-800 hover:bg-transparent">
            {colunas.map((c: string) => <TableHead key={c} className="text-xs uppercase text-slate-500">{c}</TableHead>)}
          </TableRow>
        </TableHeader>
        <TableBody>
          {dados.map((linha: any[], i: number) => (
            <TableRow key={i} className="border-slate-800 hover:bg-slate-800/30">
              {linha.map((celula: any, j: number) => <TableCell key={j} className="text-slate-300 text-xs">{celula}</TableCell>)}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function RelatorioRatio() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;
  return (
    <div className="glass p-6 rounded-2xl text-center space-y-4">
      <h3 className="text-lg font-bold text-slate-100 mb-2">Ratio Preventiva x Corretiva</h3>
      <div className="flex justify-center gap-12">
        <div><p className="text-5xl font-bold text-emerald-400">{data.ratio.percentual_preventiva.toFixed(1)}%</p><p className="text-sm text-slate-400">Preventivas ({data.ratio.preventivas})</p></div>
        <div><p className="text-5xl font-bold text-rose-400">{data.ratio.percentual_corretiva.toFixed(1)}%</p><p className="text-sm text-slate-400">Corretivas ({data.ratio.corretivas})</p></div>
      </div>
    </div>
  );
}

function RelatorioFaixaKm() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Manutenções por Faixa de Hodômetro</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.faixas_km}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="faixa" stroke="#94a3b8" tick={{ fontSize: 10 }} tickFormatter={(v: any) => Number(v).toLocaleString('pt-BR')} />
            <YAxis stroke="#94a3b8" allowDecimals={false} />
            <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }} />
            <Bar dataKey="quantidade" fill="#0284c7" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function RelatorioDesvioConsumo() {
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const recentes = veiculos.filter((v: any) => manutencoes.some((m: any) => m.veiculo_id === v.id));
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Desvio de Consumo (Pós-Manutenção)</h3>
      <Table><TableHeader><TableRow><TableHead>Veículo</TableHead><TableHead>Status</TableHead></TableRow></TableHeader>
      <TableBody>{recentes.map((v: any) => <TableRow key={v.id}><TableCell>{v.placa} - {v.modelo}</TableCell><TableCell className="text-emerald-400 text-xs">Aguardando Telemetria</TableCell></TableRow>)}</TableBody></Table>
    </div>
  );
}

function RelatorioPrevisao() {
  const { data } = useQuery({ queryKey: ["relatorios-manutencao"], queryFn: () => apiGet<any>("/dashboard/relatorios-manutencao") });
  if (!data) return <div className="glass p-6 text-center text-slate-400">Carregando...</div>;
  return (
    <div className="glass p-6 rounded-2xl text-center space-y-4">
      <h3 className="text-lg font-bold text-slate-100 mb-2">Previsão Orçamentária</h3>
      <div className="flex justify-center gap-12">
        <div><p className="text-3xl font-bold text-slate-100">{brl(data.forecast.media_mensal)}</p><p className="text-xs uppercase text-slate-500">Média Mensal</p></div>
        <div><p className="text-3xl font-bold text-amber-400">{brl(data.forecast.proximos_3_meses)}</p><p className="text-xs uppercase text-slate-500">Próximos 3 Meses</p></div>
        <div><p className="text-3xl font-bold text-rose-400">{brl(data.forecast.proximos_6_meses)}</p><p className="text-xs uppercase text-slate-500">Próximos 6 Meses</p></div>
      </div>
    </div>
  );
}

function RelatorioOficinaTempo() {
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const oficinas: Record<string, { total: number, custo: number }> = {};
  manutencoes.forEach((m: any) => { if (m.oficina && m.custo) { if (!oficinas[m.oficina]) oficinas[m.oficina] = { total: 0, custo: 0 }; oficinas[m.oficina].total += 1; oficinas[m.oficina].custo += m.custo; } });
  const dados = Object.entries(oficinas).map(([nome, d]) => ({ nome, media: d.custo / d.total, total: d.total }));
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Tempo vs. Custo por Oficina</h3>
      <Table><TableHeader><TableRow><TableHead>Oficina</TableHead><TableHead>Qtd.</TableHead><TableHead>Custo Médio</TableHead></TableRow></TableHeader>
      <TableBody>{dados.map((d, i) => <TableRow key={i}><TableCell>{d.nome}</TableCell><TableCell>{d.total}</TableCell><TableCell className="text-amber-400">{brl(d.media)}</TableCell></TableRow>)}</TableBody></Table>
    </div>
  );
}

function RelatorioOleoAtraso() {
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: planos = [] } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });
  const atrasados = veiculos.filter((v: any) => { const plano = planos.find((p: any) => p.veiculo_id === v.id && p.familia === "Lubrificação e Filtros"); if (!plano) return false; return (v.hodometro_km || 0) > ((plano.ultima_execucao_km || 0) + (plano.intervalo || 10000)); });
  return (
    <div className="glass p-6 rounded-2xl">
      <h3 className="text-lg font-bold text-slate-100 mb-4">Veículos com Óleo em Atraso</h3>
      <Table><TableHeader><TableRow><TableHead>Veículo</TableHead><TableHead>KM Atual</TableHead></TableRow></TableHeader>
      <TableBody>{atrasados.map((v: any) => <TableRow key={v.id}><TableCell>{v.placa}</TableCell><TableCell className="text-rose-400">{v.hodometro_km} km</TableCell></TableRow>)}</TableBody></Table>
    </div>
  );
}