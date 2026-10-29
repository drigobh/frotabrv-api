import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { CalendarClock, Wrench, AlertTriangle, CheckCircle2, Search, Download } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function PlanoManutencao() {
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });

  const [filtroNome, setFiltroNome] = useState("");
  const [filtroStatus, setFiltroStatus] = useState("__all__");

  // 1. Calcular as métricas e o status de cada veículo
  const planos = useMemo(() => {
    return manutencoes
      .filter((m: any) => m.proxima_revisao_km)
      .map((m: any) => {
        const v = veiculos.find((x: any) => x.id === m.veiculo_id);
        const kmAtual = v?.hodometro_km || 0;
        const falta = m.proxima_revisao_km - kmAtual;
        
        let status = "OK";
        if (falta < 0) status = "Vencido";
        else if (falta <= 5000) status = "Atenção"; // Alerta preventivo de 5.000 km

        return {
          ...m,
          kmAtual,
          falta,
          status,
          label: m.veiculo_label || "—"
        };
      })
      .sort((a: any, b: any) => a.falta - b.falta); // Mais urgentes primeiro
  }, [manutencoes, veiculos]);

  // 2. KPIs Executivos
  const kpis = useMemo(() => {
    const total = planos.length;
    const vencidos = planos.filter((p: any) => p.status === "Vencido").length;
    const atencao = planos.filter((p: any) => p.status === "Atenção").length;
    const ok = planos.filter((p: any) => p.status === "OK").length;
    return { total, vencidos, atencao, ok };
  }, [planos]);

  // 3. Filtragem
  const planosFiltrados = useMemo(() => {
    let filtered = planos;
    if (filtroNome) filtered = filtered.filter((p: any) => p.label.toLowerCase().includes(filtroNome.toLowerCase()));
    if (filtroStatus !== "__all__") filtered = filtered.filter((p: any) => p.status === filtroStatus);
    return filtered;
  }, [planos, filtroNome, filtroStatus]);

  // 4. Exportação CSV
  const exportar = () => {
    const cabecalho = ["Veículo", "KM Atual", "Próxima Revisão", "KM Faltante", "Status"];
    const linhas = planosFiltrados.map((p: any) => [p.label, p.kmAtual, p.proxima_revisao_km, p.falta, p.status]);
    const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + [cabecalho.join(";"), ...linhas.map((e: any) => e.join(";"))].join("\n");
    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", `plano_manutencao_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
  };

  const statusColor = (status: string) => {
    if (status === "Vencido") return "bg-rose-500/20 text-rose-400 border border-rose-500/30";
    if (status === "Atenção") return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
    return "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
  };

  const statusIcon = (status: string) => {
    if (status === "Vencido") return <AlertTriangle className="size-3" />;
    if (status === "Atenção") return <CalendarClock className="size-3" />;
    return <CheckCircle2 className="size-3" />;
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Plano de Manutenção"
        description="Controle preditivo de revisões preventivas baseadas no Hodômetro."
        actions={
          <Button onClick={exportar} className="bg-sky-600 hover:bg-sky-500 h-9">
            <Download className="size-4 mr-2" /> Exportar Relatório
          </Button>
        }
      />

      {/* Cards de KPI Executivos */}
      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Frota Monitorada</p><p className="text-2xl font-bold text-slate-100">{kpis.total}</p></div>
          <div className="p-2 bg-sky-500/10 rounded-lg"><Wrench className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Em Dia</p><p className="text-2xl font-bold text-emerald-400">{kpis.ok}</p></div>
          <div className="p-2 bg-emerald-500/10 rounded-lg"><CheckCircle2 className="size-5 text-emerald-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Alerta Preventivo</p><p className="text-2xl font-bold text-amber-400">{kpis.atencao}</p></div>
          <div className="p-2 bg-amber-500/10 rounded-lg"><CalendarClock className="size-5 text-amber-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Críticos / Vencidos</p><p className="text-2xl font-bold text-rose-400">{kpis.vencidos}</p></div>
          <div className="p-2 bg-rose-500/10 rounded-lg"><AlertTriangle className="size-5 text-rose-400" /></div>
        </div>
      </div>

      {/* Barra de Filtros */}
      <div className="mb-4 flex gap-2">
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
          <Input placeholder="Buscar veículo..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} className="pl-9 h-9" />
        </div>
        <select value={filtroStatus} onChange={(e) => setFiltroStatus(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
          <option value="__all__">Todos os Status</option>
          <option value="OK">Em Dia</option>
          <option value="Atenção">Alerta Preventivo</option>
          <option value="Vencido">Vencido</option>
        </select>
      </div>

      {/* Grid de Dados */}
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">KM Atual</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Próxima Revisão</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status do Prazo</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {planosFiltrados.length === 0 ? (
              <TableRow><TableCell colSpan={4} className="text-center py-8 text-slate-500">Nenhum plano de manutenção ativo.</TableCell></TableRow>
            ) : (
              planosFiltrados.map((p: any) => (
                <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="text-slate-200 font-medium">{p.label}</TableCell>
                  <TableCell className="text-slate-400">{p.kmAtual.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell className="text-slate-400">{p.proxima_revisao_km.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold ${statusColor(p.status)}`}>
                      {statusIcon(p.status)}
                      {p.status === "OK" ? "Em dia" : p.status === "Atenção" ? `Faltam ${p.falta.toLocaleString('pt-BR')} km` : `Atrasado (${Math.abs(p.falta).toLocaleString('pt-BR')} km)`}
                    </span>
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
