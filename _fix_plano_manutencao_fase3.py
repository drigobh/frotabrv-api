import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PLANO_FASE3_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = ["frontend/src/pages/Agendamento.tsx"]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def recriar(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Agendamento.tsx")
    
    codigo = '''import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { CalendarClock, Wrench, AlertTriangle, CheckCircle2, Search, Download, Info, Gauge } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function PlanoManutencao() {
  const { data: planos = [] } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: carretas = [] } = useQuery({ queryKey: ["carretas"], queryFn: () => apiGet<any[]>("/carretas") });

  const [filtroNome, setFiltroNome] = useState("");
  const [filtroStatus, setFiltroStatus] = useState("__all__");

  // 1. Calcular o status de cada plano com base nos gatilhos
  const planosCalculados = useMemo(() => {
    return planos.map((p: any) => {
      // Encontra o ativo (cavalo ou carreta)
      let ativo = null;
      if (p.veiculo_id) {
        ativo = veiculos.find((v: any) => v.id === p.veiculo_id);
      } else if (p.carreta_id) {
        ativo = carretas.find((c: any) => c.id === p.carreta_id);
      }

      // Se não encontrou o ativo, pula (dados inconsistentes)
      if (!ativo) return null;

      const kmAtual = ativo.hodometro_km || 0;
      const ultimaExecucaoKm = p.ultima_execucao_km || 0;
      const intervalo = p.intervalo || 1;

      // Cálculo do próximo gatilho (apenas para KM por enquanto)
      let proximoGatilhoKm = 0;
      let faltaKm = 0;
      
      if (p.tipo_gatilho === "km") {
        proximoGatilhoKm = ultimaExecucaoKm + intervalo;
        faltaKm = proximoGatilhoKm - kmAtual;
      }

      // Define o status
      let status = "OK";
      if (p.tipo_gatilho === "km") {
        if (faltaKm < 0) status = "Vencido";
        else if (faltaKm <= 5000) status = "Atenção";
      } else {
        // Para Horas ou Dias, o cálculo seria diferente. 
        // Vamos manter como "OK" (ou implementar depois).
        status = "OK";
      }

      return {
        ...p,
        ativoLabel: p.veiculo_id 
          ? `${ativo.placa} - ${ativo.modelo}` 
          : `${ativo.codigo} - ${ativo.tipo}`,
        kmAtual,
        proximoGatilhoKm,
        faltaKm,
        status
      };
    }).filter(Boolean); // Remove os nulos
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
    return filtered.sort((a: any, b: any) => a.faltaKm - b.faltaKm); // Mais urgentes primeiro
  }, [planosCalculados, filtroNome, filtroStatus]);

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
        description="Controle preditivo baseado nos planos cadastrados por família."
      />

      {/* Cards de KPI Executivos */}
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
        </select>
      </div>

      {/* Tabela de Planos */}
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Ativo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Família</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Descrição</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">KM Atual</TableHead>
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
                  <TableCell className="text-slate-400 font-mono">{p.kmAtual.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell className="text-slate-400 font-mono">{p.proximoGatilhoKm.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell>
                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-bold ${statusColor(p.status)}`}>
                      {statusIcon(p.status)}
                      {p.status === "OK" ? "Em dia" : p.status === "Atenção" ? `Faltam ${p.faltaKm.toLocaleString('pt-BR')} km` : `Atrasado (${Math.abs(p.faltaKm).toLocaleString('pt-BR')} km)`}
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
'''
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Tela de Plano de Manutenção (Fase 3) recriada com integração.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    recriar(raiz)
    print("\n✅ Script aplicado com sucesso!")