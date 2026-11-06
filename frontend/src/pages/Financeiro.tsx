import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, X, Check, CheckCircle2, Truck, Building2, FileText, Calendar, Filter, FileSearch, Eye, Edit, Trash2, RotateCcw, Printer } from "lucide-react";
import { apiGet, apiPost, apiPut, apiPatch, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const CATEGORIAS_FALLBACK = ["Combustível", "Manutenção", "Pneus", "Pedágio", "Seguro", "Frete", "Multa", "Outros"];
const MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];

export default function Financeiro() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<"Todos" | "Pagar" | "Receber" | "Conciliacao">("Todos");
  const [busca, setBusca] = useState("");
  const [mesFiltro, setMesFiltro] = useState(0);
  const [anoFiltro, setAnoFiltro] = useState(new Date().getFullYear());
  
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<any>(null);
  const [buscaFornecedor, setBuscaFornecedor] = useState("");
  const [mostrarSugestoesFornecedor, setMostrarSugestoesFornecedor] = useState(false);
  
  const [modalHistoricoOpen, setModalHistoricoOpen] = useState(false);
  const [modalNotaOpen, setModalNotaOpen] = useState(false);
  const [notaAtual, setNotaAtual] = useState<any>(null);
  const [contaHistorico, setContaHistorico] = useState<any>(null);
  const [form, setForm] = useState<any>({
    tipo: "Pagar", descricao: "", categoria: "Outros", valor: "", vencimento: "", status: "Pendente", 
    fornecedor_id: "", veiculo_id: "", documento_vinculo: "", observacoes: ""
  });

  // Queries
  const { data: contas = [], isLoading } = useQuery({ 
    queryKey: ["contas", abaAtiva, mesFiltro, anoFiltro], 
    queryFn: () => apiGet<any[]>(`/financeiro/contas?mes=${mesFiltro}&ano=${anoFiltro}${abaAtiva !== "Todos" && abaAtiva !== "Conciliacao" ? `&tipo=${abaAtiva}` : ""}`) 
  });
  const { data: resumo = { a_pagar: 0, a_receber: 0, vencido: 0, total_pago: 0, saldo: 0 } } = useQuery({ 
    queryKey: ["resumo-financeiro", mesFiltro, anoFiltro], 
    queryFn: () => apiGet<any>(`/financeiro/resumo?mes=${mesFiltro}&ano=${anoFiltro}`) 
  });
  const { data: conciliacao } = useQuery({ 
    queryKey: ["conciliacao", mesFiltro, anoFiltro], 
    queryFn: () => apiGet<any>(`/financeiro/conciliacao?mes=${mesFiltro}&ano=${anoFiltro}`),
    enabled: abaAtiva === "Conciliacao"
  });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });

  // Mutations
  const salvar = useMutation({
    mutationFn: (payload: any) => editando ? apiPut(`/financeiro/contas/${editando.id}`, payload) : apiPost("/financeiro/contas", payload),
    onSuccess: () => {
      toast.success(editando ? "Conta atualizada!" : "Conta registrada!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["contas"] });
      qc.invalidateQueries({ queryKey: ["resumo-financeiro"] });
      qc.invalidateQueries({ queryKey: ["conciliacao"] });
    }
  });

  const marcarPago = useMutation({
    mutationFn: (id: string) => apiPatch(`/financeiro/contas/${id}/pagar`, {}),
    onSuccess: () => {
      toast.success("Conta quitada!");
      qc.invalidateQueries({ queryKey: ["contas"] });
      qc.invalidateQueries({ queryKey: ["resumo-financeiro"] });
      qc.invalidateQueries({ queryKey: ["conciliacao"] });
    }
  });

  const estornar = useMutation({
    mutationFn: (id: string) => apiPatch(`/financeiro/contas/${id}/estornar`, {}),
    onSuccess: () => {
      toast.success("Conta estornada com sucesso!");
      setModalHistoricoOpen(false);
      qc.invalidateQueries({ queryKey: ["contas"] });
      qc.invalidateQueries({ queryKey: ["resumo-financeiro"] });
    }
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/financeiro/contas/${id}`),
    onSuccess: () => {
      toast.success("Conta excluída com sucesso!");
      qc.invalidateQueries({ queryKey: ["contas"] });
      qc.invalidateQueries({ queryKey: ["resumo-financeiro"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao excluir")
  });

  const abrirNovo = () => {
    setEditando(null);
    setForm({ tipo: "Pagar", descricao: "", categoria: "Outros", valor: "", vencimento: "", status: "Pendente", fornecedor_id: "", veiculo_id: "", documento_vinculo: "", observacoes: "" });
    setBuscaFornecedor("");
    setModalOpen(true);
  };

  const abrirEdicao = (c: any) => {
    setEditando(c);
    setForm({ ...c, valor: String(c.valor) });
    setBuscaFornecedor(fornecedores.find((f: any) => f.id === c.fornecedor_id)?.nome || "");
    setModalOpen(true);
  };

  const filtrados = contas.filter((c: any) =>
    (c.descricao || "").toLowerCase().includes(busca.toLowerCase()) ||
    (c.documento_vinculo || "").toLowerCase().includes(busca.toLowerCase())
  );

  const fornecedoresFiltrados = fornecedores.filter((f: any) =>
    (f.nome || "").toLowerCase().includes(buscaFornecedor.toLowerCase()) ||
    (f.documento || "").toLowerCase().includes(buscaFornecedor.toLowerCase())
  );

  const getFornecedorNome = (id: string) => fornecedores.find((f: any) => f.id === id)?.nome || "—";
  const getVeiculoPlaca = (id: string) => veiculos.find((v: any) => v.id === id)?.placa || "—";

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Financeiro"
        description="Controle suas contas a pagar, a receber e o fluxo de caixa."
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder="Buscar conta..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-9 h-9 w-64" />
            </div>
            <Button onClick={() => navigate("/financeiro/xml")} variant="outline" className="border-purple-500/40 text-purple-400 hover:bg-purple-500/10 h-9 mr-2"><FileSearch className="size-4 mr-2" /> Visualizar XML</Button>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">
              <Plus className="size-4 mr-2" /> Nova Conta
            </Button>
          </div>
        }
      />

      {/* Filtro de Mês/Ano */}
      <div className="flex flex-wrap items-center gap-3 mb-6 bg-slate-900/50 border border-slate-800 p-3 rounded-xl">
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <Filter className="size-4" /> Filtrar Período:
        </div>
        <select value={mesFiltro} onChange={(e) => setMesFiltro(Number(e.target.value))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
          <option value={0}>Todos os Meses</option>
          {MESES.map((m, i) => <option key={m} value={i+1}>{m}</option>)}
        </select>
        <select value={anoFiltro} onChange={(e) => setAnoFiltro(Number(e.target.value))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
          {[2024, 2025, 2026, 2027].map(a => <option key={a} value={a}>{a}</option>)}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="glass p-4 rounded-xl border border-rose-500/30">
          <p className="text-[11px] uppercase tracking-widest text-rose-400">A Pagar</p>
          <p className="text-2xl font-bold text-rose-400 mt-1">{brl(Number(resumo?.a_pagar) || 0)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-emerald-500/30">
          <p className="text-[11px] uppercase tracking-widest text-emerald-400">A Receber</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">{brl(Number(resumo?.a_receber) || 0)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-amber-500/30">
          <p className="text-[11px] uppercase tracking-widest text-amber-400">Saldo Projetado</p>
          <p className={cn("text-2xl font-bold mt-1", resumo.saldo >= 0 ? "text-emerald-400" : "text-rose-400")}>{brl(Number(resumo?.saldo) || 0)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Vencidas</p>
          <p className="text-2xl font-bold text-slate-300 mt-1">{brl(Number(resumo?.vencido) || 0)}</p>
        </div>
      </div>

      <div className="flex gap-1 bg-slate-900/50 p-1 rounded-lg mb-4 w-fit border border-slate-800">
        {["Todos", "Pagar", "Receber", "Conciliacao"].map((tipo) => (
          <button
            key={tipo}
            onClick={() => setAbaAtiva(tipo as any)}
            className={cn(
              "px-4 py-1.5 rounded-md text-sm font-medium transition-colors",
              abaAtiva === tipo ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200"
            )}
          >
            {tipo === "Todos" ? "Todas" : tipo === "Conciliacao" ? "Conciliação" : `Contas a ${tipo}`}
          </button>
        ))}
      </div>

      {/* ABA CONCILIAÇÃO */}
      {abaAtiva === "Conciliacao" && conciliacao && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass p-6 rounded-2xl border border-slate-800">
            <h3 className="text-lg font-bold text-slate-100 mb-4">Resumo do Mês</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between"><span className="text-slate-400">Total a Pagar:</span> <span className="text-rose-400 font-bold">{brl(conciliacao.total_pagar)}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Total a Receber:</span> <span className="text-emerald-400 font-bold">{brl(conciliacao.total_receber)}</span></div>
              <div className="flex justify-between border-t border-slate-800 pt-3 mt-3"><span className="text-slate-300 font-bold">Saldo:</span> <span className={cn("font-bold", conciliacao.saldo >= 0 ? "text-emerald-400" : "text-rose-400")}>{brl(conciliacao.saldo)}</span></div>
            </div>
          </div>
          <div className="glass p-6 rounded-2xl border border-slate-800">
            <h3 className="text-lg font-bold text-slate-100 mb-4">Status das Contas</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between"><span className="text-slate-400">Pagas:</span> <span className="text-emerald-400 font-bold">{brl(conciliacao.pago)}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Pendentes:</span> <span className="text-amber-400 font-bold">{brl(conciliacao.pendente)}</span></div>
              <div className="flex justify-between"><span className="text-slate-400">Atrasadas:</span> <span className="text-rose-400 font-bold">{brl(conciliacao.atrasado)}</span></div>
            </div>
          </div>
        </div>
      )}

      {/* GRID DE CONTAS */}
      {abaAtiva !== "Conciliacao" && (
        <div className="glass rounded-2xl overflow-hidden border border-slate-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50">
              <tr className="text-[11px] uppercase tracking-wider text-slate-400">
                <th className="px-5 py-3 font-medium">Vencimento</th>
                <th className="px-3 py-3 font-medium">Descrição</th>
                <th className="px-3 py-3 font-medium">Categoria</th>
                <th className="px-3 py-3 font-medium">Vínculo</th>
                <th className="px-3 py-3 font-medium">Valor</th>
                <th className="px-3 py-3 font-medium">Origem</th>
                <th className="px-3 py-3 font-medium">Status</th>
                <th className="px-3 py-3 text-right font-medium">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {isLoading ? (
                <tr><td colSpan={7} className="p-8 text-center text-slate-400">Carregando...</td></tr>
              ) : filtrados.length === 0 ? (
                <tr><td colSpan={7} className="p-8 text-center text-slate-400">Nenhuma conta encontrada.</td></tr>
              ) : (
                filtrados.map((c: any) => (
                  <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3 font-mono text-slate-300">{c.vencimento ? c.vencimento.split("-").reverse().join("/") : "—"}</td>
                    <td className="px-3 py-3">
                      <p className="text-slate-200">{c.descricao}</p>
                      <p className="text-xs text-slate-400">{c.observacoes}</p>
                    </td>
                    <td className="px-3 py-3 text-slate-300">{c.categoria}</td>
                    <td className="px-3 py-3 text-slate-300 font-mono text-xs">
                      {c.fornecedor_id && <div className="flex items-center gap-1"><Building2 className="size-3" /> {getFornecedorNome(c.fornecedor_id)}</div>}
                      {c.veiculo_id && <div className="flex items-center gap-1"><Truck className="size-3" /> {getVeiculoPlaca(c.veiculo_id)}</div>}
                      {c.documento_vinculo && <div className="flex items-center gap-1"><FileText className="size-3" /> {c.documento_vinculo}</div>}
                    </td>
                    <td className={cn("px-3 py-3 font-mono font-bold", c.tipo === "Pagar" ? "text-rose-400" : "text-emerald-400")}>
                      {c.tipo === "Pagar" ? "-" : "+"}{brl(Number(c.valor || 0))}
                    </td>
                    <td className="px-3 py-3 text-slate-400 text-xs">{c.origem || "Manual"}</td>
                    <td className="px-3 py-3">
                      <span className={cn(
                        "px-2 py-0.5 rounded text-[10px] font-bold uppercase",
                        c.status === "Pago" ? "bg-emerald-500/20 text-emerald-400" :
                        c.status === "Atrasado" ? "bg-rose-500/20 text-rose-400" :
                        "bg-amber-500/20 text-amber-400"
                      )}>
                        {c.status}
                      </span>
                    </td>
<td className="px-3 py-3 text-right flex justify-end gap-1">
                      {c.status !== "Pago" ? (
                        <Button size="sm" variant="ghost" className="text-emerald-400 hover:bg-emerald-500/10 h-8 px-2" onClick={() => marcarPago.mutate(c.id)}>
                          <CheckCircle2 className="size-4 mr-1" /> Quitar
                        </Button>
                      ) : (
                        <Button size="sm" variant="ghost" className="text-sky-400 hover:bg-sky-500/10 h-8 px-2" onClick={() => { setContaHistorico(c); setModalHistoricoOpen(true); }}>
                          <Eye className="size-4 mr-1" /> Histórico
                        </Button>
                      )}
                      
                      {c.origem === "Importado XML" && (
                        <>
                          <Button size="sm" variant="ghost" className="text-purple-400 hover:bg-purple-500/10 h-8 px-2" onClick={() => navigate(`/financeiro/xml?key=${c.documento_vinculo}`)} title="Imprimir DANFE">
                            <Printer className="size-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="text-sky-400 hover:bg-sky-500/10 h-8 px-2" onClick={() => navigate(`/financeiro/xml?key=${c.documento_vinculo}`)} title="Visualizar DANFE Completo">
                            <FileText className="size-4" />
                          </Button>
                        </>
                      )}

                      <Button size="sm" variant="ghost" className="text-amber-400 hover:bg-amber-500/10 h-8 px-2" onClick={() => abrirEdicao(c)}>
                        <Edit className="size-4" />
                      </Button>
                      <Button size="sm" variant="ghost" className="text-rose-400 hover:bg-rose-500/10 h-8 px-2" disabled={c.status === "Pago"} onClick={() => { if(confirm("Excluir esta conta permanentemente?")) { excluir.mutate(c.id); } }}>
                        <Trash2 className="size-4" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* MODAL DE NOVA CONTA */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">{editando ? "Editar Conta" : "Nova Conta"}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="grid gap-1.5 md:col-span-2">
                <Label className="text-xs text-slate-400">Tipo de Conta</Label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    <input type="radio" checked={form.tipo === "Pagar"} onChange={() => setForm((s: any) => ({ ...s, tipo: "Pagar" }))} /> Conta a Pagar
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    <input type="radio" checked={form.tipo === "Receber"} onChange={() => setForm((s: any) => ({ ...s, tipo: "Receber" }))} /> Conta a Receber
                  </label>
                </div>
              </div>
              
              <div className="grid gap-1.5 md:col-span-2">
                <Label className="text-xs text-slate-400">Descrição *</Label>
                <Input value={form.descricao} onChange={(e) => setForm((s: any) => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Frete Campinas x SP" />
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Categoria</Label>
                <select value={form.categoria} onChange={(e) => setForm((s: any) => ({ ...s, categoria: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  {CATEGORIAS_FALLBACK.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Valor (R$) *</Label>
                <Input type="number" value={form.valor} onChange={(e) => setForm((s: any) => ({ ...s, valor: e.target.value }))} placeholder="0,00" />
              </div>
              
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Vencimento *</Label>
                <Input type="date" value={form.vencimento} onChange={(e) => setForm((s: any) => ({ ...s, vencimento: e.target.value }))} />
              </div>

              {/* Busca de Fornecedor */}
              <div className="grid gap-1.5 relative">
                <Label className="text-xs text-slate-400">Fornecedor</Label>
                <Input 
                  placeholder="Buscar fornecedor por nome ou CNPJ..." 
                  value={buscaFornecedor} 
                  onChange={(e) => { setBuscaFornecedor(e.target.value); setMostrarSugestoesFornecedor(true); }}
                  onFocus={() => setMostrarSugestoesFornecedor(true)}
                  onBlur={() => setTimeout(() => setMostrarSugestoesFornecedor(false), 200)}
                />
                {form.fornecedor_id && (
                  <p className="text-[10px] text-emerald-400 mt-1">Selecionado: {getFornecedorNome(form.fornecedor_id)}</p>
                )}
                {mostrarSugestoesFornecedor && buscaFornecedor.length > 0 && (
                  <div className="absolute top-full mt-1 left-0 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-2xl max-h-48 overflow-y-auto z-50">
                    {fornecedoresFiltrados.map((f: any) => (
                      <button key={f.id} type="button" className="w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-slate-700" onClick={() => { setForm((s: any) => ({ ...s, fornecedor_id: f.id })); setBuscaFornecedor(f.nome); setMostrarSugestoesFornecedor(false); }}>
                        {f.nome} {f.documento && <span className="text-xs text-slate-400">({f.documento})</span>}
                      </button>
                    ))}
                    {fornecedoresFiltrados.length === 0 && (
                      <div className="p-3 text-xs text-slate-400">Nenhum fornecedor encontrado.</div>
                    )}
                  </div>
                )}
              </div>

              {/* Vínculo Dinâmico */}
              {form.tipo === "Pagar" && (
                <div className="grid gap-1.5 md:col-span-2">
                  <Label className="text-xs text-slate-400">Veículo Vinculado</Label>
                  <select value={form.veiculo_id} onChange={(e) => setForm((s: any) => ({ ...s, veiculo_id: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                    <option value="">Nenhum (Despesa Geral)</option>
                    {veiculos.map((v: any) => <option key={v.id} value={v.id}>{v.placa} - {v.modelo}</option>)}
                  </select>
                </div>
              )}
              {form.tipo === "Receber" && (
                <div className="grid gap-1.5 md:col-span-2">
                  <Label className="text-xs text-slate-400">Documento de Vínculo (CT-e, XML, NF)</Label>
                  <Input value={form.documento_vinculo} onChange={(e) => setForm((s: any) => ({ ...s, documento_vinculo: e.target.value }))} placeholder="Ex: CT-e 12345 / NF 67890" />
                </div>
              )}

              <div className="grid gap-1.5 md:col-span-2">
                <Label className="text-xs text-slate-400">Observações</Label>
                <Input value={form.observacoes} onChange={(e) => setForm((s: any) => ({ ...s, observacoes: e.target.value }))} />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate(form)} disabled={salvar.isPending || !form.descricao || !form.valor || !form.vencimento} className="bg-emerald-600 hover:bg-emerald-500 text-white">
                <Check className="size-4 mr-2" /> Salvar Conta
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE HISTÓRICO */}
      {modalHistoricoOpen && contaHistorico && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Histórico da Conta</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalHistoricoOpen(false)}><X className="size-5" /></Button>
            </div>
            
            <div className="space-y-4 mb-6">
              <div className="bg-slate-800/50 p-3 rounded-lg">
                <p className="text-xs text-slate-400">Descrição</p>
                <p className="text-sm font-bold text-slate-200">{contaHistorico.descricao}</p>
                <p className="text-xs text-slate-400 mt-1">Valor Original: {brl(contaHistorico.valor)}</p>
              </div>

              <div className="space-y-3">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Linha do Tempo</p>
                {(contaHistorico.historico || []).length === 0 ? (
                  <p className="text-sm text-slate-500 italic">Nenhum histórico registrado.</p>
                ) : (
                  [...(contaHistorico.historico || [])].reverse().map((h: any, i: number) => (
                    <div key={i} className="flex gap-3 items-start border-l-2 border-slate-700 pl-3 py-1">
                      <div className={cn("mt-1 size-2 rounded-full shrink-0", h.acao === "Baixa" ? "bg-emerald-500" : h.acao === "Estorno" ? "bg-amber-500" : "bg-sky-500")} />
                      <div>
                        <p className="text-sm font-medium text-slate-200">{h.acao} por {h.usuario}</p>
                        <p className="text-xs text-slate-400">{new Date(h.data).toLocaleString("pt-BR")}</p>
                        <p className="text-xs text-slate-400">Valor: {brl(h.valor)}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {contaHistorico.status === "Pago" && (
              <Button onClick={() => estornar.mutate(contaHistorico.id)} disabled={estornar.isPending} className="w-full bg-amber-600 hover:bg-amber-500 text-white">
                <RotateCcw className="size-4 mr-2" /> Estornar Baixa (Voltar para Pendente)
              </Button>
            )}
          </div>
        </div>
      )}


      {/* MODAL DE VISUALIZAÇÃO DA NOTA (XML) */}
      {modalNotaOpen && notaAtual && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Detalhes da Nota Fiscal</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalNotaOpen(false)}><X className="size-5" /></Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-slate-800/50 p-4 rounded-lg">
                <p className="text-xs text-slate-400 mb-1">Chave de Acesso</p>
                <p className="text-xs font-mono text-slate-200 break-all">{notaAtual.documento_vinculo}</p>
              </div>
              <div className="bg-slate-800/50 p-4 rounded-lg">
                <p className="text-xs text-slate-400 mb-1">Valor Total</p>
                <p className="text-lg font-bold text-emerald-400">{brl(notaAtual.valor)}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-xs text-slate-400">Descrição</p>
                <p className="text-sm text-slate-200">{notaAtual.descricao}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Vencimento</p>
                <p className="text-sm text-slate-200">{notaAtual.vencimento ? notaAtual.vencimento.split("-").reverse().join("/") : "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Fornecedor</p>
                <p className="text-sm text-slate-200">{getFornecedorNome(notaAtual.fornecedor_id)}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Origem</p>
                <p className="text-sm text-slate-200">{notaAtual.origem || "Manual"}</p>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalNotaOpen(false)}>Fechar</Button>
              <Button onClick={() => navigate(`/financeiro/xml?key=${notaAtual.documento_vinculo}`)} className="bg-purple-600 hover:bg-purple-500">
                <Printer className="size-4 mr-2" /> Imprimir DANFE
              </Button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}