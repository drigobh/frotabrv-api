import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, Sparkles, X, Save, Check, Trash2, MapPin, Phone, Mail } from "lucide-react";
import { apiGet, apiPost, apiPatch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function Orcamentos() {
  const qc = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  
  // Estados do Orçamento
  const [produto, setProduto] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [ofertas, setOfertas] = useState<any[]>([]);

  // Estados da IA
  const [cidade, setCidade] = useState("");
  const [pesquisando, setPesquisando] = useState(false);
  const [resultadosIA, setResultadosIA] = useState<any[]>([]);

  // Estados do Fornecedor Manual
  const [modalFornecedorOpen, setModalFornecedorOpen] = useState(false);
  const [tipoForn, setTipoForn] = useState("");
  const [fornecedorManual, setFornecedorManual] = useState<any>(null);

  const { data: orcamentos = [] } = useQuery({ queryKey: ["orcamentos"], queryFn: () => apiGet<any[]>("/orcamentos") });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });

  const salvar = useMutation({
    mutationFn: (payload: any) => apiPost("/orcamentos", payload),
    onSuccess: () => {
      toast.success("Orçamento salvo!");
      setModalOpen(false);
      setOfertas([]); setProduto(""); setResultadosIA([]);
      qc.invalidateQueries({ queryKey: ["orcamentos"] });
    }
  });

  const escolherVencedor = useMutation({
    mutationFn: (payload: any) => apiPatch(`/orcamentos/${payload.id}/escolher-vencedor`, payload),
    onSuccess: () => {
      toast.success("Vencedor escolhido! Pedido de Compra gerado.");
      qc.invalidateQueries({ queryKey: ["orcamentos"] });
    }
  });

  const pesquisarComIA = async () => {
    if (!produto || !cidade) return toast.error("Preencha o produto e a cidade.");
    setPesquisando(true);
    try {
      const res = await apiPost<any[]>("/orcamentos/ia-search", { produto, cidade, estado: "MG" });
      setResultadosIA(res);
    } catch (e) { toast.error("Erro na IA"); } finally { setPesquisando(false); }
  };

  const adicionarOferta = async (base: any) => {
    if (!produto) return toast.error("Preencha o produto antes de adicionar fornecedores.");
    
    // Checar histórico de preço
    if (base.fornecedor_id) {
      try {
        const hist = await apiGet<any>(`/orcamentos/historico-preco?produto=${produto}&fornecedor_id=${base.fornecedor_id}`);
        if (hist.tem_historico && hist.preco !== base.valor_unitario) {
          const confirma = confirm(`Atenção: O último preço comprado deste fornecedor para este produto foi ${brl(hist.preco)} por ${hist.usuario}. Deseja continuar com ${brl(base.valor_unitario)}?`);
          if (!confirma) return;
        }
      } catch (e) {}
    }

    setOfertas([...ofertas, { ...base, quantidade: 1, prazo_entrega: "5 dias", prazo_pagamento: "30 dias", forma_pagamento: "Boleto" }]);
    toast.success("Fornecedor adicionado ao orçamento.");
  };

  const handleSalvar = () => {
    if (ofertas.length === 0) return toast.error("Adicione pelo menos um fornecedor.");
    salvar.mutate({ produto, observacoes, ofertas });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Compras"
        title="Orçamentos"
        description="Pesquise com IA ou use fornecedores cadastrados."
        actions={<Button onClick={() => setModalOpen(true)} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2"/> Novo Orçamento</Button>}
      />

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3">Nº Orçamento</th>
              <th className="px-3 py-3">Produto</th>
              <th className="px-3 py-3">Ofertas</th>
              <th className="px-3 py-3">Status</th>
              <th className="px-3 py-3">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {orcamentos.map((o: any) => (
              <tr key={o.id} className="hover:bg-slate-800/30">
                <td className="px-5 py-3 font-mono text-sky-400 font-bold">{o.numero}</td>
                <td className="px-3 py-3 text-slate-200">{o.produto}</td>
                <td className="px-3 py-3 text-slate-400">{o.ofertas.length} opções</td>
                <td className="px-3 py-3"><span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded text-xs font-bold">{o.status}</span></td>
                <td className="px-3 py-3 flex gap-2">
                  <Button size="sm" variant="ghost" className="text-emerald-400" onClick={() => {
                    // Abrir modal para escolher vencedor
                    const vencedor = prompt(`Qual fornecedor venceu?\n${o.ofertas.map((x:any) => x.fornecedor_nome).join("\n")}`);
                    const of = o.ofertas.find((x:any) => x.fornecedor_nome === vencedor);
                    if (of) escolherVencedor.mutate({ id: o.id, fornecedor_id: of.fornecedor_id, fornecedor_nome: of.fornecedor_nome });
                  }}>Escolher Vencedor</Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* MODAL DE NOVO ORÇAMENTO */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-800/30">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2"><Sparkles className="size-5 text-purple-400"/> Novo Orçamento</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><Label className="text-xs text-slate-400">Produto (Descritivo)</Label><Input value={produto} onChange={e => setProduto(e.target.value)} placeholder="Ex: farol volvo fh440 lado esquerdo" className="bg-slate-950" /></div>
                <div><Label className="text-xs text-slate-400">Observações</Label><Input value={observacoes} onChange={e => setObservacoes(e.target.value)} className="bg-slate-950" /></div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* BLOCO MANUAL */}
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                  <h3 className="text-sm font-bold text-slate-200 mb-3">Fornecedor Manual</h3>
                  <div className="flex gap-2">
                    <select value={tipoForn} onChange={(e) => setTipoForn(e.target.value)} className="flex-1 h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="">Escolha o Tipo de Fornecedor</option>
                      {tipos.map((t: any) => <option key={t.id} value={t.id}>{t.nome}</option>)}
                    </select>
                    <Button onClick={() => setModalFornecedorOpen(true)} disabled={!tipoForn} className="bg-sky-600">Listar</Button>
                  </div>
                </div>

                {/* BLOCO IA */}
                <div className="bg-purple-500/10 p-4 rounded-lg border border-purple-500/30">
                  <h3 className="text-sm font-bold text-purple-400 mb-3 flex items-center gap-2"><Sparkles className="size-4"/> Busca com IA</h3>
                  <div className="flex gap-2">
                    <Input placeholder="Cidade (ex: Contagem)" value={cidade} onChange={e => setCidade(e.target.value)} className="bg-slate-950" />
                    <Button onClick={pesquisarComIA} disabled={pesquisando} className="bg-purple-600">{pesquisando ? "..." : "Buscar"}</Button>
                    <Button variant="outline" onClick={() => { setResultadosIA([]); setCidade(""); }} className="border-slate-700 text-slate-400"><X className="size-4"/></Button>
                  </div>
                </div>
              </div>

              {/* RESULTADOS IA */}
              {resultadosIA.length > 0 && (
                <div className="bg-slate-900 border border-purple-500/30 rounded-lg p-4">
                  <p className="text-xs font-bold text-purple-400 uppercase mb-3">Resultados da IA para "{produto}"</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {resultadosIA.map((r, i) => (
                      <div key={i} className="bg-slate-800/50 p-3 rounded border border-slate-700 text-xs">
                        <p className="font-bold text-slate-200">{r.fornecedor_nome}</p>
                        <p className="text-emerald-400 font-bold my-1">{brl(r.preco)}</p>
                        <div className="text-slate-400 space-y-1 mb-2">
                          <p className="flex items-center gap-1"><MapPin className="size-3"/> {r.distancia}</p>
                          <p className="flex items-center gap-1"><Phone className="size-3"/> {r.whatsapp}</p>
                          <p className="flex items-center gap-1"><Mail className="size-3"/> {r.email}</p>
                        </div>
                        <Button size="sm" onClick={() => adicionarOferta({ fornecedor_nome: r.fornecedor_nome, valor_unitario: r.preco, whatsapp: r.whatsapp, email: r.email, origem: "IA" })} className="w-full bg-emerald-600 hover:bg-emerald-500">Adicionar</Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* LISTA DE OFERTAS (Híbrido) */}
              <div className="border-t border-slate-800 pt-4">
                <h3 className="text-sm font-bold text-slate-200 mb-3">Ofertas neste Orçamento</h3>
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-800 text-slate-400">
                    <tr>
                      <th className="p-2">Fornecedor</th><th className="p-2">Origem</th><th className="p-2">Qtd</th><th className="p-2">Valor Unit.</th><th className="p-2">Total</th><th className="p-2">Condições</th><th className="p-2"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {ofertas.map((of, i) => (
                      <tr key={i}>
                        <td className="p-2 text-slate-200 font-medium">{of.fornecedor_nome}</td>
                        <td className="p-2"><span className={of.origem === "IA" ? "text-purple-400" : "text-sky-400"}>{of.origem}</span></td>
                        <td className="p-2"><Input type="number" value={of.quantidade} onChange={e => { const n = [...ofertas]; n[i].quantidade = Number(e.target.value); setOfertas(n); }} className="h-7 w-16 bg-slate-950" /></td>
                        <td className="p-2"><Input type="number" value={of.valor_unitario} onChange={e => { const n = [...ofertas]; n[i].valor_unitario = Number(e.target.value); setOfertas(n); }} className="h-7 w-24 bg-slate-950" /></td>
                        <td className="p-2 text-emerald-400 font-bold">{brl(of.quantidade * of.valor_unitario)}</td>
                        <td className="p-2 text-slate-400">{of.prazo_entrega} / {of.forma_pagamento}</td>
                        <td className="p-2 text-right"><Button size="icon" variant="ghost" onClick={() => setOfertas(ofertas.filter((_, idx) => idx !== i))} className="text-rose-400 h-7 w-7"><Trash2 className="size-3"/></Button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="p-4 border-t border-slate-800 flex justify-end gap-3 bg-slate-800/30">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleSalvar} disabled={salvar.isPending} className="bg-sky-600 hover:bg-sky-500"><Save className="size-4 mr-2"/> Salvar Orçamento</Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE LISTAGEM DE FORNECEDOR MANUAL */}
      {modalFornecedorOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Escolha um Fornecedor</h2>
            <div className="max-h-60 overflow-y-auto space-y-2">
              {fornecedores.filter((f: any) => f.tipo_fornecedor_id === tipoForn || f.tipo_fornecedor === tipoForn).map((f: any) => (
                <div key={f.id} className="flex justify-between items-center bg-slate-800 p-3 rounded-lg">
                  <div>
                    <p className="text-sm font-bold text-slate-200">{f.nome}</p>
                    <p className="text-xs text-slate-400">{f.whatsapp} | {f.email}</p>
                  </div>
                  <Button size="sm" onClick={() => {
                    adicionarOferta({ fornecedor_id: f.id, fornecedor_nome: f.nome, valor_unitario: 0, whatsapp: f.whatsapp, email: f.email, origem: "Manual" });
                    setModalFornecedorOpen(false);
                  }} className="bg-emerald-600">Selecionar</Button>
                </div>
              ))}
            </div>
            <div className="flex justify-end mt-4"><Button variant="outline" onClick={() => setModalFornecedorOpen(false)}>Fechar</Button></div>
          </div>
        </div>
      )}
    </div>
  );
}
