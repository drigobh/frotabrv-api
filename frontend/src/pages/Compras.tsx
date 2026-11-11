import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, CheckCircle2, XCircle, Clock, X, ShoppingCart, DollarSign, Package } from "lucide-react";
import { apiGet, apiPost, apiPatch, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function Compras() {
  const qc = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [modalAprovacaoOpen, setModalAprovacaoOpen] = useState(false);
  const [pedidoSelecionado, setPedidoSelecionado] = useState<any>(null);

  // Form State
  const [fornecedorId, setFornecedorId] = useState("");
  const [veiculoId, setVeiculoId] = useState("");
  const [descricao, setDescricao] = useState("");
  const [quantidade, setQuantidade] = useState("");
  const [valorUnit, setValorUnit] = useState("");
  const [obs, setObs] = useState("");

  // Queries
  const { data: pedidos = [] } = useQuery({ queryKey: ["compras"], queryFn: () => apiGet<any[]>("/compras") });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });

  // Mutations
  const salvar = useMutation({
    mutationFn: (payload: any) => apiPost("/compras", payload),
    onSuccess: () => {
      toast.success("Pedido de compra criado!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["compras"] });
    }
  });

  const aprovar = useMutation({
    mutationFn: (payload: any) => apiPatch(`/compras/${pedidoSelecionado.id}/aprovar`, payload),
    onSuccess: () => {
      toast.success("Pedido atualizado!");
      setModalAprovacaoOpen(false);
      qc.invalidateQueries({ queryKey: ["compras"] });
    }
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/compras/${id}`),
    onSuccess: () => {
      toast.success("Pedido excluído!");
      qc.invalidateQueries({ queryKey: ["compras"] });
    }
  });

  const handleSalvar = () => {
    if (!fornecedorId || !descricao || !quantidade || !valorUnit) {
      return toast.error("Preencha todos os campos obrigatórios.");
    }
    const qtd = parseFloat(quantidade);
    const unit = parseFloat(valorUnit);
    salvar.mutate({
      fornecedor_id: fornecedorId,
      veiculo_id: veiculoId || null,
      itens: [{ descricao, quantidade: qtd, valor_unitario: unit }],
      observacoes: obs,
      valor_total: qtd * unit
    });
  };

  // KPIs
  const total = pedidos.length;
  const pendentes = pedidos.filter((p: any) => p.status === "Pendente").length;
  const aprovados = pedidos.filter((p: any) => p.status === "Aprovado").length;
  const valorAprovado = pedidos.filter((p: any) => p.status === "Aprovado").reduce((acc: number, p: any) => acc + (p.valor_total || 0), 0);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Suprimentos"
        title="Compras e Aprovações"
        description="Gerencie pedidos de compra, aprove ou reprove orçamentos."
        actions={<Button onClick={() => setModalOpen(true)} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Pedido</Button>}
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass p-4 rounded-xl border border-slate-800"><p className="text-[11px] uppercase text-slate-400">Total Pedidos</p><p className="text-2xl font-bold text-slate-200">{total}</p></div>
        <div className="glass p-4 rounded-xl border border-amber-500/30"><p className="text-[11px] uppercase text-amber-400">Aguardando Aprovação</p><p className="text-2xl font-bold text-amber-400">{pendentes}</p></div>
        <div className="glass p-4 rounded-xl border border-emerald-500/30"><p className="text-[11px] uppercase text-emerald-400">Aprovados</p><p className="text-2xl font-bold text-emerald-400">{aprovados}</p></div>
        <div className="glass p-4 rounded-xl border border-sky-500/30"><p className="text-[11px] uppercase text-sky-400">Valor Aprovado</p><p className="text-2xl font-bold text-sky-400">{brl(valorAprovado)}</p></div>
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3 font-medium">Nº Pedido</th>
              <th className="px-3 py-3 font-medium">Data</th>
              <th className="px-3 py-3 font-medium">Fornecedor / Item</th>
              <th className="px-3 py-3 font-medium">Valor Total</th>
              <th className="px-3 py-3 font-medium">Status</th>
              <th className="px-3 py-3 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {pedidos.length === 0 ? (
              <tr><td colSpan={6} className="p-8 text-center text-slate-400">Nenhum pedido encontrado.</td></tr>
            ) : (
              pedidos.map((p: any) => (
                <tr key={p.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-3 font-mono text-sky-400 font-bold">{p.numero || p.id.slice(0, 8)}</td>
                  <td className="px-3 py-3 text-slate-300 text-xs">{new Date(p.data_criacao).toLocaleString("pt-BR")}</td>
                  <td className="px-3 py-3">
                    <p className="text-slate-200 font-medium">{fornecedores.find((f: any) => f.id === p.fornecedor_id)?.nome || "Fornecedor"}</p>
                    <p className="text-xs text-slate-400">{p.itens?.[0]?.descricao || "Item"}</p>
                  </td>
                  <td className="px-3 py-3 font-mono font-bold text-slate-200">{brl(p.valor_total)}</td>
                  <td className="px-3 py-3">
                    <span className={cn(
                      "px-2 py-1 rounded text-xs font-bold",
                      p.status === "Pendente" ? "bg-amber-500/20 text-amber-400" :
                      p.status === "Aprovado" ? "bg-emerald-500/20 text-emerald-400" :
                      p.status === "Reprovado" ? "bg-rose-500/20 text-rose-400" :
                      "bg-sky-500/20 text-sky-400"
                    )}>
                      {p.status}
                    </span>
                  </td>
                  <td className="px-3 py-3 flex gap-1">
                    {p.status === "Pendente" && (
                      <Button size="sm" variant="ghost" className="text-sky-400" onClick={() => { setPedidoSelecionado(p); setModalAprovacaoOpen(true); }} title="Aprovar/Reprovar">
                        <CheckCircle2 className="size-4" />
                      </Button>
                    )}
                    <Button size="sm" variant="ghost" className="text-rose-400" onClick={() => { if(confirm("Excluir?")) excluir.mutate(p.id); }} title="Excluir">
                      <XCircle className="size-4" />
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* MODAL DE CRIAÇÃO */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Novo Pedido de Compra</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>
            <div className="grid gap-4">
              <div>
                <Label className="text-xs text-slate-400">Fornecedor *</Label>
                <select value={fornecedorId} onChange={(e) => setFornecedorId(e.target.value)} className="w-full h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  <option value="">Selecione</option>
                  {fornecedores.map((f: any) => <option key={f.id} value={f.id}>{f.nome}</option>)}
                </select>
              </div>
              <div>
                <Label className="text-xs text-slate-400">Veículo (Opcional)</Label>
                <select value={veiculoId} onChange={(e) => setVeiculoId(e.target.value)} className="w-full h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  <option value="">Nenhum (Despesa Geral)</option>
                  {veiculos.map((v: any) => <option key={v.id} value={v.id}>{v.placa}</option>)}
                </select>
              </div>
              <div>
                <Label className="text-xs text-slate-400">Item / Descrição *</Label>
                <Input value={descricao} onChange={(e) => setDescricao(e.target.value)} placeholder="Ex: Óleo 15w40" className="bg-slate-950" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs text-slate-400">Qtd *</Label>
                  <Input type="number" value={quantidade} onChange={(e) => setQuantidade(e.target.value)} placeholder="1" className="bg-slate-950" />
                </div>
                <div>
                  <Label className="text-xs text-slate-400">Valor Unitário *</Label>
                  <Input type="number" value={valorUnit} onChange={(e) => setValorUnit(e.target.value)} placeholder="0.00" className="bg-slate-950" />
                </div>
              </div>
              <div>
                <Label className="text-xs text-slate-400">Observações</Label>
                <textarea value={obs} onChange={(e) => setObs(e.target.value)} className="w-full h-20 bg-slate-950 border border-slate-700 rounded-md p-2 text-sm text-slate-300" />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleSalvar} disabled={salvar.isPending} className="bg-emerald-600 hover:bg-emerald-500">Enviar para Aprovação</Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE APROVAÇÃO */}
      {modalAprovacaoOpen && pedidoSelecionado && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Aprovar Pedido {pedidoSelecionado.numero}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalAprovacaoOpen(false)}><X className="size-5" /></Button>
            </div>
            <div className="bg-slate-800/50 p-4 rounded-lg mb-4">
              <p className="text-sm font-bold text-slate-200">{fornecedores.find((f: any) => f.id === pedidoSelecionado.fornecedor_id)?.nome}</p>
              <p className="text-xs text-slate-400">{pedidoSelecionado.itens?.[0]?.descricao}</p>
              <p className="text-lg font-bold text-emerald-400 mt-2">{brl(pedidoSelecionado.valor_total)}</p>
            </div>
            <Label className="text-xs text-slate-400">Motivo (opcional para reprovar)</Label>
            <textarea id="motivo" className="w-full h-20 bg-slate-950 border border-slate-700 rounded-md p-2 text-sm text-slate-300 mt-1" placeholder="Justificativa..." />
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalAprovacaoOpen(false)}>Cancelar</Button>
              <Button variant="outline" className="border-rose-500 text-rose-400" onClick={() => {
                const motivo = (document.getElementById("motivo") as HTMLTextAreaElement)?.value || "";
                aprovar.mutate({ status: "Reprovado", motivo });
              }}>Reprovar</Button>
              <Button className="bg-emerald-600 hover:bg-emerald-500" onClick={() => aprovar.mutate({ status: "Aprovado" })}>Aprovar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
