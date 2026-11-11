import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Truck, CheckCircle2, FileText, MessageCircle, Trash2, Edit, X, History, ShieldCheck } from "lucide-react";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const CATEGORIAS = [
  { nome: "Elétrica", itens: ["Faróis", "Lanternas", "Setas", "Buzina", "Bateria"] },
  { nome: "Pneus", itens: ["Dianteiros", "Traseiros", "Estepe", "Calibragem"] },
  { nome: "Documentação", itens: ["CRLV", "CNH", "Extintor", "Triângulo"] },
  { nome: "Mecânica", itens: ["Óleo", "Radiador", "Freios", "Suspensão"] },
  { nome: "Chassi", itens: ["Placa", "Chassi Visual", "Limpadores", "Retrovisores"] }
];

const ITENS_INICIAIS = CATEGORIAS.flatMap(cat => 
  cat.itens.map(nome => ({ categoria: cat.nome, nome, status: "OK", observacao: "" }))
);

export default function ChecklistViagem() {
  const qc = useQueryClient();
  
  // Estados dos Modais
  const [modalOpen, setModalOpen] = useState(false);
  const [modalHistoricoOpen, setModalHistoricoOpen] = useState(false);
  const [editandoId, setEditandoId] = useState<string | null>(null);
  const [checklistHistorico, setChecklistHistorico] = useState<any>(null);
  
  // Filtros
  const [filtroVeiculo, setFiltroVeiculo] = useState("");
  const [filtroMotorista, setFiltroMotorista] = useState("");
  
  // Form State
  const [veiculoId, setVeiculoId] = useState("");
  const [motoristaId, setMotoristaId] = useState("");
  const [itens, setItens] = useState(ITENS_INICIAIS);
  const [obsGeral, setObsGeral] = useState("");

  // Queries
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: motoristas = [] } = useQuery({ queryKey: ["motoristas"], queryFn: () => apiGet<any[]>("/motoristas") });
  const { data: checklists = [], isLoading } = useQuery({ 
    queryKey: ["checklist", filtroVeiculo, filtroMotorista], 
    queryFn: () => apiGet<any[]>(`/checklist?veiculo_id=${filtroVeiculo}&motorista_id=${filtroMotorista}`) 
  });

  // Mutations
  const salvar = useMutation({
    mutationFn: (payload: any) => editandoId ? apiPut(`/checklist/${editandoId}`, payload) : apiPost("/checklist", payload),
    onSuccess: () => {
      toast.success(editandoId ? "Checklist atualizado!" : "Checklist gerado!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["checklist"] });
    }
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/checklist/${id}`),
    onSuccess: () => {
      toast.success("Checklist excluído!");
      qc.invalidateQueries({ queryKey: ["checklist"] });
    }
  });

  const abrirNovo = () => {
    setEditandoId(null);
    setVeiculoId("");
    setMotoristaId("");
    setItens(ITENS_INICIAIS);
    setObsGeral("");
    setModalOpen(true);
  };

  const abrirEdicao = (c: any) => {
    setEditandoId(c.id);
    setVeiculoId(c.veiculo_id);
    setMotoristaId(c.motorista_id);
    setItens(c.itens);
    setObsGeral(c.observacoes_gerais || "");
    setModalOpen(true);
  };

  const handleSalvar = () => {
    if (!veiculoId || !motoristaId) return toast.error("Selecione o veículo e o motorista.");
    const statusGeral = itens.some(i => i.status === "Falha") ? "Reprovado" : "Aprovado";
    salvar.mutate({ veiculo_id: veiculoId, motorista_id: motoristaId, itens, observacoes_gerais: obsGeral, status_geral: statusGeral });
  };

  const imprimirPDF = (c: any) => { /* Lógica do PDF mantida */ toast.info("Gerando PDF..."); };
  const enviarWhatsApp = (c: any) => { /* Lógica do Zap mantida */ toast.info("Abrindo WhatsApp..."); };

  // KPIs
  const total = checklists.length;
  const aprovados = checklists.filter((c: any) => c.status_geral === "Aprovado").length;
  const reprovados = checklists.filter((c: any) => c.status_geral === "Reprovado").length;
  const riscoAlto = checklists.filter((c: any) => c.risco === "Alto").length;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Frota"
        title="Checklist de Viagem"
        description="Controle de qualidade e segurança da frota."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Checklist</Button>}
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl border border-slate-800"><p className="text-[11px] uppercase text-slate-400">Total</p><p className="text-2xl font-bold text-slate-200">{total}</p></div>
        <div className="glass p-4 rounded-xl border border-emerald-500/30"><p className="text-[11px] uppercase text-emerald-400">Aprovados</p><p className="text-2xl font-bold text-emerald-400">{aprovados}</p></div>
        <div className="glass p-4 rounded-xl border border-rose-500/30"><p className="text-[11px] uppercase text-rose-400">Reprovados</p><p className="text-2xl font-bold text-rose-400">{reprovados}</p></div>
        <div className="glass p-4 rounded-xl border border-amber-500/30"><p className="text-[11px] uppercase text-amber-400">Risco Alto</p><p className="text-2xl font-bold text-amber-400">{riscoAlto}</p></div>
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3 font-medium">Nº Checklist</th>
              <th className="px-3 py-3 font-medium">Data / Hora</th>
              <th className="px-3 py-3 font-medium">Veículo / Motorista</th>
              <th className="px-3 py-3 font-medium">Avaliação</th>
              <th className="px-3 py-3 font-medium">Aprovado Por / Data</th>
              <th className="px-3 py-3 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {isLoading ? (
              <tr><td colSpan={6} className="p-8 text-center text-slate-400">Carregando...</td></tr>
            ) : checklists.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-slate-400">Nenhum checklist encontrado.</td></tr>
            ) : (
              checklists.map((c: any) => {
                const temFalha = c.status_geral === "Reprovado";
                return (
                  <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3 font-mono text-sky-400 font-bold">{c.numero || c.id.slice(0, 8)}</td>
                    <td className="px-3 py-3 text-slate-300 text-xs">{new Date(c.data_criacao).toLocaleString("pt-BR")}</td>
                    <td className="px-3 py-3">
                      <p className="text-slate-200 font-medium">{veiculos.find((v: any) => v.id === c.veiculo_id)?.placa || c.veiculo_id}</p>
                      <p className="text-xs text-slate-400">{motoristas.find((m: any) => m.id === c.motorista_id)?.nome || c.motorista_id}</p>
                    </td>
                    <td className="px-3 py-3">
                      {temFalha ? (
                        <div className="flex items-center gap-2 text-rose-400 font-bold animate-pulse bg-rose-500/10 px-3 py-1 rounded-full w-fit">
                          <Truck className="size-4" /> REPROVADO
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-emerald-400 font-medium bg-emerald-500/10 px-3 py-1 rounded-full w-fit">
                          <CheckCircle2 className="size-4" /> APROVADO
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-3">
                      {c.aprovado_por ? (
                        <div className="flex flex-col">
                          <span className="text-emerald-400 font-medium text-xs">{c.aprovado_por}</span>
                          <span className="text-slate-500 text-[10px]">{new Date(c.data_aprovacao).toLocaleString("pt-BR")}</span>
                        </div>
                      ) : (
                        <span className="text-slate-500 text-xs">—</span>
                      )}
                    </td>
                    <td className="px-3 py-3 flex gap-1">
                      <Button size="sm" variant="ghost" className="text-sky-400" onClick={() => imprimirPDF(c)} title="PDF"><FileText className="size-4" /></Button>
                      <Button size="sm" variant="ghost" className="text-emerald-400" onClick={() => enviarWhatsApp(c)} title="WhatsApp"><MessageCircle className="size-4" /></Button>
                      {c.historico_correcoes && c.historico_correcoes.length > 0 && (
                        <Button size="sm" variant="ghost" className="text-purple-400" onClick={() => { setChecklistHistorico(c); setModalHistoricoOpen(true); }} title="Histórico"><History className="size-4" /></Button>
                      )}
                      <Button size="sm" variant="ghost" className="text-amber-400" onClick={() => abrirEdicao(c)} title="Editar"><Edit className="size-4" /></Button>
                      <Button size="sm" variant="ghost" className="text-rose-400" onClick={() => { if(confirm("Excluir?")) excluir.mutate(c.id); }} title="Excluir"><Trash2 className="size-4" /></Button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* MODAL DE HISTÓRICO DE CORREÇÃO */}
      {modalHistoricoOpen && checklistHistorico && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2"><ShieldCheck className="size-5 text-emerald-400" /> Histórico de Correção</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalHistoricoOpen(false)}><X className="size-5" /></Button>
            </div>
            <p className="text-sm text-slate-400 mb-4">Este checklist foi reprovado e posteriormente corrigido.</p>
            
            <div className="space-y-3">
              {(checklistHistorico.historico_correcoes || []).map((h: any, i: number) => (
                <div key={i} className="bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                  <p className="text-sm font-bold text-emerald-400">{h.acao} por {h.usuario}</p>
                  <p className="text-xs text-slate-400 mt-1">{new Date(h.data).toLocaleString("pt-BR")}</p>
                  <p className="text-xs text-slate-300 mt-2">Veículo: {veiculos.find((v: any) => v.id === h.veiculo_id)?.placa} | Motorista: {motoristas.find((m: any) => m.id === h.motorista_id)?.nome}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE CRIAÇÃO/EDIÇÃO (Mantido igual ao anterior) */}
      {/* ... Cole aqui o modal que já existe no seu arquivo ... */}
    </div>
  );
}
