import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, Sparkles, X, Save, FileText, ArrowRight } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";

export default function Orcamentos() {
  const qc = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [busca, setBusca] = useState("");
  
  // Estados do Formulário
  const [produto, setProduto] = useState("");
  const [quantidade, setQuantidade] = useState("1");
  const [cidade, setCidade] = useState("");
  const [estado, setEstado] = useState("");
  const [fornecedorNome, setFornecedorNome] = useState("");
  const [valorUnit, setValorUnit] = useState("0");

  // Estados da IA
  const [pesquisando, setPesquisando] = useState(false);
  const [resultadosIA, setResultadosIA] = useState<any[]>([]);
  const [origem, setOrigem] = useState<"Manual" | "IA">("Manual");

  const { data: orcamentos = [], isLoading } = useQuery({ 
    queryKey: ["orcamentos"], 
    queryFn: () => apiGet<any[]>("/orcamentos"),
    staleTime: 1000 * 60 * 5 // Cache de 5 minutos para ficar mais rápido
  });

  const { data: fornecedores = [] } = useQuery({ 
    queryKey: ["fornecedores"], 
    queryFn: () => apiGet<any[]>("/fornecedores"),
    staleTime: 1000 * 60 * 5
  });

  const salvar = useMutation({
    mutationFn: (payload: any) => apiPost("/orcamentos", payload),
    onSuccess: () => {
      toast.success("Orçamento criado com sucesso!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["orcamentos"] });
    }
  });

  const pesquisarComIA = async () => {
    if (!produto || !cidade || !estado) return toast.error("Preencha o produto, cidade e estado.");
    setPesquisando(true);
    try {
      const res = await apiPost<any[]>("/orcamentos/ia-search", { produto, cidade, estado });
      setResultadosIA(res);
      toast.success("Fornecedores encontrados pela IA!");
    } catch (e) {
      toast.error("Erro na busca de IA.");
    } finally {
      setPesquisando(false);
    }
  };

  const usarFornecedorIA = (res: any) => {
    setFornecedorNome(res.fornecedor);
    setValorUnit(res.preco.toString());
    setOrigem("IA");
    setResultadosIA([]);
    toast.info(`Fornecedor ${res.fornecedor} selecionado.`);
  };

  const handleSalvar = () => {
    if (!fornecedorNome || !produto || !quantidade || !valorUnit) return toast.error("Preencha todos os campos.");
    salvar.mutate({
      fornecedor_nome_ia: origem === "IA" ? fornecedorNome : null,
      itens: [{ produto, quantidade: parseFloat(quantidade), valor_unitario: parseFloat(valorUnit) }],
      observacoes: `Orçamento via ${origem}`,
      origem: origem
    });
  };

  const filtrados = orcamentos.filter((o: any) => 
    (o.numero || "").toLowerCase().includes(busca.toLowerCase()) ||
    (o.itens?.[0]?.produto || "").toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Compras"
        title="Orçamentos"
        description="Pesquise preços com IA e gere orçamentos antes de abrir um pedido de compra."
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder="Buscar orçamento..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-9 h-9 w-64" />
            </div>
            <Button onClick={() => setModalOpen(true)} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2"/> Novo Orçamento</Button>
          </div>
        }
      />

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3 font-medium">Nº Orçamento</th>
              <th className="px-3 py-3 font-medium">Data</th>
              <th className="px-3 py-3 font-medium">Produto</th>
              <th className="px-3 py-3 font-medium">Fornecedor</th>
              <th className="px-3 py-3 font-medium">Valor Total</th>
              <th className="px-3 py-3 font-medium">Origem</th>
              <th className="px-3 py-3 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {isLoading ? (
              <tr><td colSpan={7} className="p-8 text-center text-slate-400">Carregando...</td></tr>
            ) : filtrados.length === 0 ? (
              <tr><td colSpan={7} className="p-8 text-center text-slate-400">Nenhum orçamento encontrado.</td></tr>
            ) : (
              filtrados.map((o: any) => (
                <tr key={o.id} className="hover:bg-slate-800/30">
                  <td className="px-5 py-3 font-mono text-sky-400 font-bold">{o.numero || o.id.slice(0, 8)}</td>
                  <td className="px-3 py-3 text-slate-300 text-xs">{new Date(o.data_criacao).toLocaleString("pt-BR")}</td>
                  <td className="px-3 py-3 text-slate-200">{o.itens?.[0]?.produto}</td>
                  <td className="px-3 py-3 text-slate-200">{o.fornecedor_nome_ia || fornecedores.find((f: any) => f.id === o.fornecedor_id)?.nome || "—"}</td>
                  <td className="px-3 py-3 font-mono font-bold text-slate-200">{brl((o.itens?.[0]?.valor_unitario || 0) * (o.itens?.[0]?.quantidade || 1))}</td>
                  <td className="px-3 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${o.origem === "IA" ? "bg-purple-500/20 text-purple-400" : "bg-slate-500/20 text-slate-400"}`}>
                      {o.origem}
                    </span>
                  </td>
                  <td className="px-3 py-3 flex gap-1">
                    <Button size="sm" variant="ghost" className="text-emerald-400 hover:bg-emerald-500/10" title="Transformar em Pedido"><ArrowRight className="size-4" /></Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* MODAL DE NOVO ORÇAMENTO */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-800/30">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2"><Sparkles className="size-5 text-purple-400"/> Novo Orçamento</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div><Label className="text-xs text-slate-400">Produto</Label><Input value={produto} onChange={e => setProduto(e.target.value)} placeholder="Ex: Óleo 15w40" className="bg-slate-950" /></div>
                <div><Label className="text-xs text-slate-400">Cidade</Label><Input value={cidade} onChange={e => setCidade(e.target.value)} placeholder="Ex: São Paulo" className="bg-slate-950" /></div>
                <div><Label className="text-xs text-slate-400">Estado (UF)</Label><Input value={estado} onChange={e => setEstado(e.target.value)} placeholder="Ex: SP" maxLength={2} className="bg-slate-950" /></div>
              </div>
              
              <Button onClick={pesquisarComIA} disabled={pesquisando} className="w-full bg-purple-600 hover:bg-purple-500">
                <Sparkles className="size-4 mr-2" /> {pesquisando ? "Pesquisando preços..." : "Pesquisar Fornecedores com IA"}
              </Button>

              {/* RESULTADOS DA IA */}
              {resultadosIA.length > 0 && (
                <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                  <p className="text-xs font-bold text-purple-400 uppercase mb-3">Fornecedores encontrados pela IA</p>
                  <div className="space-y-2">
                    {resultadosIA.map((r, i) => (
                      <div key={i} className="flex justify-between items-center bg-slate-900/50 p-3 rounded border border-slate-700">
                        <div>
                          <p className="text-sm font-bold text-slate-200">{r.fornecedor}</p>
                          <p className="text-xs text-slate-400">{r.cidade} | CNPJ: {r.cnpj}</p>
                        </div>
                        <div className="flex items-center gap-4">
                          <p className="font-mono font-bold text-emerald-400">{brl(r.preco)}</p>
                          <Button size="sm" onClick={() => usarFornecedorIA(r)} className="bg-emerald-600 hover:bg-emerald-500">Usar</Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="border-t border-slate-800 pt-4">
                <h3 className="text-sm font-bold text-slate-200 mb-4">Dados do Orçamento</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div><Label className="text-xs text-slate-400">Fornecedor Selecionado</Label><Input value={fornecedorNome} readOnly placeholder="Selecione na IA ou digite..." className="bg-slate-950" /></div>
                  <div><Label className="text-xs text-slate-400">Qtd</Label><Input type="number" value={quantidade} onChange={e => setQuantidade(e.target.value)} className="bg-slate-950" /></div>
                  <div><Label className="text-xs text-slate-400">Valor Unitário</Label><Input type="number" value={valorUnit} onChange={e => setValorUnit(e.target.value)} className="bg-slate-950" /></div>
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-slate-800 flex justify-end gap-3 bg-slate-800/30">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleSalvar} disabled={salvar.isPending} className="bg-sky-600 hover:bg-sky-500"><Save className="size-4 mr-2"/> Salvar Orçamento</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
