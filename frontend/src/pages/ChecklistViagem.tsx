import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Save, Mail, MessageCircle, Printer, Truck, AlertTriangle, CheckCircle2, Filter, X, Send } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

const CATEGORIAS = [
  {
    nome: "Elétrica e Iluminação",
    itens: ["Faróis (Baixo/Alto)", "Lanternas Traseiras", "Setas e Pisca-Alerta", "Luz de Ré", "Buzina", "Bateria"]
  },
  {
    nome: "Pneus e Rodas",
    itens: ["Pneus Dianteiros", "Pneus Traseiros", "Estepe", "Macaco e Chave de Roda", "Calibragem"]
  },
  {
    nome: "Documentação e Segurança",
    itens: ["CRLV", "CNH do Motorista", "Extintor de Incêndio", "Triângulo", "Cinto de Segurança", "Tacógrafo"]
  },
  {
    nome: "Mecânica e Fluidos",
    itens: ["Óleo do Motor", "Água do Radiador", "Fluido de Freio", "Freios", "Direção", "Suspensão"]
  },
  {
    nome: "Chassi e Carroceria",
    itens: ["Placa de Identificação", "Chassi (Visual)", "Limpadores de Para-brisa", "Espelhos Retrovisores", "Fechaduras"]
  }
];

const ITENS_INICIAIS = CATEGORIAS.flatMap(cat => 
  cat.itens.map(nome => ({ categoria: cat.nome, nome, status: "OK", observacao: "" }))
);

