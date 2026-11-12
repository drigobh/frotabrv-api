import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, Sparkles, X, Save, Edit, Trash2, MapPin, Phone, Image as ImageIcon, MessageCircle, Maximize2, Star, History, ArrowRight } from "lucide-react";
import { apiGet, apiPost, apiPut, apiPatch, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function Orcamentos() {
  const qc = useQueryClient();
  
  // Estados de Controle
  const [modalOpen, setModalOpen] = useState(false);
  const [editandoId, setEditandoId] = useState<string | null>(null);
  const [modalAprovacaoOpen, setModalAprovacaoOpen] = useState(false);
  const [orcamentoAprovacao, setOrcamentoAprovacao] = useState<any>(null);
  const [imagemExpandida, setImagemExpandida] = useState<string | null>(null);

  // Estados do Formulário
  const [produto, setProduto] = useState("");
  const [observacoes, setObservacoes] = useState("");
  const [ofertas, setOfertas] = useState<any[]>([]);

  // Estados da IA
  const [cidade, setCidade] = useState("");
  const [raioKm, setRaioKm] = useState("50");
  const [condicao, setCondicao] = useState("Novo");
  const [pesquisando, setPesquisando] = useState(false);
  const [resultadosIA, setResultadosIA] = useState<any[]>([]);

  // Estados do Fornecedor Cadastrado
  const [modalFornecedorOpen, setModalFornecedorOpen] = useState(false);
  const [tipoForn, setTipoForn] = useState("");
  const [buscaForn, setBuscaForn] = useState("");

  // Queries
  const { data: orcamentos = [] } = useQuery({ queryKey: ["orcamentos"], queryFn: () => apiGet<any[]>("/orcamentos") });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });

  // Filtra tipos que possuem fornecedores
  const tiposComFornecedores = tipos.filter((t: any) => 
    fornecedores.some((f: any) => f.tipo_fornecedor_id === t.id || f.tipo_fornecedor === t.id)
  );

  // Mutations
  const salvar = useMutation({
    mutationFn: (payload: any) => editandoId ? apiPut(`/orcamentos/${editandoId}`, payload) : apiPost("/orcamentos", payload),
    onSuccess: () => {
      toast.success(editandoId ? "Orçamento atualizado!" : "Orçamento criado!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["orcamentos"] });
    }
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/orcamentos/${id}`),
    onSuccess: () => {
      toast.success("Orçamento excluído!");
      qc.invalidateQueries({ queryKey: ["orcamentos"] });
    }
  });

  const escolherVencedor = useMutation({
    mutationFn: (payload: any) => apiPatch(`/orcamentos/${payload.id}/escolher-vencedor`, payload),
    onSuccess: () => {
      toast.success("Vencedor escolhido! Pedido de Compra gerado.");
      setModalAprovacaoOpen(false);
      qc.invalidateQueries({ queryKey: ["orcamentos"] });
    }
  });

  // Funções de Ação
  const abrirNovo = () => {
    setEditandoId(null);
    setProduto("");
    setObservacoes("");
    setOfertas([]);
    setResultadosIA([]);
    setCidade("");
    setModalOpen(true);
  };

  const abrirEdicao = (o: any) => {
    setEditandoId(o.id);
    setProduto(o.produto);
    setObservacoes(o.observacoes || "");
    setOfertas(o.ofertas);
    setModalOpen(true);
  };

  const pesquisarComIA = async () => {
    if (!produto || !cidade) return toast.error("Preencha o produto e a cidade.");
    setPesquisando(true);
    try {
      const res = await apiPost<any[]>("/orcamentos/ia-search", { produto, cidade, estado: "MG", raio_km: raioKm, condicao });
      setResultadosIA(res);
    } catch (e) { toast.error("Erro na IA"); } finally { setPesquisando(false); }
  };

  const adicionarOferta = async (base: any) => {
    if (!produto) return toast.error("Preencha o produto antes de adicionar fornecedores.");
    
    if (base.fornecedor_id) {
      try {
        const hist = await apiGet<any>(`/orcamentos/historico-preco?produto=${produto}&fornecedor_id=${base.fornecedor_id}`);
        if (hist.tem_historico && hist.preco !== base.valor_unitario) {
          const confirma = confirm(`Atenção: Último preço comprado foi ${brl(hist.preco)} por ${hist.usuario}. Continuar com ${brl(base.valor_unitario)}?`);
          if (!confirma) return;
        }
      } catch (e) {}
    }

    setOfertas([...ofertas, { ...base, quantidade: 1, valor_unitario: base.valor_unitario || 0, prazo_entrega: base.prazo_entrega || "5 dias", prazo_pagamento: base.prazo_pagamento || "30 dias", forma_pagamento: base.forma_pagamento || "Boleto" }]);
    toast.success("Fornecedor adicionado.");
  };

  const handleSalvar = () => {
    if (ofertas.length === 0) return toast.error("Adicione pelo menos um fornecedor.");
    salvar.mutate({ produto, observacoes, ofertas });
  };

  const filtradosManual = fornecedores.filter((f: any) => 
    (f.tipo_fornecedor_id === tipoForn || f.tipo_fornecedor === tipoForn) &&
    f.nome.toLowerCase().includes(buscaForn.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Compras"
        title="Orçamentos"
        description="Pesquise com IA ou use fornecedores cadastrados."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2"/> Novo Orçamento</Button>}
      />

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3">Nº Orçamento</th>
              <th className="px-3 py-3">Produto</th>
              <th className="px-3 py-3">Ofertas</th>
              <th className="px-3 py-3">Status</th>
              <th className="px-3 py-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {orcamentos.map((o: any) => (
              <tr key={o.id} className="hover:bg-slate-800/30">
                <td className="px-5 py-3 font-mono text-sky-400 font-bold">{o.numero}</td>
                <td className="px-3 py-3 text-slate-200">{o.produto}</td>
                <td className="px-3 py-3 text-slate-400">{o.ofertas.length} opções</td>
                <td className="px-3 py-3"><span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded text-xs font-bold">{o.status}</span></td>
                <td className="px-3 py-3 flex gap-1 justify-end">
                  <Button size="sm" variant="ghost" className="text-amber-400" onClick={() => abrirEdicao(o)} title="Editar"><Edit className="size-4" /></Button>
                  <Button size="sm" variant="ghost" className="text-emerald-400 border border-emerald-500/30" onClick={() => { setOrcamentoAprovacao(o); setModalAprovacaoOpen(true); }}>Aprovar</Button>
                  <Button size="sm" variant="ghost" className="text-rose-400" onClick={() => { if(confirm("Excluir orçamento?")) excluir.mutate(o.id); }} title="Excluir"><Trash2 className="size-4" /></Button>
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
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2"><Sparkles className="size-5 text-purple-400"/> {editandoId ? "Editar Orçamento" : "Novo Orçamento"}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><Label className="text-xs text-slate-400">Produto (Descritivo)</Label><Input value={produto} onChange={e => setProduto(e.target.value)} placeholder="Ex: farol volvo fh440" className="bg-slate-950" /></div>
                <div><Label className="text-xs text-slate-400">Observações</Label><Input value={observacoes} onChange={e => setObservacoes(e.target.value)} className="bg-slate-950" /></div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* MANUAL */}
                <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                  <h3 className="text-sm font-bold text-slate-200 mb-3">Fornecedor Cadastrado</h3>
                  <div className="flex gap-2">
                    <select value={tipoForn} onChange={(e) => setTipoForn(e.target.value)} className="flex-1 h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="">Escolha o Tipo</option>
                      {tiposComFornecedores.map((t: any) => <option key={t.id} value={t.id}>{t.nome}</option>)}
                    </select>
                    <Button onClick={() => setModalFornecedorOpen(true)} disabled={!tipoForn} className="bg-sky-600">Listar</Button>
                  </div>
                </div>

                {/* IA */}
                <div className="bg-purple-500/10 p-4 rounded-lg border border-purple-500/30">
                  <h3 className="text-sm font-bold text-purple-400 mb-3 flex items-center gap-2"><Sparkles className="size-4"/> Busca com IA</h3>
                  <div className="flex flex-col gap-2">
                    <Input placeholder="Cidade (ex: Contagem)" value={cidade} onChange={e => setCidade(e.target.value)} className="bg-slate-950" />
                    <div className="flex gap-2 items-end">
                      <div className="flex-1 flex gap-2">
                        <div className="flex flex-col gap-1 w-20">
                          <Label className="text-[10px] text-purple-400">Raio (km)</Label>
                          <Input type="number" value={raioKm} onChange={e => setRaioKm(e.target.value)} className="bg-slate-950 h-8 text-xs" />
                        </div>
                        <div className="flex flex-col gap-1">
                          <Label className="text-[10px] text-purple-400">Condição</Label>
                          <select value={condicao} onChange={e => setCondicao(e.target.value)} className="bg-slate-950 border border-slate-700 rounded-md text-xs text-slate-300 px-2 h-8">
                            <option value="Novo">Novo</option>
                            <option value="Usado">Usado</option>
                          </select>
                        </div>
                      </div>
                      <Button onClick={pesquisarComIA} disabled={pesquisando} className="bg-purple-600 h-8">{pesquisando ? "..." : "Buscar"}</Button>
                      <Button variant="outline" onClick={() => { setResultadosIA([]); setCidade(""); }} className="border-slate-700 text-slate-400 h-8 px-2"><X className="size-4"/></Button>
                    </div>
                  </div>
                </div>
              </div>

              {/* RESULTADOS IA */}
              {resultadosIA.length > 0 && (
                <div className="bg-slate-900 border border-purple-500/30 rounded-lg p-4">
                  <p className="text-xs font-bold text-purple-400 uppercase mb-3">Resultados da IA para "{produto}"</p>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {resultadosIA.map((r, i) => (
                      <div key={i} className="bg-slate-800/50 p-3 rounded border border-slate-700 text-xs flex gap-3">
                        <div className="relative w-16 h-16 rounded bg-slate-700 flex items-center justify-center shrink-0 overflow-hidden group cursor-pointer" onClick={() => setImagemExpandida(r.foto_url)}>
                          {r.foto_url ? <img src={r.foto_url} alt="Peça" className="w-full h-full object-cover group-hover:scale-110 transition-transform" /> : <ImageIcon className="size-6 text-slate-500" />}
                          <div className="absolute inset-0 bg-black/40 hidden group-hover:flex items-center justify-center"><Maximize2 className="size-4 text-white" /></div>
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start">
                            <p className="font-bold text-slate-200 line-clamp-1">{r.fornecedor_nome}</p>
                            <span className="text-amber-400 flex items-center text-[10px]"><Star className="size-3 fill-amber-400 mr-0.5"/>{r.classificacao}</span>
                          </div>
                          <p className="text-emerald-400 font-bold my-1">{brl(r.preco)}</p>
                          <div className="text-slate-400 space-y-0.5 mb-2 text-[10px]">
                            <p className="flex items-center gap-1 cursor-pointer hover:text-sky-400" onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(r.fornecedor_nome + " " + r.cidade)}`, "_blank")}>
                              <MapPin className="size-3"/> {r.bairro} - {r.distancia}km
                            </p>
                            <p className="flex items-center gap-1"><Phone className="size-3"/> {r.whatsapp.replace(/^55/, '')} <a href={`https://wa.me/${r.whatsapp}?text=Olá, gostaria de orçar o produto: ${produto}`} target="_blank" rel="noreferrer" className="text-emerald-500 hover:text-emerald-400 ml-1"><MessageCircle className="size-3" /></a></p>
                          </div>
                          <Button size="sm" onClick={() => adicionarOferta({ fornecedor_nome: r.fornecedor_nome, valor_unitario: r.preco, whatsapp: r.whatsapp, email: r.email, origem: "IA", prazo_entrega: r.prazo_entrega, prazo_pagamento: r.prazo_pagamento, forma_pagamento: r.forma_pagamento, classificacao: r.classificacao, compras_realizadas: r.compras_realizadas })} className="w-full bg-emerald-600 hover:bg-emerald-500 h-7 text-xs">Adicionar</Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* OFERTAS NO ORÇAMENTO */}
              <div className="border-t border-slate-800 pt-4">
                <h3 className="text-sm font-bold text-slate-200 mb-3">Ofertas neste Orçamento</h3>
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-800 text-slate-400">
                    <tr><th className="p-2">Fornecedor</th><th className="p-2">Origem</th><th className="p-2">Qtd</th><th className="p-2">Valor Unit.</th><th className="p-2">Total</th><th className="p-2">Condições</th><th className="p-2"></th></tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {ofertas.map((of, i) => (
                      <tr key={i}>
                        <td className="p-2 text-slate-200 font-medium">{of.fornecedor_nome}</td>
                        <td className="p-2"><span className={of.origem === "IA" ? "text-purple-400" : "text-sky-400"}>{of.origem}</span></td>
                        <td className="p-2"><Input type="number" value={of.quantidade} onChange={e => { const n = [...ofertas]; n[i].quantidade = Number(e.target.value); setOfertas(n); }} className="h-7 w-16 bg-slate-950" /></td>
                        <td className="p-2"><Input type="number" value={of.valor_unitario} onChange={e => { const n = [...ofertas]; n[i].valor_unitario = Number(e.target.value); setOfertas(n); }} className="h-7 w-24 bg-slate-950" /></td>
                        <td className="p-2 text-emerald-400 font-bold">{brl(of.quantidade * of.valor_unitario)}</td>
                        <td className="p-2 flex gap-1">
                          <Input value={of.prazo_entrega} onChange={e => { const n = [...ofertas]; n[i].prazo_entrega = e.target.value; setOfertas(n); }} className="h-7 w-16 text-xs bg-slate-950" placeholder="Prazo" />
                          <select value={of.forma_pagamento} onChange={e => { const n = [...ofertas]; n[i].forma_pagamento = e.target.value; setOfertas(n); }} className="h-7 w-20 text-xs bg-slate-950 border border-slate-700 rounded">
                            <option value="Boleto">Boleto</option>
                            <option value="Pix">Pix</option>
                            <option value="Cartão">Cartão</option>
                          </select>
                        </td>
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

      {/* MODAL DE LISTAGEM DE FORNECEDOR CADASTRADO */}
      {modalFornecedorOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg p-6 flex flex-col">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Escolha um Fornecedor</h2>
            <div className="relative mb-4"><Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" /><Input placeholder="Pesquisar fornecedor..." value={buscaForn} onChange={e => setBuscaForn(e.target.value)} className="pl-9 bg-slate-950" /></div>
            <div className="max-h-60 overflow-y-auto space-y-2">
              {filtradosManual.map((f: any) => (
                <div key={f.id} className="flex justify-between items-center bg-slate-800 p-3 rounded-lg">
                  <div><p className="text-sm font-bold text-slate-200">{f.nome}</p><p className="text-xs text-slate-400">{f.whatsapp} | {f.email}</p></div>
                  <Button size="sm" onClick={() => { adicionarOferta({ fornecedor_id: f.id, fornecedor_nome: f.nome, valor_unitario: 0, whatsapp: f.whatsapp, email: f.email, origem: "Manual" }); setModalFornecedorOpen(false); }} className="bg-emerald-600 hover:bg-emerald-500">Selecionar</Button>
                </div>
              ))}
              {filtradosManual.length === 0 && <p className="text-center text-slate-500 text-sm py-4">Nenhum fornecedor encontrado.</p>}
            </div>
            <div className="flex justify-end mt-4"><Button variant="outline" onClick={() => setModalFornecedorOpen(false)}>Fechar</Button></div>
          </div>
        </div>
      )}

      {/* MODAL DE ZOOM DA IMAGEM */}
      {imagemExpandida && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 p-4 cursor-pointer" onClick={() => setImagemExpandida(null)}>
          <img src={imagemExpandida} alt="Zoom" className="max-w-full max-h-full rounded-lg shadow-2xl" />
          <Button variant="ghost" size="icon" className="absolute top-4 right-4 text-white"><X className="size-8" /></Button>
        </div>
      )}

      {/* MODAL DE APROVAÇÃO */}
      {modalAprovacaoOpen && orcamentoAprovacao && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-800/30">
              <div>
                <h2 className="text-lg font-bold text-slate-100">Análise de Aprovação</h2>
                <p className="text-sm text-slate-400">Orçamento: {orcamentoAprovacao.numero} | Produto: {orcamentoAprovacao.produto}</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setModalAprovacaoOpen(false)}><X className="size-5" /></Button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              <div className="bg-sky-500/10 border border-sky-500/30 p-4 rounded-lg mb-6 flex gap-3 text-sm text-sky-200">
                <History className="size-5 shrink-0" />
                <p>Analise as ofertas abaixo. O sistema destaca o <b>Melhor Preço</b> e a <b>Melhor Classificação</b>. A escolha final é sua.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Filtrando ofertas duplicadas por fornecedor_nome + valor para não repetir visualmente */}
                {orcamentoAprovacao.ofertas.filter((v: any, i: number, a: any[]) => a.findIndex(x => x.fornecedor_nome === v.fornecedor_nome && x.valor_unitario === v.valor_unitario) === i).map((of: any, i: number) => {
                  const menorPreco = Math.min(...orcamentoAprovacao.ofertas.map((x: any) => x.valor_unitario));
                  const isMenorPreco = of.valor_unitario === menorPreco;

                  return (
                    <div key={i} className={`p-4 rounded-xl border-2 flex flex-col ${isMenorPreco ? 'border-emerald-500 bg-emerald-500/5' : 'border-slate-700 bg-slate-800/50'}`}>
                      {isMenorPreco && <span className="text-[10px] font-bold uppercase text-emerald-400 mb-2 flex items-center gap-1"><Star className="size-3 fill-emerald-400"/> Melhor Preço</span>}
                      <p className="font-bold text-slate-100 text-lg line-clamp-1">{of.fornecedor_nome}</p>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-amber-400 flex items-center text-xs"><Star className="size-3 fill-amber-400 mr-1"/>{of.classificacao || 'N/A'}</span>
                        <span className="text-slate-400 text-xs">({of.compras_realizadas || 0} compras)</span>
                      </div>
                      <div className="space-y-1 text-xs text-slate-300 mb-4 flex-1">
                        <p className="flex justify-between"><span className="text-slate-500">Valor Unit.:</span> <span className="font-bold text-slate-100">{brl(of.valor_unitario)}</span></p>
                        <p className="flex justify-between"><span className="text-slate-500">Qtd:</span> <span>{of.quantidade}</span></p>
                        <p className="flex justify-between"><span className="text-slate-500">Total:</span> <span className="font-bold text-sky-400">{brl(of.valor_unitario * of.quantidade)}</span></p>
                        <p className="flex justify-between"><span className="text-slate-500">Entrega:</span> <span>{of.prazo_entrega}</span></p>
                        <p className="flex justify-between"><span className="text-slate-500">Pagamento:</span> <span>{of.prazo_pagamento} - {of.forma_pagamento}</span></p>
                        <p className="flex justify-between"><span className="text-slate-500">Origem:</span> <span className={of.origem === "IA" ? "text-purple-400" : "text-slate-400"}>{of.origem}</span></p>
                      </div>
                      <Button onClick={() => {
                        escolherVencedor.mutate({ id: orcamentoAprovacao.id, fornecedor_id: of.fornecedor_id, fornecedor_nome: of.fornecedor_nome });
                      }} className="w-full bg-sky-600 hover:bg-sky-500">Aprovar este Fornecedor</Button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
