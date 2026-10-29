import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertCircle, CheckCircle2, Clock, Info, Pencil, Plus, Trash2, UserCircle, Wrench, FileDown, FileText, Filter } from "lucide-react";
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
  data: hoje, data_inicio: hoje, data_fim: "", previsao_dias: "", autorizado_por: "",
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
      const payload = {
        ...form,
        data: form.data_inicio, // Compatibilidade com backend antigo
        pecas_utilizadas: pecasUsadas,
        ...form,
        custo: Number(form.custo.replace(",", ".")) || 0,
        km_manutencao: form.km_manutencao ? Number(form.km_manutencao) : null,
        proxima_revisao_km: form.proxima_revisao_km ? Number(form.proxima_revisao_km) : null,
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
    onError: (e) => toast.error(errMsg(e)),
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
    setOpen(true);
  };

  const abrirEdicao = (r: Manutencao) => { 
    setEditingId(r.id); 
    setForm({
      veiculo_id: r.veiculo_id, tipo: r.tipo, status: r.status, descricao: r.descricao,
      data: r.data, data_inicio: (r as any).data_inicio || r.data, data_fim: (r as any).data_fim || "", previsao_dias: String((r as any).previsao_dias || ""), autorizado_por: (r as any).autorizado_por || "", custo: String(r.custo), oficina: r.oficina || "", fornecedor_id: (r as any).fornecedor_id || "",
      km_manutencao: r.km_manutencao ? String(r.km_manutencao) : "", proxima_revisao_km: r.proxima_revisao_km ? String(r.proxima_revisao_km) : "",
      pecas_substituidas: r.pecas_substituidas || ""
    });
    setPecasUsadas((r as any).pecas_utilizadas || []);
    setOpen(true); 
  };;

  const exportarExcel = () => {
    const cabecalho = ["Data Início", "Veículo", "Tipo", "Descrição", "Oficina", "Custo", "Status"];
    const linhas = rowsFiltradas.map(r => [
      r.data_inicio || r.data, 
      r.veiculo_label, 
      r.tipo, 
      r.descricao, 
      r.oficina || "", 
      r.custo.toString().replace(".", ","), 
      r.status
    ]);
    const csvContent = "data:text/csv;charset=utf-8,\uFEFF" + [cabecalho.join(";"), ...linhas.map(e => e.join(";"))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `manutencoes_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
  };

  const exportarPDF = () => {
    window.print();
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

  const custoTotal = rowsFiltradas.reduce((s, r) => s + (r.custo || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Manutenções"
        description="Preventivas e corretivas, com custo, oficina e próxima revisão por KM."
        actions={<Button onClick={abrirNovo}><Plus className="size-4" /> Nova manutenção</Button>}
      />

      {/* Cards de Resumo */}
      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-4">
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Total de Manutenções</p>
            <p className="text-2xl font-bold text-slate-100 mt-1">{rowsFiltradas.length}</p>
          </div>
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><Wrench className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Custo Total</p>
            <p className="text-2xl font-bold text-amber-400 mt-1">{brl(custoTotal)}</p>
          </div>
          <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 font-bold">R$</div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Agendadas</p>
            <p className="text-2xl font-bold text-sky-400 mt-1">{rowsFiltradas.filter(r => r.status === 'Agendada').length}</p>
          </div>
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><AlertCircle className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Concluídas</p>
            <p className="text-2xl font-bold text-emerald-400 mt-1">{rowsFiltradas.filter(r => r.status === 'Concluída').length}</p>
          </div>
          <div className="size-10 rounded-lg bg-emerald-500/10 flex items-center justify-center"><CheckCircle2 className="size-5 text-emerald-400" /></div>
        </div>
      </div>

      {/* Filtros */}
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="grid w-64 gap-1.5">
          <Label>Veículo</Label>
          <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} testId="filtro-manutencao-veiculo" />
        </div>
        <div className="grid w-48 gap-1.5">
          <Label>Status</Label>
          <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: TODOS, label: "Todos os status" }, ...STATUS.map(s => ({ value: s, label: s }))]} testId="filtro-manutencao-status" />
        </div>
        {(filtroVeiculo !== TODOS || filtroStatus !== TODOS) && (
          <Button variant="ghost" onClick={() => { setFiltroVeiculo(TODOS); setFiltroStatus(TODOS); }}>Limpar Filtros</Button>
        )}
      </div>

      {/* Tabela */}
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Veículo", "Tipo", "Descrição", "Oficina", "Custo", "Próx. KM", "Status", "Ações"].map((h) => (
                <TableHead key={h} className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-3">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && (
              <TableRow><TableCell colSpan={9} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhuma manutenção encontrada."}</TableCell></TableRow>
            )}
            {rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-mono text-xs whitespace-nowrap px-3">{dataBR(r.data)}</TableCell>
                <TableCell className="font-mono text-xs whitespace-nowrap px-3">{r.veiculo_label?.split(" · ")[0]}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-3">{r.tipo}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-3 max-w-[200px] truncate" title={r.descricao}>{r.descricao}</TableCell>
                <TableCell className="text-xs text-slate-400 px-3 truncate max-w-[120px]">{r.oficina || "—"}</TableCell>
                <TableCell className="tabular-nums text-xs font-medium px-3 text-amber-300">{brl(r.custo)}</TableCell>
                <TableCell className="tabular-nums text-xs px-3 text-sky-300">{r.proxima_revisao_km ? r.proxima_revisao_km.toLocaleString('pt-BR') : "—"}</TableCell>
                <TableCell className="px-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${statusColor(r.status)}`}>
                    {statusIcon(r.status)} {r.status}
                  </span>
                </TableCell>
                <TableCell className="text-center px-3">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Criado por: ${r.criado_por || 'Sistema'}`}>
                      <Info className="size-4 text-slate-400" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)} aria-label="Editar">
                      <Pencil className="size-4 text-sky-400" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)} aria-label="Excluir">
                      <Trash2 className="size-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Dialog de Cadastro/Edição */}
      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center gap-2"><Wrench className="size-5 text-sky-400" /> {editingId ? "Editar" : "Nova"} manutenção</DialogTitle>
              <span className="text-xs text-slate-500 flex items-center gap-1"><UserCircle className="size-3"/> {me?.nome || "Usuário"}</span>
            </div>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 grid gap-1.5">
              <Label>Veículo *</Label>
              <FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="manutencao-form-veiculo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Tipo *</Label>
              <FieldSelect value={form.tipo} onChange={set("tipo")} options={TIPOS.map(t => ({ value: t, label: t }))} testId="manutencao-form-tipo" />
            </div>
            <div className="grid gap-1.5">
              <Label>Status *</Label>
              <FieldSelect value={form.status} onChange={set("status")} options={STATUS.map(s => ({ value: s, label: s }))} testId="manutencao-form-status" />
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
              <Label>Oficina / Prestador</Label>
              <FieldSelect 
                value={form.fornecedor_id} 
                onChange={(v) => {
                  setForm(s => ({ ...s, fornecedor_id: v, oficina: fornecedores.find((f:any)=>f.id===v)?.nome || "" }));
                }} 
                options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} 
                placeholder="Selecione o fornecedor" 
              />
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
                  {pecasUsadas.map((pu, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <FieldSelect 
                        value={pu.peca_id} 
                        onChange={(v) => {
                          const nova = [...pecasUsadas];
                          nova[idx].peca_id = v;
                          const p = listaPecas.find(x => x.id === v);
                          nova[idx].nome = p ? p.nome : "";
                          setPecasUsadas(nova);
                        }} 
                        options={listaPecas.map(p => ({ value: p.id, label: `${p.nome} (Estoque: ${p.quantidade_estoque})` }))} 
                        placeholder="Selecione a peça" 
                      />
                      <Input 
                        type="number" 
                        min="1"
                        value={pu.quantidade} 
                        onChange={(e) => {
                          const nova = [...pecasUsadas];
                          nova[idx].quantidade = e.target.value;
                          setPecasUsadas(nova);
                        }} 
                        className="w-20" 
                      />
                      <Button type="button" variant="ghost" size="icon" className="text-red-400" onClick={() => setPecasUsadas(pecasUsadas.filter((_, i) => i !== idx))}>
                        <Trash2 className="size-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="col-span-2 grid gap-1.5">
              <Label>Peças substituídas (Descrição livre)</Label>
              <textarea value={form.pecas_substituidas} onChange={(e) => set("pecas_substituidas")(e.target.value)} className="flex min-h-[60px] w-full rounded-md border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-100" placeholder="Liste as peças..." />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={salvar.isPending || !form.veiculo_id || !form.descricao}>{editingId ? "Salvar Alterações" : "Registrar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* ConfirmDialog para Exclusão */}
      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir manutenção?"
        description="Esta ação não pode ser desfeita."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="manutencao-excluir"
      />
    </div>
  );
}