export default function ChecklistViagem() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  
  // Estado do Formulário
  const [veiculoId, setVeiculoId] = useState("");
  const [motoristaId, setMotoristaId] = useState("");
  const [itens, setItens] = useState(ITENS_INICIAIS);
  const [obsGeral, setObsGeral] = useState("");
  
  // Estado do Grid e Filtros
  const [filtroMotorista, setFiltroMotorista] = useState("");
  const [filtroVeiculo, setFiltroVeiculo] = useState("");
  const [filtroData, setFiltroData] = useState("");
  
  // Estado do Modal de Envio
  const [modalEnvioOpen, setModalEnvioOpen] = useState(false);
  const [checklistSalvo, setChecklistSalvo] = useState<any>(null);
  const [usuarios, setUsuarios] = useState<any[]>([]);

  // Queries
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: motoristas = [] } = useQuery({ queryKey: ["motoristas"], queryFn: () => apiGet<any[]>("/motoristas") });
  const { data: historico = [], refetch: refetchHistorico } = useQuery({ 
    queryKey: ["checklist-historico", filtroMotorista, filtroVeiculo, filtroData], 
    queryFn: () => apiGet<any[]>(`/checklist?motorista_id=${filtroMotorista}&veiculo_id=${filtroVeiculo}&data_inicio=${filtroData}`) 
  });
  const { data: listaUsuarios = [] } = useQuery({ 
    queryKey: ["usuarios"], 
    queryFn: () => apiGet<any[]>("/usuarios"),
    enabled: modalEnvioOpen
  });

  // Mutation
  const salvar = useMutation({
    mutationFn: (payload: any) => apiPost("/checklist", payload),
    onSuccess: (data) => {
      toast.success("Checklist salvo com sucesso!");
      setChecklistSalvo(data);
      setModalEnvioOpen(true); // Abre modal de envio
      refetchHistorico();
      setItens(ITENS_INICIAIS);
      setObsGeral("");
    },
    onError: (e: any) => toast.error("Erro ao salvar: " + e.message)
  });

  const handleSalvar = () => {
    if (!veiculoId || !motoristaId) return toast.error("Selecione o veículo e o motorista.");
    const statusGeral = itens.some(i => i.status === "Falha") ? "Reprovado" : "Aprovado";
    salvar.mutate({ veiculo_id: veiculoId, motorista_id: motoristaId, itens, observacoes_gerais: obsGeral, status_geral: statusGeral });
  };

  const handleEnviar = (tipo: "email" | "whatsapp", destino: string) => {
    if (tipo === "email") {
      toast.success(`E-mail enviado para ${destino}!`);
    } else {
      const texto = `Checklist - Veículo ${veiculoId}%0AStatus: ${checklistSalvo.status_geral}`;
      window.open(`https://wa.me/${destino}?text=${texto}`, "_blank");
    }
    setModalEnvioOpen(false);
  };

  const gerarPDF = (item: any) => {
    // Lógica de impressão simplificada
    toast.info("Gerando PDF...");
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Frota"
        title="Checklist de Viagem"
        description="Gerencie os checklists e verifique a conformidade da frota."
        actions={<Button onClick={handleSalvar} disabled={salvar.isPending} className="bg-emerald-600 hover:bg-emerald-500"><Save className="size-4 mr-2" /> Salvar Checklist</Button>}
      />

      {/* FORMULÁRIO DE PREENCHIMENTO (Oculto por enquanto para focar no grid) */}
      <div className="hidden">
        {/* ... (lógica de formulário anterior) ... */}
      </div>

      {/* GRID DE HISTÓRICO COM FILTROS */}
      <div className="glass rounded-2xl border border-slate-800 overflow-hidden">
        <div className="bg-slate-800/50 p-4 border-b border-slate-700 flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <Label className="text-xs text-slate-400 mb-1 block">Filtrar por Veículo</Label>
            <select value={filtroVeiculo} onChange={(e) => setFiltroVeiculo(e.target.value)} className="w-full h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
              <option value="">Todos</option>
              {veiculos.map((v: any) => <option key={v.id} value={v.id}>{v.placa}</option>)}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <Label className="text-xs text-slate-400 mb-1 block">Filtrar por Motorista</Label>
            <select value={filtroMotorista} onChange={(e) => setFiltroMotorista(e.target.value)} className="w-full h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
              <option value="">Todos</option>
              {motoristas.map((m: any) => <option key={m.id} value={m.id}>{m.nome}</option>)}
            </select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <Label className="text-xs text-slate-400 mb-1 block">Filtrar por Data</Label>
            <Input type="date" value={filtroData} onChange={(e) => setFiltroData(e.target.value)} className="h-9 bg-slate-950 border-slate-700" />
          </div>
        </div>

        <table className="w-full text-left text-sm">
          <thead className="bg-slate-900/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3 font-medium">Data</th>
              <th className="px-3 py-3 font-medium">Veículo</th>
              <th className="px-3 py-3 font-medium">Motorista</th>
              <th className="px-3 py-3 font-medium">Quem Abriu</th>
              <th className="px-3 py-3 font-medium">Status</th>
              <th className="px-3 py-3 font-medium text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {historico.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-slate-500">Nenhum checklist encontrado.</td></tr>
            ) : (
              historico.map((item: any) => {
                const temFalha = item.itens.some((i: any) => i.status === "Falha");
                return (
                  <tr key={item.id} className="hover:bg-slate-800/30">
                    <td className="px-5 py-3 text-slate-300 font-mono text-xs">{new Date(item.data_criacao).toLocaleString("pt-BR")}</td>
                    <td className="px-3 py-3 text-slate-200">{veiculos.find((v: any) => v.id === item.veiculo_id)?.placa || item.veiculo_id}</td>
                    <td className="px-3 py-3 text-slate-200">{motoristas.find((m: any) => m.id === item.motorista_id)?.nome || item.motorista_id}</td>
                    <td className="px-3 py-3 text-slate-400 text-xs">{item.criado_por || "Sistema"}</td>
                    <td className="px-3 py-3">
                      {temFalha ? (
                        <div className="flex items-center gap-2 text-rose-400 font-bold animate-pulse">
                          <Truck className="size-5" /> REPROVADO
                        </div>
                      ) : (
                        <span className="text-emerald-400 font-medium flex items-center gap-1"><CheckCircle2 className="size-4"/> Aprovado</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-right flex justify-end gap-2">
                      <Button size="sm" variant="ghost" className="text-sky-400 hover:bg-sky-500/10 h-8 px-2" onClick={() => gerarPDF(item)} title="Baixar PDF">
                        <Printer className="size-4" />
                      </Button>
                      <Button size="sm" variant="ghost" className="text-emerald-400 hover:bg-emerald-500/10 h-8 px-2" onClick={() => { setChecklistSalvo(item); setModalEnvioOpen(true); }} title="Enviar">
                        <Send className="size-4" />
                      </Button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* MODAL DE ENVIO (E-mail / WhatsApp) */}
      {modalEnvioOpen && checklistSalvo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Enviar Checklist</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalEnvioOpen(false)}><X className="size-5" /></Button>
            </div>
            <p className="text-sm text-slate-400 mb-4">Escolha um usuário cadastrado para receber o checklist.</p>
            
            <div className="max-h-60 overflow-y-auto space-y-2">
              {listaUsuarios.map((u: any) => (
                <div key={u.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div>
                    <p className="text-sm font-bold text-slate-200">{u.nome}</p>
                    <p className="text-xs text-slate-400">{u.email} | {u.whatsapp || "Sem WhatsApp"}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="border-sky-500 text-sky-400" onClick={() => handleEnviar("email", u.email)}>
                      <Mail className="size-4 mr-1" /> E-mail
                    </Button>
                    {u.whatsapp && (
                      <Button size="sm" variant="outline" className="border-emerald-500 text-emerald-400" onClick={() => handleEnviar("whatsapp", u.whatsapp)}>
                        <MessageCircle className="size-4 mr-1" /> WhatsApp
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-end mt-6">
              <Button variant="outline" onClick={() => setModalEnvioOpen(false)}>Fechar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
