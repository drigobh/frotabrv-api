import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, CheckCircle2, Clock, Info, Pencil, Plus, Trash2, UserCircle, Wrench, FileDown, FileText, Filter, Truck } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { brl, dataBR, errMsg } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { useVeiculos } from "@/hooks/useCadastros";
import { useHoje, useMe } from "@/hooks/useSession";
import type { Manutencao } from "@/types/manutencoes";

const TODOS = "__all__";
const STATUS = ["Agendada", "Em execução", "Concluída"] as const;
const TIPOS = ["Preventiva", "Corretiva"] as const;

const vazio = (hoje: string) => ({
  veiculo_id: "",
  tipo: "Preventiva",
  status: "Agendada",
  descricao: "",
  data: hoje,
  data_inicio: hoje,
  data_fim: "",
  previsao_dias: "",
  autorizado_por: "",
  custo: "",
  oficina: "",
  fornecedor_id: "",
  km_manutencao: "",
  proxima_revisao_km: "",
  pecas_substituidas: "",
  pecas_utilizadas: [],
});

export default function Manutencoes() {
  const qc = useQueryClient();
  const hoje = useHoje();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  
  const [filtroVeiculo, setFiltroVeiculo] = useState(TODOS);
  const [filtroStatus, setFiltroStatus] = useState(TODOS);
  const [filtroData, setFiltroData] = useState("");
  const [filtroFornecedor, setFiltroFornecedor] = useState(TODOS);
  const [filtroPeca, setFiltroPeca] = useState(TODOS);
  
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(() => vazio(""));
  const [pecasUsadas, setPecasUsadas] = useState<{ peca_id: string, quantidade: string, nome: string }[]>([]);
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const fq = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const fornecedores = fq.data ?? [];

  const pecasQ = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas") });
  const listaPecas = pecasQ.data ?? [];

  const q = useQuery({
    queryKey: ["manutencoes"],
    queryFn: () => apiGet<Manutencao[]>("/manutencoes"),
  });

  const rows = q.isError ? [] : (q.data ?? []);

  const rowsFiltradas = useMemo(() => {
    let filtered = rows;
    if (filtroVeiculo !== TODOS) {
      filtered = filtered.filter(r => r.veiculo_id === filtroVeiculo);
    }
    if (filtroStatus !== TODOS) {
      filtered = filtered.filter(r => r.status === filtroStatus);
    }
    if (filtroData) {
      filtered = filtered.filter(r => (r as any).data_inicio?.startsWith(filtroData) || r.data?.startsWith(filtroData));
    }
    if (filtroFornecedor !== TODOS) {
      filtered = filtered.filter(r => (r as any).fornecedor_id === filtroFornecedor);
    }
    if (filtroPeca !== TODOS) {
      filtered = filtered.filter(r => (r as any).pecas_utilizadas?.some((p: any) => p.peca_id === filtroPeca));
    }
    return filtered;
  }, [rows, filtroVeiculo, filtroStatus, filtroData, filtroFornecedor, filtroPeca]);

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["manutencoes"] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const salvar = useMutation({
    mutationFn: () => {
      // Validação de Estoque no Frontend
      for (const pu of pecasUsadas) {
        const p = listaPecas.find((x: any) => x.id === pu.peca_id);
        if (p && Number(pu.quantidade) > (p.quantidade_atual || 0)) {
          throw new Error(`Estoque insuficiente para ${p.nome}. Disponível: ${p.quantidade_atual || 0}, Solicitado: ${pu.quantidade}`);
        }
      }
      const payload = {
        ...form,
        data: form.data_inicio, // Compatibilidade
        pecas_utilizadas: pecasUsadas,
        custo: Number(form.custo.replace(",",".")) || 0,
        km_manutencao: form.km_manutencao ? Number(form.km_manutencao) : null,
        proxima_revisao_km: form.proxima_revisao_km ? Number(form.proxima_revisao_km) : null,
        previsao_dias: form.previsao_dias ? Number(form.previsao_dias) : null,
      };
      if (editingId) return apiPut<Manutencao>(`/manutencoes/${editingId}`, payload);
      return apiPost<Manutencao>("/manutencoes", payload);
    },
    onSuccess: () => {
      toast.success(editingId ? "Manutenção atualizada" : "Manutenção registrada");
      setOpen(false);
      setEditingId(null);
      invalidate();
    },
    onError: (e: any) => toast.error(e.message || errMsg(e)),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/manutencoes/${id}`),
    onSuccess: () => {
      toast.success("Manutenção excluída");
      setExcluirId(null);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const set = (k: keyof ReturnType<typeof vazio>) => (v: string) => setForm((s) => ({ ...s, [k]: v }));

  const handleVeiculoChange = (veiculoId: string) => {
    set("veiculo_id")(veiculoId);
    const v = veiculos.data?.find((x: any) => x.id === veiculoId);
    if (v) {
      setForm(s => ({ ...s, km_manutencao: String(v.hodometro_km || 0) }));
    }
  };
  
  const veicOpts = (veiculos.data ?? []).filter(v => v.ativo).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));

  const abrirNovo = () => {
    setEditingId(null);
    setForm(vazio(hoje));
    setPecasUsadas([]);
    setOpen(true);
  };

  const abrirEdicao = (r: Manutencao) => { 
    setEditingId(r.id); 
    setForm({
      veiculo_id: r.veiculo_id, tipo: r.tipo, status: r.status, descricao: r.descricao,
      data: r.data, data_inicio: (r as any).data_inicio || r.data, data_fim: (r as any).data_fim || "", 
      previsao_dias: String((r as any).previsao_dias || ""), autorizado_por: (r as any).autorizado_por || "",
      custo: String(r.custo), oficina: r.oficina || "", fornecedor_id: (r as any).fornecedor_id || "",
      km_manutencao: r.km_manutencao ? String(r.km_manutencao) : "", proxima_revisao_km: r.proxima_revisao_km ? String(r.proxima_revisao_km) : "",
      pecas_substituidas: r.pecas_substituidas || ""
    });
    setPecasUsadas((r as any).pecas_utilizadas || []);
    setOpen(true); 
  };

  const exportarExcel = () => {
    let filtrosStr = "";
    if (filtroVeiculo !== TODOS) filtrosStr += `Veículo: ${veicOpts.find(v => v.value === filtroVeiculo)?.label} | `;
    if (filtroStatus !== TODOS) filtrosStr += `Status: ${filtroStatus} | `;
    if (filtroData) filtrosStr += `Mês/Data: ${filtroData} | `;
    if (filtroFornecedor !== TODOS) filtrosStr += `Fornecedor: ${fornecedores.find((f:any) => f.id === filtroFornecedor)?.nome} | `;
    if (filtroPeca !== TODOS) filtrosStr += `Peça: ${listaPecas.find((p:any) => p.id === filtroPeca)?.nome} | `;

    let html = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">`;
    html += `<head><meta charset="utf-8"><style>table { border-collapse: collapse; } th, td { border: 1px solid #ccc; padding: 5px; } th { background-color: #f2f2f2; font-weight: bold; }</style></head><body>`;
    html += `<h3>Relatório de Manutenções</h3>`;
    if (filtrosStr) html += `<p><b>Filtros Aplicados:</b> ${filtrosStr}</p>`;
    html += `<table><tr><th>Data Início</th><th>Veículo</th><th>Tipo</th><th>Descrição</th><th>Oficina</th><th>Custo</th><th>Status</th></tr>`;
    
    rowsFiltradas.forEach(r => {
      html += `<tr><td>${dataBR((r as any).data_inicio || r.data)}</td><td>${r.veiculo_label}</td><td>${r.tipo}</td><td>${r.descricao}</td><td>${r.oficina || ""}</td><td>${brl(r.custo)}</td><td>${r.status}</td></tr>`;
    });
    html += `</table></body></html>`;
    
    const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `manutencoes_${new Date().getTime()}.xls`;
    document.body.appendChild(link);
    link.click();
  };
  
  const exportarPDF = () => {
    let filtrosStr = "";
    if (filtroVeiculo !== TODOS) filtrosStr += `<span><b>Veículo:</b> ${veicOpts.find(v => v.value === filtroVeiculo)?.label}</span>`;
    if (filtroStatus !== TODOS) filtrosStr += `<span><b>Status:</b> ${filtroStatus}</span>`;
    if (filtroData) filtrosStr += `<span><b>Mês/Data:</b> ${filtroData}</span>`;
    if (filtroFornecedor !== TODOS) filtrosStr += `<span><b>Fornecedor:</b> ${fornecedores.find((f:any) => f.id === filtroFornecedor)?.nome}</span>`;
    if (filtroPeca !== TODOS) filtrosStr += `<span><b>Peça:</b> ${listaPecas.find((p:any) => p.id === filtroPeca)?.nome}</span>`;

    let html = `<html><head><title>Relatório de Manutenções</title><style>
      body { font-family: Arial, sans-serif; color: #333; margin: 20px; }
      h1 { color: #0284c7; font-size: 24px; border-bottom: 2px solid #0284c7; padding-bottom: 10px; }
      .filters { background: #f8fafc; padding: 10px; border-radius: 5px; margin-bottom: 20px; font-size: 12px; display: flex; gap: 15px; flex-wrap: wrap; }
      table { width: 100%; border-collapse: collapse; font-size: 11px; }
      th { background: #0284c7; color: white; padding: 8px; text-align: left; }
      td { padding: 8px; border-bottom: 1px solid #e2e8f0; }
      tr:nth-child(even) { background: #f8fafc; }
      .footer { margin-top: 20px; font-size: 10px; color: #64748b; text-align: right; }
    </style></head><body>`;
    html += `<h1>Relatório de Manutenções</h1>`;
    html += `<div class="filters">${filtrosStr || "Nenhum filtro aplicado (Todos os registros)"}</div>`;
    html += `<table><thead><tr><th>Data</th><th>Veículo</th><th>Tipo</th><th>Descrição</th><th>Oficina</th><th>Custo</th><th>Status</th></tr></thead><tbody>`;
    
    rowsFiltradas.forEach(r => {
      html += `<tr><td>${dataBR((r as any).data_inicio || r.data)}</td><td>${r.veiculo_label}</td><td>${r.tipo}</td><td>${r.descricao}</td><td>${r.oficina || "-"}</td><td>${brl(r.custo)}</td><td>${r.status}</td></tr>`;
    });
    html += `</tbody></table><div class="footer">Gerado em ${new Date().toLocaleString('pt-BR')}</div></body></html>`;

    const win = window.open('', '_blank');
    if (win) {
      win.document.write(html);
      win.document.close();
      win.focus();
      setTimeout(() => { win.print(); win.close(); }, 500);
    }
  };

  const statusColor = (status: string) => {
    if (status === "Concluída") return "bg-emerald-500/20 text-emerald-400";
    if (status === "Em execução") return "bg-amber-500/20 text-amber-400";
    return "bg-sky-500/20 text-sky-400";
  };

  const statusIcon = (status: string) => {
    if (status === "Concluída") return <CheckCircle2 className="size-3" />;
    if (status === "Em execução") return <Clock className="size-3" />;
    return <AlertCircle className="size-3" />;
  };

  const custoTotal = rowsFiltradas.reduce((s,r) => s + (r.custo || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Manutenções"
        description="Preventivas e corretivas, com custo, oficina e próxima revisão por KM."
        actions={<div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={exportarPDF} className="h-9 border-slate-700 text-slate-300"><FileText className="size-4 mr-1.5" /> PDF</Button>
          <Button variant="outline" size="sm" onClick={exportarExcel} className="h-9 border-emerald-700/50 text-emerald-400 hover:bg-emerald-900/20"><FileDown className="size-4 mr-1.5" /> Excel</Button>
          <Button size="sm" onClick={abrirNovo} className="h-9 bg-sky-600 hover:bg-sky-500 text-white"><Plus className="size-4 mr-1.5" /> Nova manutenção</Button>
        </div>}
      />

      {/* Cards de Resumo */}
      <div className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs text-slate-400">Total de Manutenções</p><p className="text-2xl font-bold text-slate-100">{rowsFiltradas.length}</p></div>
          <div className="p-2 bg-sky-500/10 rounded-lg"><Wrench className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs text-slate-400">Custo Total</p><p className="text-2xl font-bold text-amber-400">{brl(custoTotal)}</p></div>
          <div className="p-2 bg-amber-500/10 rounded-lg"><span className="text-amber-400 font-bold">R$</span></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs text-slate-400">Agendadas</p><p className="text-2xl font-bold text-sky-400">{rowsFiltradas.filter(r => r.status === "Agendada").length}</p></div>
          <div className="p-2 bg-sky-500/10 rounded-lg"><Clock className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl flex justify-between items-center">
          <div><p className="text-xs text-slate-400">Concluídas</p><p className="text-2xl font-bold text-emerald-400">{rowsFiltradas.filter(r => r.status === "Concluída").length}</p></div>
          <div className="p-2 bg-emerald-500/10 rounded-lg"><CheckCircle2 className="size-5 text-emerald-400" /></div>
        </div>
      </div>

      
      {/* Termômetro Top 5 Manutenções */}
      <div className="mb-5 glass rounded-xl p-4">
        <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-2">
          <Wrench className="size-4 text-amber-500" />
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">Top 5 Veículos com Maior Custo de Manutenção</h3>
        </div>
        <div className="space-y-4">
          {Object.values(rowsFiltradas.reduce((acc: any, r: any) => {
            if (!acc[r.veiculo_id]) acc[r.veiculo_id] = { label: r.veiculo_label?.split(" · ")[0] || "—", custo: 0 };
            acc[r.veiculo_id].custo += Number(r.custo) || 0;
            return acc;
          }, {})).sort((a: any, b: any) => b.custo - a.custo).slice(0, 5).map((r: any, i: number) => {
            const maxCusto = Math.max(...Object.values(rowsFiltradas.reduce((acc: any, x: any) => {
              if (!acc[x.veiculo_id]) acc[x.veiculo_id] = { custo: 0 };
              acc[x.veiculo_id].custo += Number(x.custo) || 0;
              return acc;
            }, {})).map((x: any) => x.custo), 1);
            
            const percent = (r.custo / maxCusto) * 100;

            return (
              <div key={i} className="flex items-center gap-3 group" title={`Custo total: ${brl(r.custo)}`}>
                <span className={`text-xs font-bold w-5 text-center flex items-center justify-center ${i === 0 ? 'text-amber-400' : 'text-slate-500'}`}>
                  {i === 0 ? <CheckCircle2 className="size-4 drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]" /> : `${i + 1}º`}
                </span>
                <span className="text-xs font-semibold text-slate-300 w-24 truncate">{r.label}</span>
                
                <div className="flex-1 bg-slate-900/60 rounded-full h-4 border border-slate-700/50 shadow-inner relative flex items-center">
                  {/* Preenchimento */}
                  <div
                    className="h-full rounded-full transition-all duration-1000 ease-out relative z-10 bg-gradient-to-r from-rose-600 to-orange-400 shadow-[0_0_12px_rgba(225,29,72,0.4)]"
                    style={{ width: `${percent}%` }}
                  ></div>

                  {/* Caminhãozinho animado correndo na ponta (Vermelho) */}
                  <div 
                    className="absolute z-30 transition-all duration-1000 ease-out flex items-center justify-center"
                    style={{ left: `calc(${percent}% - 16px)` }}
                  >
                    <Truck className="size-4 text-white drop-shadow-[0_0_6px_rgba(255,255,255,0.8)] animate-pulse" />
                  </div>
                </div>
                
                <span className="text-xs font-bold w-20 text-right tabular-nums text-amber-400">
                  {brl(r.custo)}
                </span>
              </div>
            );
          })}
          {rowsFiltradas.length === 0 && <p className="text-xs text-slate-500 text-center py-2">Sem dados para exibir.</p>}
        </div>
      </div>

      {/* Filtros */}
      <div className="flex flex-wrap gap-3 mb-4 items-end">
        <div className="grid w-48 gap-1.5">
          <Label>Veículo</Label>
          <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} />
        </div>
        <div className="grid w-40 gap-1.5">
          <Label>Status</Label>
          <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: TODOS, label: "Todos os status" }, ...STATUS.map(s => ({ value: s, label: s }))]} />
        </div>
        <div className="grid w-36 gap-1.5">
          <Label>Mês/Data</Label>
          <Input type="month" value={filtroData} onChange={(e) => setFiltroData(e.target.value)} className="h-9" />
        </div>
        <div className="grid w-48 gap-1.5">
          <Label>Fornecedor</Label>
          <FieldSelect value={filtroFornecedor} onChange={setFiltroFornecedor} options={[{ value: TODOS, label: "Todos" }, ...fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))]} />
        </div>
        <div className="grid w-48 gap-1.5">
          <Label>Peça</Label>
          <FieldSelect value={filtroPeca} onChange={setFiltroPeca} options={[{ value: TODOS, label: "Todas" }, ...listaPecas.map((p: any) => ({ value: p.id, label: p.nome }))]} />
        </div>
        <div className="mb-1">
          <Button variant="outline" size="sm" onClick={() => { setFiltroVeiculo(TODOS); setFiltroStatus(TODOS); setFiltroData(""); setFiltroFornecedor(TODOS); setFiltroPeca(TODOS); }} className="h-9 border-red-500/40 text-red-400 hover:bg-red-500/10"><Filter className="size-4 mr-1.5" /> Limpar</Button>
        </div>
      </div>

      {/* Tabela */}
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data Início", "Veículo", "Tipo", "Descrição", "Oficina", "Custo", "Próx. KM", "Previsão", "Status", "Ações"].map((h) => (
                <TableHead key={h} className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-3">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && (
              <TableRow><TableCell colSpan={10} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhuma manutenção encontrada."}</TableCell></TableRow>
            )}
            {rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-mono text-xs whitespace-nowrap px-3">{dataBR((r as any).data_inicio || r.data)}</TableCell>
                <TableCell className="font-mono text-xs whitespace-nowrap px-3">{r.veiculo_label?.split(" · ")[0]}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-3">{r.tipo}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-3 max-w-[200px] truncate" title={r.descricao}>{r.descricao}</TableCell>
                <TableCell className="text-xs text-slate-400 px-3 truncate max-w-[120px]">{r.oficina || "—"}</TableCell>
                <TableCell className="tabular-nums text-xs font-medium px-3 text-amber-300">{brl(r.custo)}</TableCell>
                <TableCell className="tabular-nums text-xs px-3 text-sky-300">{r.proxima_revisao_km ? r.proxima_revisao_km.toLocaleString('pt-BR') : "—"}</TableCell>
                <TableCell className="text-xs px-3">{(r as any).previsao_dias ? `${(r as any).previsao_dias} dias` : "—"}</TableCell>
                <TableCell className="px-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${statusColor(r.status)}`}>
                    {statusIcon(r.status)} {r.status}
                  </span>
                </TableCell>
                <TableCell className="text-center px-3">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Modal */}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Wrench className="size-5 text-sky-400" /> 
              {editingId ? "Editar manutenção" : "Nova manutenção"}
            </DialogTitle>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 grid gap-1.5">
              <Label>Veículo *</Label>
              <FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Tipo *</Label>
              <FieldSelect value={form.tipo} onChange={set("tipo")} options={TIPOS.map(t =>({ value: t, label: t }))} />
            </div>
            <div className="grid gap-1.5">
              <Label>Status *</Label>
              <FieldSelect value={form.status} onChange={set("status")} options={STATUS.map(s => ({ value: s, label: s }))} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Descrição *</Label>
              <Input value={form.descricao} onChange={(e) => set("descricao")(e.target.value)} placeholder="Ex: Troca de óleo" required />
            </div>
            <div className="grid gap-1.5">
              <Label>Data Início *</Label>
              <Input type="date" value={form.data_inicio} onChange={(e) => set("data_inicio")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label>Data Término</Label>
              <Input type="date" value={form.data_fim} onChange={(e) => set("data_fim")(e.target.value)} />
            </div>
            <div className="grid gap-1.5">
              <Label>Previsão (Dias)</Label>
              <Input type="number" value={form.previsao_dias} onChange={(e) => set("previsao_dias")(e.target.value)} placeholder="Ex: 5" />
            </div>
            <div className="grid gap-1.5">
              <Label>Autorizado por</Label>
              <Input value={form.autorizado_por || me?.nome || ""} disabled className="bg-slate-800/50" />
            </div>
            <div className="grid gap-1.5">
              <Label>Custo (R$)</Label>
              <Input inputMode="decimal" value={form.custo} onChange={(e) => set("custo")(e.target.value)} placeholder="0,00" />
            </div>
            <div className="grid gap-1.5">
              <Label>Oficina / Prestador (Digite)</Label>
              <Input
                list="fornecedores-list"
                value={form.oficina}
                onChange={(e) => {
                  const val = e.target.value;
                  const f = fornecedores.find((x: any) => x.nome === val);
                  setForm(s => ({ ...s, oficina: val, fornecedor_id: f ? f.id : "" }));
                }}
                placeholder="Ex: Tonho"
              />
              <datalist id="fornecedores-list">
                {fornecedores.map((f: any) => <option key={f.id} value={f.nome} />)}
              </datalist>
            </div>
            <div className="grid gap-1.5">
              <Label>KM na manutenção</Label>
              <Input type="number" value={form.km_manutencao} onChange={(e) => set("km_manutencao")(e.target.value)} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Próxima revisão (KM) — gera alerta</Label>
              <Input type="number" value={form.proxima_revisao_km} onChange={(e) => set("proxima_revisao_km")(e.target.value)} placeholder="Ex: 350000" />
            </div>
            <div className="col-span-2 border-t border-slate-800 pt-3 mt-1">
              <div className="flex justify-between items-center mb-2">
                <Label className="text-sm font-semibold text-slate-300">Peças Utilizadas (Baixa no Estoque)</Label>
                <Button type="button" variant="outline" size="sm" onClick={() => setPecasUsadas([...pecasUsadas, { peca_id: "", quantidade: "1", nome: "" }])}>
                  <Plus className="size-3 mr-1" /> Adicionar Peça
                </Button>
              </div>
              {pecasUsadas.length === 0 ? (
                <p className="text-xs text-slate-500 italic">Nenhuma peça vinculada a esta manutenção.</p>
              ) : (
                <div className="space-y-2">
                  {pecasUsadas.map((p, i) => (
                    <div key={i} className="flex gap-2 items-center">
                      <FieldSelect 
                        value={p.peca_id} 
                        onChange={(v) => {
                          const pObj = listaPecas.find((x:any) => x.id === v);
                          const arr = [...pecasUsadas];
                          arr[i] = { ...arr[i], peca_id: v, nome: pObj ? pObj.nome : "" };
                          setPecasUsadas(arr);
                        }} 
                        options={listaPecas.map((x: any) => ({ value: x.id, label: `${x.nome} (Estoque: ${x.quantidade_atual || 0})` }))} 
                        placeholder="Selecione a peça" 
                      />
                      <Input 
                        type="number" 
                        className="w-20" 
                        value={p.quantidade} 
                        onChange={(e) => {
                          const arr = [...pecasUsadas];
                          arr[i].quantidade = e.target.value;
                          setPecasUsadas(arr);
                        }} 
                      />
                      <Button type="button" variant="ghost" size="icon" onClick={() => setPecasUsadas(pecasUsadas.filter((_, idx) => idx !== i))}>
                        <Trash2 className="size-4 text-red-400" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="col-span-2 grid gap-1.5 mt-2">
              <Label>Peças substituídas (Descrição livre)</Label>
              <textarea 
                value={form.pecas_substituidas} 
                onChange={(e) => set("pecas_substituidas")(e.target.value)} 
                className="flex min-h-[80px] w-full rounded-md border border-slate-800 bg-slate-950/50 px-3 py-2 text-sm text-slate-200 placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-sky-500"
                placeholder="Liste as peças..." 
              />
            </div>
            <DialogFooter className="col-span-2 mt-4 gap-2">
              <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button type="submit" disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog 
        open={excluirId !== null} 
        onOpenChange={(o) => !o && setExcluirId(null)} 
        title="Remover?" 
        onConfirm={() => excluirId && excluir.mutate(excluirId)} 
        confirmLabel="Remover" 
        destructive 
        pending={excluir.isPending} 
      />
    </div>
  );
}
