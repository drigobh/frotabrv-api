import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Save } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const ITENS_PADRAO = [
  "Pneus e Rodas", "Luzes (Farol, Lanterna, Seta)", "Óleo do Motor", 
  "Freios", "Documentação", "Água do Radiador", "Palhetas do Limpador", "Extintor"
];

export default function ChecklistViagem() {
  const qc = useQueryClient();
  const [veiculoId, setVeiculoId] = useState("");
  const [motoristaId, setMotoristaId] = useState("");
  const [itens, setItens] = useState(ITENS_PADRAO.map(nome => ({ nome, status: "OK", observacao: "" })));
  const [obsGeral, setObsGeral] = useState("");

  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: motoristas = [] } = useQuery({ queryKey: ["motoristas"], queryFn: () => apiGet<any[]>("/motoristas") });

  const salvar = useMutation({
    mutationFn: (payload: any) => apiPost("/checklist", payload),
    onSuccess: () => {
      toast.success("Checklist salvo com sucesso!");
      qc.invalidateQueries({ queryKey: ["checklist"] });
      setItens(ITENS_PADRAO.map(nome => ({ nome, status: "OK", observacao: "" })));
      setObsGeral("");
    },
    onError: (e: any) => toast.error("Erro ao salvar: " + e.message)
  });

  const handleSalvar = () => {
    if (!veiculoId || !motoristaId) return toast.error("Selecione o veículo e o motorista.");
    const statusGeral = itens.some(i => i.status === "Falha") ? "Reprovado" : "Aprovado";
    salvar.mutate({ veiculo_id: veiculoId, motorista_id: motoristaId, itens, observacoes_gerais: obsGeral, status_geral: statusGeral });
  };

  return (
    <div>
      <PageHeader
        eyebrow="Frota"
        title="Checklist de Viagem"
        description="Verifique as condições do veículo antes de iniciar a viagem."
        actions={<Button onClick={handleSalvar} disabled={salvar.isPending} className="bg-emerald-600 hover:bg-emerald-500"><Save className="size-4 mr-2" /> Salvar Checklist</Button>}
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

      <div className="glass rounded-2xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3 font-medium">Item Verificado</th>
              <th className="px-3 py-3 font-medium">Status</th>
              <th className="px-3 py-3 font-medium">Observação</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {itens.map((item, index) => (
              <tr key={index} className="hover:bg-slate-800/30">
                <td className="px-5 py-3 text-slate-200 font-medium">{item.nome}</td>
                <td className="px-3 py-3">
                  <div className="flex gap-2">
                    <button onClick={() => { const newItens = [...itens]; newItens[index].status = "OK"; setItens(newItens); }} className={item.status === "OK" ? "text-emerald-400 font-bold" : "text-slate-600"}>OK</button>
                    <button onClick={() => { const newItens = [...itens]; newItens[index].status = "Falha"; setItens(newItens); }} className={item.status === "Falha" ? "text-rose-400 font-bold" : "text-slate-600"}>Falha</button>
                    <button onClick={() => { const newItens = [...itens]; newItens[index].status = "N/A"; setItens(newItens); }} className={item.status === "N/A" ? "text-amber-400 font-bold" : "text-slate-600"}>N/A</button>
                  </div>
                </td>
                <td className="px-3 py-3">
                  <Input value={item.observacao} onChange={(e) => { const newItens = [...itens]; newItens[index].observacao = e.target.value; setItens(newItens); }} placeholder="Opcional..." className="h-8 text-xs" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4">
        <Label className="text-xs text-slate-400">Observações Gerais</Label>
        <textarea value={obsGeral} onChange={(e) => setObsGeral(e.target.value)} className="w-full h-20 bg-slate-950 border border-slate-700 rounded-md p-2 text-sm text-slate-300 mt-1" placeholder="Alguma observação adicional?" />
      </div>
    </div>
  );
}
