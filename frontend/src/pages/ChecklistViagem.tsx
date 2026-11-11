import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Save, Mail, MessageCircle, FileText, Edit, Trash2, Printer, CheckCircle2, ShieldAlert } from "lucide-react";
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
  const [veiculoId, setVeiculoId] = useState("");
  const [motoristaId, setMotoristaId] = useState("");
  const [itens, setItens] = useState(ITENS_INICIAIS);
  const [obsGeral, setObsGeral] = useState("");
  const [checklistSalvo, setChecklistSalvo] = useState<any>(null);

  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: motoristas = [] } = useQuery({ queryKey: ["motoristas"], queryFn: () => apiGet<any[]>("/motoristas") });

  const salvar = useMutation({
    mutationFn: (payload: any) => apiPost("/checklist", payload),
    onSuccess: (data) => {
      toast.success("Checklist salvo com sucesso!");
      setChecklistSalvo(data);
      qc.invalidateQueries({ queryKey: ["checklist"] });
    },
    onError: (e: any) => toast.error("Erro ao salvar: " + e.message)
  });

  const handleSalvar = () => {
    if (!veiculoId || !motoristaId) return toast.error("Selecione o veículo e o motorista.");
    const statusGeral = itens.some(i => i.status === "Falha") ? "Reprovado" : "Aprovado";
    salvar.mutate({ veiculo_id: veiculoId, motorista_id: motoristaId, itens, observacoes_gerais: obsGeral, status_geral: statusGeral });
  };

  const gerarPDF = () => {
    if (!checklistSalvo) return toast.error("Salve o checklist antes de gerar o PDF.");
    window.print();
  };

  const enviarEmail = () => {
    if (!checklistSalvo) return toast.error("Salve o checklist primeiro.");
    toast.info("Função de e-mail será integrada na próxima etapa.");
  };

  const enviarWhatsApp = () => {
    if (!checklistSalvo) return toast.error("Salve o checklist primeiro.");
    const texto = `Checklist de Viagem - Veículo ${veiculoId}%0AStatus: ${checklistSalvo.status_geral}%0AObservações: ${obsGeral}`;
    window.open(`https://wa.me/?text=${texto}`, "_blank");
  };

  const excluirChecklist = () => {
    if (!checklistSalvo) return;
    if (confirm("Tem certeza que deseja excluir este checklist?")) {
      toast.info("Função de exclusão será integrada na próxima etapa.");
    }
  };

  return (
    <div className="print:bg-white">
      <div className="print:hidden">
        <PageHeader
          eyebrow="Frota"
          title="Checklist de Viagem"
          description="Verifique as condições do veículo antes de iniciar a viagem."
          actions={
            <div className="flex gap-2">
              <Button onClick={handleSalvar} disabled={salvar.isPending} className="bg-emerald-600 hover:bg-emerald-500">
                <Save className="size-4 mr-2" /> Salvar
              </Button>
              {checklistSalvo && (
                <>
                  <Button onClick={gerarPDF} variant="outline" className="border-slate-700 text-slate-300">
                    <Printer className="size-4 mr-2" /> PDF
                  </Button>
                  <Button onClick={enviarEmail} variant="outline" className="border-slate-700 text-slate-300">
                    <Mail className="size-4 mr-2" /> E-mail
                  </Button>
                  <Button onClick={enviarWhatsApp} variant="outline" className="border-slate-700 text-emerald-400 hover:bg-emerald-500/10">
                    <MessageCircle className="size-4 mr-2" /> WhatsApp
                  </Button>
                  <Button onClick={() => setChecklistSalvo(null)} variant="outline" className="border-slate-700 text-amber-400">
                    <Edit className="size-4 mr-2" /> Editar
                  </Button>
                  <Button onClick={excluirChecklist} variant="outline" className="border-slate-700 text-rose-400">
                    <Trash2 className="size-4 mr-2" /> Excluir
                  </Button>
                </>
              )}
            </div>
          }
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="grid gap-1.5">
            <Label className="text-xs text-slate-400">Veículo</Label>
            <select value={veiculoId} onChange={(e) => setVeiculoId(e.target.value)} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
              <option value="">Selecione o veículo</option>
              {veiculos.map((v: any) => <option key={v.id} value={v.id}>{v.placa} - {v.modelo}</option>)}
            </select>
          </div>
          <div className="grid gap-1.5">
            <Label className="text-xs text-slate-400">Motorista</Label>
            <select value={motoristaId} onChange={(e) => setMotoristaId(e.target.value)} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
              <option value="">Selecione o motorista</option>
              {motoristas.map((m: any) => <option key={m.id} value={m.id}>{m.nome}</option>)}
            </select>
          </div>
        </div>

        {/* Renderização por Categorias */}
        <div className="space-y-6 mb-6">
          {CATEGORIAS.map((cat, catIndex) => (
            <div key={catIndex} className="glass rounded-2xl border border-slate-800 overflow-hidden">
              <div className="bg-slate-800/80 px-5 py-3 border-b border-slate-700">
                <h3 className="text-sm font-bold text-sky-400 uppercase tracking-wider">{cat.nome}</h3>
              </div>
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-900/50">
                  <tr className="text-[10px] uppercase tracking-wider text-slate-500">
                    <th className="px-5 py-2 font-medium">Item</th>
                    <th className="px-3 py-2 font-medium">Status</th>
                    <th className="px-3 py-2 font-medium">Observação</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {itens.filter(i => i.categoria === cat.nome).map((item, index) => {
                    const globalIndex = itens.findIndex(i => i.categoria === cat.nome && i.nome === item.nome);
                    return (
                      <tr key={index} className="hover:bg-slate-800/30">
                        <td className="px-5 py-3 text-slate-200 font-medium">{item.nome}</td>
                        <td className="px-3 py-3">
                          <div className="flex gap-2">
                            <button onClick={() => { const newItens = [...itens]; newItens[globalIndex].status = "OK"; setItens(newItens); }} className={item.status === "OK" ? "text-emerald-400 font-bold bg-emerald-500/10 px-2 py-1 rounded" : "text-slate-600 hover:text-slate-400 px-2 py-1"}>OK</button>
                            <button onClick={() => { const newItens = [...itens]; newItens[globalIndex].status = "Falha"; setItens(newItens); }} className={item.status === "Falha" ? "text-rose-400 font-bold bg-rose-500/10 px-2 py-1 rounded" : "text-slate-600 hover:text-slate-400 px-2 py-1"}>Falha</button>
                            <button onClick={() => { const newItens = [...itens]; newItens[globalIndex].status = "N/A"; setItens(newItens); }} className={item.status === "N/A" ? "text-amber-400 font-bold bg-amber-500/10 px-2 py-1 rounded" : "text-slate-600 hover:text-slate-400 px-2 py-1"}>N/A</button>
                          </div>
                        </td>
                        <td className="px-3 py-3">
                          <Input value={item.observacao} onChange={(e) => { const newItens = [...itens]; newItens[globalIndex].observacao = e.target.value; setItens(newItens); }} placeholder="Opcional..." className="h-8 text-xs bg-slate-950" />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ))}
        </div>

        <div className="mb-6">
          <Label className="text-xs text-slate-400">Observações Gerais</Label>
          <textarea value={obsGeral} onChange={(e) => setObsGeral(e.target.value)} className="w-full h-20 bg-slate-950 border border-slate-700 rounded-md p-2 text-sm text-slate-300 mt-1" placeholder="Alguma observação adicional?" />
        </div>
      </div>

      {/* ÁREA DE IMPRESSÃO (Visível apenas no PDF) */}
      {checklistSalvo && (
        <div className="hidden print:block p-8 text-black bg-white">
          <div className="text-center mb-6">
            <h1 className="text-2xl font-bold">Checklist de Viagem</h1>
            <p className="text-sm">Bravus Frota - Gestão de Frotas</p>
          </div>
          <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
            <p><b>Veículo:</b> {veiculos.find((v: any) => v.id === veiculoId)?.placa}</p>
            <p><b>Motorista:</b> {motoristas.find((m: any) => m.id === motoristaId)?.nome}</p>
            <p><b>Data:</b> {new Date().toLocaleString("pt-BR")}</p>
            <p><b>Status Geral:</b> {checklistSalvo.status_geral}</p>
          </div>
          <table className="w-full border-collapse border border-black text-xs mb-4">
            <thead>
              <tr className="bg-gray-200">
                <th className="border border-black p-2 text-left">Categoria</th>
                <th className="border border-black p-2 text-left">Item</th>
                <th className="border border-black p-2">Status</th>
                <th className="border border-black p-2">Obs</th>
              </tr>
            </thead>
            <tbody>
              {itens.map((item, i) => (
                <tr key={i}>
                  <td className="border border-black p-2">{item.categoria}</td>
                  <td className="border border-black p-2">{item.nome}</td>
                  <td className="border border-black p-2 text-center font-bold">{item.status}</td>
                  <td className="border border-black p-2 text-center">{item.observacao}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="text-sm">
            <p><b>Observações Gerais:</b> {obsGeral || "Nenhuma"}</p>
            <p className="mt-8">Assinatura do Motorista: ___________________________</p>
          </div>
        </div>
      )}
    </div>
  );
}
