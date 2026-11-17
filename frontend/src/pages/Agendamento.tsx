import { useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { CalendarClock, Wrench, AlertTriangle, CheckCircle2, Search, X, Gauge, Info, User } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const DIA_MS = 86400000;

function dataISO(valor: string) {
  const dia = valor?.match(/^\d{4}-\d{2}-\d{2}/)?.[0];
  return dia ? new Date(dia + "T00:00:00Z") : new Date(NaN);
}

function proximaData(base: string, intervalo: number, unidade: string) {
  const data = dataISO(base);
  if (!Number.isFinite(data.getTime()) || !Number.isInteger(intervalo) || intervalo <= 0) return null;
  if (unidade === "dias" || !unidade) {
    data.setUTCDate(data.getUTCDate() + intervalo);
  } else if (unidade === "meses" || unidade === "anos") {
    const dia = data.getUTCDate();
    data.setUTCDate(1);
    data.setUTCMonth(data.getUTCMonth() + intervalo * (unidade === "anos" ? 12 : 1));
    const ultimo = new Date(data.getTime());
    ultimo.setUTCMonth(ultimo.getUTCMonth() + 1, 0);
    data.setUTCDate(Math.min(dia, ultimo.getUTCDate()));
  } else return null;
  return Number.isFinite(data.getTime()) ? data : null;
}

export default function PlanoManutencao() {
  const { data: planos = [] } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: carretas = [] } = useQuery({ queryKey: ["carretas"], queryFn: () => apiGet<any[]>("/carretas") });

  const [filtroNome, setFiltroNome] = useState("");
  const [filtroStatus, setFiltroStatus] = useState("__all__");
  const [veiculoFocado, setVeiculoFocado] = useState<any>(null);

  // 1. Calcular o status de cada plano com base nos gatilhos
  const planosCalculados = useMemo(() => {
    const hoje = dataISO(new Date().toLocaleDateString("sv-SE", { timeZone: "America/Sao_Paulo" }));
    return planos.filter((p: any) => p.ativo !== false).map((p: any) => {
      let ativo = null;
      if (p.veiculo_id) {
        ativo = veiculos.find((v: any) => v.id === p.veiculo_id);
      } else if (p.carreta_id) {
        ativo = carretas.find((c: any) => c.id === p.carreta_id);
      }

      if (!ativo) return null;

      const kmAtual = ativo.hodometro_km;
      const ultimaExecucaoKm = p.ultima_execucao_km;
      const intervalo = p.intervalo;
      const vitalicioExecutado = p.tipo_recorrencia === "vitalicio" &&
        Boolean(p.ultima_execucao_data || (p.tipo_gatilho === "km" && p.ultima_execucao_km != null) || (p.tipo_gatilho === "horas" && p.ultima_execucao_horas != null));

      let falta = 0;
      let limiteAtencao = 0;
      let gatilho = "—";
      let unidade = "";
      const intervaloValido = Number.isFinite(intervalo) && intervalo > 0;
      if (!vitalicioExecutado && p.tipo_gatilho === "km" && intervaloValido &&
          Number.isFinite(kmAtual) && Number.isFinite(ultimaExecucaoKm)) {
        const proximoKm = ultimaExecucaoKm + intervalo;
        falta = proximoKm - kmAtual;
        limiteAtencao = 5000;
        gatilho = proximoKm.toLocaleString("pt-BR") + " km";
        unidade = "km";
      } else if (!vitalicioExecutado && p.tipo_gatilho === "horas" && intervaloValido &&
          Number.isFinite(p.horimetro_atual) && Number.isFinite(p.ultima_execucao_horas)) {
        const proximaHora = p.ultima_execucao_horas + intervalo;
        falta = proximaHora - p.horimetro_atual;
        limiteAtencao = intervalo * 0.1;
        gatilho = proximaHora.toLocaleString("pt-BR") + " h";
        unidade = "h";
      } else if (!vitalicioExecutado && p.tipo_gatilho === "dias") {
        const proxima = proximaData(p.ultima_execucao_data || p.data_abertura, intervalo, p.unidade_tempo);
        if (proxima) {
          falta = (proxima.getTime() - hoje.getTime()) / DIA_MS;
          limiteAtencao = 30;
          gatilho = proxima.toLocaleDateString("pt-BR", { timeZone: "UTC" });
          unidade = "dias";
        }
      }
      const status = vitalicioExecutado ? "Executado" : !unidade ? "Sem cálculo"
        : falta < 0 ? "Vencido" : falta <= limiteAtencao ? "Atenção" : "OK";

      return {
        ...p,
        ativoLabel: p.veiculo_id 
          ? `${ativo.placa} - ${ativo.modelo}` 
          : `${ativo.codigo} - ${ativo.tipo}`,
        leituraAtual: p.tipo_gatilho === "horas" && Number.isFinite(p.horimetro_atual)
          ? p.horimetro_atual.toLocaleString("pt-BR") + " h"
          : p.tipo_gatilho === "km" && Number.isFinite(kmAtual) ? kmAtual.toLocaleString("pt-BR") + " km" : "—",
        gatilho,
        falta,
        unidade,
        status
      };
    }).filter(Boolean);
  }, [planos, veiculos, carretas]);

  // 2. KPIs
  const kpis = useMemo(() => {
    const total = planosCalculados.length;
    const vencidos = planosCalculados.filter((p: any) => p.status === "Vencido").length;
    const atencao = planosCalculados.filter((p: any) => p.status === "Atenção").length;
    const ok = planosCalculados.filter((p: any) => p.status === "OK").length;
    return { total, vencidos, atencao, ok };
  }, [planosCalculados]);

  // 3. Filtragem
  const planosFiltrados = useMemo(() => {
    let filtered = planosCalculados;
    if (filtroNome) {
      filtered = filtered.filter((p: any) => p.ativoLabel.toLowerCase().includes(filtroNome.toLowerCase()));
    }
    if (filtroStatus !== "__all__") {
      filtered = filtered.filter((p: any) => p.status === filtroStatus);
    }
    const prioridade: Record<string, number> = { Vencido: 0, Atenção: 1, OK: 2, "Sem cálculo": 3, Executado: 4 };
    return [...filtered].sort((a: any, b: any) =>
      prioridade[a.status] - prioridade[b.status] ||
      String(a.unidade).localeCompare(b.unidade) || a.falta - b.falta
    );
  }, [planosCalculados, filtroNome, filtroStatus]);

  const statusColor = (status: string) => {
    if (status === "Vencido") return "bg-rose-500/20 text-rose-400 border border-rose-500/30";
    if (status === "Atenção") return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
    if (status === "Sem cálculo") return "bg-slate-800 text-slate-300";
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
        title="Agendamento Preventivo"
        description="Acompanhe os vencimentos dos planos de manutenção."
        actions={<>
          <Button variant="outline" render={<Link to="/cadastros/planos-manutencao" />}>Gerenciar planos</Button>
          <Button render={<Link to="/cadastros/planos-manutencao?novo=1" />}>Novo plano</Button>
        </>}
      />

      {/* Cards de KPI */}
      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs uppercase text-slate-400">Planos Ativos</p><p className="text-2xl font-bold text-slate-100">{kpis.total}</p></div>
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

      {/* Filtros */}
      <div className="mb-4 flex gap-2">
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
          <Input placeholder="Buscar veículo/carreta..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} className="pl-9 h-9" />
        </div>
        <select value={filtroStatus} onChange={(e) => setFiltroStatus(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
          <option value="__all__">Todos os Status</option>
          <option value="OK">Em Dia</option>
          <option value="Atenção">Alerta Preventivo</option>
          <option value="Vencido">Vencido</option>
          <option value="Executado">Executado</option>
          <option value="Sem cálculo">Sem cálculo</option>
        </select>
      </div>

      {/* Tabela */}
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Ativo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Família</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Descrição</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Leitura atual</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Próx. Gatilho</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {planosFiltrados.length === 0 ? (
              <TableRow><TableCell colSpan={6} className="text-center py-8 text-slate-500">Nenhum plano ativo encontrado.</TableCell></TableRow>
            ) : (
              planosFiltrados.map((p: any) => (
                <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="font-medium text-slate-200">{p.ativoLabel}</TableCell>
                  <TableCell className="text-xs text-slate-400">{p.familia}</TableCell>
                  <TableCell className="text-xs text-slate-400">{p.descricao}</TableCell>
                  <TableCell className="text-slate-400 font-mono">{p.leituraAtual}</TableCell>
                  <TableCell className="text-slate-400 font-mono">{p.gatilho}</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold ${statusColor(p.status)}`}>
                      {statusIcon(p.status)}
                      {p.status === "OK" ? "Em dia" : p.status === "Atenção" ? `Faltam ${p.falta.toLocaleString("pt-BR")} ${p.unidade}` : p.status === "Vencido" ? `Atrasado (${Math.abs(p.falta).toLocaleString("pt-BR")} ${p.unidade})` : p.status}
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
