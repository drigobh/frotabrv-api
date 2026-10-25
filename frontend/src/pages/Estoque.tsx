import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Package, Plus, Pencil, Trash2, AlertTriangle, CheckCircle2, Search, MapPin, Info, Star, Barcode, Box, ArrowDownRight, ClipboardList, RefreshCw, Printer, FileSpreadsheet, Eye } from "lucide-react";
import { toast } from "sonner";
import * as XLSX from "xlsx";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { brl } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { FieldSelect } from "@/components/common/FieldSelect";
import { useVeiculos, useCarretas } from "@/hooks/useCadastros";

export default function Estoque() {
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("catalogo");
  
  // Estados da Peça
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [busca, setBusca] = useState("");
  const [form, setForm] = useState({ 
    nome: "", codigo: "", codigo_barras: "", corredor: "", prateleira: "", caixa: "", 
    quantidade_estoque: "", estoque_minimo: "5", fornecedor_atual_id: "", ativo: true 
  });
  const [listaFornecedores, setListaFornecedores] = useState<{ fornecedor_id: string, preco_atual: string, historico: number[] }[]>([]);

  // Estados de Baixa de Estoque (Saída)
  const [openMov, setOpenMov] = useState(false);
  const [movForm, setMovForm] = useState({ peca_id: "", fornecedor_id: "", destino_tipo: "veiculo", veiculo_id: "", carreta_id: "", quantidade: "", motivo: "", observacao: "" });

  // Estados de Inventário
  const [openInv, setOpenInv] = useState(false);
  const [invContagens, setInvContagens] = useState<Record<string, string>>({});
  const [viewInv, setViewInv] = useState<any | null>(null);
  const [excluirInvId, setExcluirInvId] = useState<string | null>(null);
  const [openInvConfirm, setOpenInvConfirm] = useState(false);

  // Queries
  const q = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas"), staleTime: 0, refetchOnMount: true });
  const fornQ = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const veicQ = useVeiculos();
  const carrQ = useCarretas();
  const movQ = useQuery({ queryKey: ["movimentacoes"], queryFn: () => apiGet<any[]>("/estoque/movimentacoes"), enabled: activeTab === "movimentacoes" });
  const invQ = useQuery({ queryKey: ["inventarios"], queryFn: () => apiGet<any[]>("/estoque/inventarios"), enabled: activeTab === "inventarios" });
  
  const rows = q.data ?? [];
  const fornecedores = fornQ.data ?? [];
  const veiculos = veicQ.data ?? [];
  const carretas = carrQ.data ?? [];
  const movimentacoes = movQ.data ?? [];
  const inventarios = invQ.data ?? [];

  const rowsFiltradas = useMemo(() => {
    return rows.filter(r => r.nome.toLowerCase().includes(busca.toLowerCase()) || (r.codigo && r.codigo.toLowerCase().includes(busca.toLowerCase())) || (r.codigo_barras && r.codigo_barras.toLowerCase().includes(busca.toLowerCase())));
  }, [rows, busca]);

  // Mutations
  const salvar = useMutation({
    mutationFn: () => {
      const payload = { 
        ...form, quantidade_estoque: Number(form.quantidade_estoque) || 0, estoque_minimo: Number(form.estoque_minimo) || 0,
        fornecedores_precos: listaFornecedores.map(f => ({ fornecedor_id: f.fornecedor_id, preco_atual: Number(f.preco_atual.replace(",", ".")) || 0, historico: f.historico }))
      };
      if (editingId) return apiPut(`/pecas/${editingId}`, payload);
      return apiPost("/pecas", payload);
    },
    onSuccess: () => { toast.success("Peça salva!"); setOpen(false); setEditingId(null); qc.invalidateQueries({ queryKey: ["pecas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pecas/${id}`),
    onSuccess: () => { toast.success("Peça excluída"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pecas"] }); },
  });

  const salvarMov = useMutation({
    mutationFn: () => apiPost("/estoque/movimentacoes", { 
      peca_id: movForm.peca_id, fornecedor_id: movForm.fornecedor_id,
      veiculo_id: movForm.destino_tipo === "veiculo" ? movForm.veiculo_id : null,
      carreta_id: movForm.destino_tipo === "carreta" ? movForm.carreta_id : null,
      quantidade: Number(movForm.quantidade), motivo: movForm.motivo, observacao: movForm.observacao
    }),
    onSuccess: () => { 
      toast.success("Baixa realizada com sucesso!"); setOpenMov(false); 
      setMovForm({ peca_id: "", fornecedor_id: "", destino_tipo: "veiculo", veiculo_id: "", carreta_id: "", quantidade: "", motivo: "", observacao: "" });
      qc.invalidateQueries({ queryKey: ["pecas"] }); qc.invalidateQueries({ queryKey: ["movimentacoes"] }); 
    },
    onError: (e: any) => toast.error(e.message || "Erro na baixa"),
  });

  const salvarInv = useMutation({
    mutationFn: () => {
      const itens = Object.entries(invContagens).filter(([_, qtd]) => qtd !== "").map(([id, qtd]) => {
        const p = rows.find((r:any) => r.id === id);
        return { peca_id: id, peca_nome: p.nome, qtd_anterior: p.quantidade_estoque, qtd_fisica: Number(qtd) };
      });
      return apiPost("/estoque/inventario", { itens });
    },
    onSuccess: (data: any) => { 
      toast.success(`Inventário concluído! ${data.ajustes} peças ajustadas.`); 
      setOpenInv(false); setInvContagens({}); 
      qc.invalidateQueries({ queryKey: ["pecas"] }); qc.invalidateQueries({ queryKey: ["movimentacoes"] }); qc.invalidateQueries({ queryKey: ["inventarios"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro no inventário"),
  });

  const reverterInv = useMutation({
    mutationFn: (id: string) => apiPost(`/estoque/inventarios/${id}/reverter`),
    onSuccess: () => { toast.success("Inventário revertido e estoque restaurado!"); qc.invalidateQueries({ queryKey: ["pecas"] }); qc.invalidateQueries({ queryKey: ["movimentacoes"] }); qc.invalidateQueries({ queryKey: ["inventarios"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao reverter"),
  });

  const excluirInv = useMutation({
    mutationFn: (id: string) => apiDelete(`/estoque/inventarios/${id}`),
    onSuccess: () => { toast.success("Histórico de inventário excluído"); setExcluirInvId(null); qc.invalidateQueries({ queryKey: ["inventarios"] }); },
  });

  // Exportações de Inventário
  const exportarExcel = (inv: any) => {
    const dados = inv.itens.map((i: any) => ({
      "Peça": i.peca_nome, "Qtd Anterior": i.qtd_anterior, "Qtd Contada": i.qtd_fisica, "Diferença": i.qtd_fisica - i.qtd_anterior
    }));
    const ws = XLSX.utils.json_to_sheet(dados);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Inventario");
    XLSX.writeFile(wb, `Inventario_${inv.data_hora.split('T')[0]}.xlsx`);
  };

  const imprimirPDF = (inv: any) => {
    const win = window.open('', '_blank');
    if (!win) return;
    const rowsHtml = inv.itens.map((i: any) => `
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">${i.peca_nome}</td>
        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">${i.qtd_anterior}</td>
        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold;">${i.qtd_fisica}</td>
        <td style="padding: 8px; border: 1px solid #ddd; text-align: center; color: ${i.qtd_fisica - i.qtd_anterior < 0 ? 'red' : 'green'};">${i.qtd_fisica - i.qtd_anterior}</td>
      </tr>
    `).join('');

    win.document.write(`
      <html><head><title>Inventário</title>
      <style>body { font-family: sans-serif; margin: 40px; } table { width: 100%; border-collapse: collapse; margin-top: 20px; } th { background: #f4f4f4; padding: 8px; border: 1px solid #ddd; text-align: left; }</style>
      </head><body>
      <h2>Relatório de Inventário - Bravus</h2>
      <p>Data: ${new Date(inv.data_hora).toLocaleString('pt-BR')} | Responsável: ${inv.usuario_nome}</p>
      <table><thead><tr><th>Peça</th><th style="text-align:center;">Qtd Sistema</th><th style="text-align:center;">Qtd Física</th><th style="text-align:center;">Diferença</th></tr></thead>
      <tbody>${rowsHtml}</tbody></table>
      <script>window.onload = () => { window.print(); window.close(); }</script>
      </body></html>
    `);
    win.document.close();
  };

  const abrirNovo = () => { 
    setEditingId(null); 
    setForm({ nome: "", codigo: "", codigo_barras: "", corredor: "", prateleira: "", caixa: "", quantidade_estoque: "", estoque_minimo: "5", fornecedor_atual_id: "", ativo: true }); 
    setListaFornecedores([]); setOpen(true); 
  };

  const abrirEdicao = (r: any) => { 
    setEditingId(r.id); 
    setForm({ 
      nome: r.nome, codigo: r.codigo || "", codigo_barras: r.codigo_barras || "", corredor: r.corredor || "", prateleira: r.prateleira || "", caixa: r.caixa || "",
      quantidade_estoque: String(r.quantidade_estoque), estoque_minimo: String(r.estoque_minimo), fornecedor_atual_id: r.fornecedor_atual_id || "", ativo: r.ativo 
    }); 
    setListaFornecedores((r.fornecedores_precos || []).map((f: any) => ({ fornecedor_id: f.fornecedor_id, preco_atual: String(f.preco_atual), historico: f.historico || [] })));
    setOpen(true); 
  };

  const abrirMovimentacao = (peca_id: string = "") => {
    setMovForm({ peca_id, fornecedor_id: "", destino_tipo: "veiculo", veiculo_id: "", carreta_id: "", quantidade: "", motivo: "", observacao: "" });
    setOpenMov(true);
  };

  const adicionarFornecedor = () => setListaFornecedores([...listaFornecedores, { fornecedor_id: "", preco_atual: "", historico: [] }]);
  const removerFornecedor = (idx: number) => setListaFornecedores(listaFornecedores.filter((_, i) => i !== idx));
  
  const atualizarPreco = (idx: number, novoPreco: string) => { const nova = [...listaFornecedores]; nova[idx].preco_atual = novoPreco; setListaFornecedores(nova); };
  const registrarPreco = (idx: number) => {
    const nova = [...listaFornecedores];
    const precoNum = Number(nova[idx].preco_atual.replace(",", "."));
    if (isNaN(precoNum) || precoNum <= 0) { toast.error("Preço inválido"); return; }
    nova[idx].historico = [precoNum, ...nova[idx].historico].slice(0, 3);
    nova[idx].preco_atual = ""; setListaFornecedores(nova);
    toast.success("Preço registrado no histórico!");
  };

  const totalItens = rows.length;
  const itensBaixos = rows.filter(r => r.quantidade_estoque <= r.estoque_minimo).length;
  const valorTotal = rows.reduce((acc, r) => {
    if (!r.fornecedor_atual_id) return acc;
    const fp = (r.fornecedores_precos || []).find((f: any) => f.fornecedor_id === r.fornecedor_atual_id);
    return acc + ((fp ? fp.preco_atual : 0) * r.quantidade_estoque);
  }, 0);
  const estadosOrigem = new Set(rows.flatMap(r => (r.fornecedores_precos || []).map((fp: any) => fornecedores.find((x: any) => x.id === fp.fornecedor_id)?.estado)).filter(Boolean)).size;

  // Filtra os fornecedores que vendem a peça selecionada na baixa
  const pecaSelecionada = rows.find((r:any) => r.id === movForm.peca_id);
  const fornecedoresDaPeca = pecaSelecionada ? (pecaSelecionada.fornecedores_precos || []).map((fp:any) => {
    const f = fornecedores.find((x:any) => x.id === fp.fornecedor_id);
    return f ? { value: f.id, label: `${f.nome} (${f.avaliacao || 0}★)` } : null;
  }).filter(Boolean) : [];

  return (
    <div>
      <PageHeader 
        eyebrow="Operação" title="Estoque de Peças" description="Controle de almoxarifado." 
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => setOpenInv(true)}><ClipboardList className="size-4 mr-2" /> Inventário</Button>
            <Button variant="outline" onClick={() => abrirMovimentacao()}><ArrowDownRight className="size-4 mr-2" /> Baixa de Estoque</Button>
            <Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Entrada / Cadastro de Peça</Button>
          </div>
        } 
      />

      {/* Abas */}
      <div className="flex gap-4 mb-4 border-b border-slate-800">
        <button onClick={() => setActiveTab("catalogo")} className={`pb-2 text-sm font-medium transition-colors ${activeTab === "catalogo" ? "text-sky-400 border-b-2 border-sky-400" : "text-slate-400 hover:text-slate-200"}`}>Catálogo de Peças</button>
        <button onClick={() => setActiveTab("movimentacoes")} className={`pb-2 text-sm font-medium transition-colors ${activeTab === "movimentacoes" ? "text-sky-400 border-b-2 border-sky-400" : "text-slate-400 hover:text-slate-200"}`}>Histórico de Saídas</button>
        <button onClick={() => setActiveTab("inventarios")} className={`pb-2 text-sm font-medium transition-colors ${activeTab === "inventarios" ? "text-sky-400 border-b-2 border-sky-400" : "text-slate-400 hover:text-slate-200"}`}>Histórico de Inventários</button>
      </div>

      {activeTab === "catalogo" && (
        <>
          <div className="mb-4 grid gap-2 sm:grid-cols-2 md:grid-cols-4">
            <div className="glass rounded-lg p-3 flex items-center justify-between h-[70px]">
              <div><p className="text-[11px] text-slate-500 font-medium">Total de Itens</p><p className="text-xl font-bold text-slate-100">{totalItens}</p></div>
              <div className="size-8 rounded bg-sky-500/10 flex items-center justify-center"><Package className="size-4 text-sky-400" /></div>
            </div>
            <div className="glass rounded-lg p-3 flex items-center justify-between h-[70px]">
              <div><p className="text-[11px] text-slate-500 font-medium">Valor do Estoque</p><p className="text-xl font-bold text-amber-400">{brl(valorTotal)}</p></div>
              <div className="size-8 rounded bg-amber-500/10 flex items-center justify-center font-bold text-amber-400 text-xs">R$</div>
            </div>
            <div className="glass rounded-lg p-3 flex items-center justify-between h-[70px]">
              <div><p className="text-[11px] text-slate-500 font-medium">Estoque Baixo</p><p className="text-xl font-bold text-red-400">{itensBaixos}</p></div>
              <div className="size-8 rounded bg-red-500/10 flex items-center justify-center"><AlertTriangle className="size-4 text-red-400" /></div>
            </div>
            <div className="glass rounded-lg p-3 flex items-center justify-between h-[70px]">
              <div><p className="text-[11px] text-slate-500 font-medium">Estados de Origem</p><p className="text-xl font-bold text-purple-400">{estadosOrigem} UF</p></div>
              <div className="size-8 rounded bg-purple-500/10 flex items-center justify-center"><MapPin className="size-4 text-purple-400" /></div>
            </div>
          </div>

          <div className="mb-3">
            <div className="relative w-72">
              <Search className="absolute left-2 top-2.5 size-4 text-slate-500" />
              <Input placeholder="Buscar peça..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-8 h-9 text-sm" />
            </div>
          </div>

          <div className="glass overflow-hidden rounded-2xl">
            <Table>
              <TableHeader>
                <TableRow className="border-slate-800 hover:bg-transparent">
                  <TableHead className="text-xs uppercase text-slate-500">Peça / Localização</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Atual</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Mínima</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500 text-right">Preço (Atual)</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500 text-right">Valor Total</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500 text-center">Status</TableHead>
                  <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rowsFiltradas.length === 0 && <TableRow><TableCell colSpan={7} className="py-10 text-center text-slate-500">Nenhuma peça encontrada.</TableCell></TableRow>}
                {rowsFiltradas.map((r) => {
                  const estoqueBaixo = r.quantidade_estoque <= r.estoque_minimo;
                  const fornAtual = fornecedores.find((f: any) => f.id === r.fornecedor_atual_id);
                  const fpAtual = (r.fornecedores_precos || []).find((f: any) => f.fornecedor_id === r.fornecedor_atual_id);
                  const precoAtual = fpAtual ? fpAtual.preco_atual : 0;
                  
                  const temLocalizacao = r.corredor || r.prateleira || r.caixa;
                  const localizacaoStr = [r.corredor && `C: ${r.corredor}`, r.prateleira && `P: ${r.prateleira}`, r.caixa && `Cx: ${r.caixa}`].filter(Boolean).join(" | ");
                  
                  return (
                    <TableRow key={r.id} className="border-slate-800/70">
                      <TableCell className="font-medium text-slate-200">
                        <div>{r.nome}</div>
                        <div className="text-slate-500 font-mono text-xs flex gap-2">
                          {r.codigo && <span>{r.codigo}</span>}
                          {r.codigo_barras && <span className="flex items-center gap-0.5"><Barcode className="size-3"/> {r.codigo_barras}</span>}
                        </div>
                        {temLocalizacao && <div className="text-[10px] text-amber-400 mt-1 flex items-center gap-1"><Box className="size-3" /> {localizacaoStr}</div>}
                        {fornAtual ? <div className="text-[10px] text-emerald-400 mt-1">Estoque de: {fornAtual.nome}</div> : <div className="text-[10px] text-slate-500 mt-1">Fornecedor não informado</div>}
                      </TableCell>
                      <TableCell className={`text-center font-bold ${estoqueBaixo ? 'text-red-400' : 'text-emerald-400'}`}>{r.quantidade_estoque}</TableCell>
                      <TableCell className="text-center text-slate-400">{r.estoque_minimo}</TableCell>
                      <TableCell className="text-right text-slate-300">{brl(precoAtual)}</TableCell>
                      <TableCell className="text-right font-medium text-slate-200">{brl(precoAtual * r.quantidade_estoque)}</TableCell>
                      <TableCell className="text-center">
                        {estoqueBaixo ? <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400"><AlertTriangle className="size-3" /> Baixo</span> : <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400"><CheckCircle2 className="size-3" /> OK</span>}
                      </TableCell>
                      <TableCell className="text-center">
                        <div className="flex gap-1 justify-center">
                          <Button size="icon-sm" variant="ghost" className="text-emerald-400" onClick={() => abrirMovimentacao(r.id)} title="Baixa de Estoque"><ArrowDownRight className="size-4" /></Button>
                          <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Cadastrado por: ${r.created_by_name || 'Sistema'}`}><Info className="size-4 text-slate-400" /></Button>
                          <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                          <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </>
      )}

      {activeTab === "movimentacoes" && (
        <div className="glass overflow-hidden rounded-2xl">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-800 hover:bg-transparent">
                <TableHead className="text-xs uppercase text-slate-500">Data/Hora</TableHead>
                <TableHead className="text-xs uppercase text-slate-500">Peça</TableHead>
                <TableHead className="text-xs uppercase text-slate-500">Fornecedor</TableHead>
                <TableHead className="text-xs uppercase text-slate-500">Destino</TableHead>
                <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd</TableHead>
                <TableHead className="text-xs uppercase text-slate-500">Motivo</TableHead>
                <TableHead className="text-xs uppercase text-slate-500">Usuário</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {movimentacoes.length === 0 && <TableRow><TableCell colSpan={7} className="py-10 text-center text-slate-500">Nenhuma baixa registrada.</TableCell></TableRow>}
              {movimentacoes.map((m) => (
                <TableRow key={m.id} className="border-slate-800/70">
                  <TableCell className="text-xs text-slate-400 font-mono">{m.data_hora.replace("T", " ").substring(0, 16)}</TableCell>
                  <TableCell className="font-medium text-slate-200">{m.peca_nome}</TableCell>
                  <TableCell className="text-xs text-slate-400">{m.fornecedor_nome || "—"}</TableCell>
                  <TableCell className="text-xs text-sky-400">{m.destino_nome || "—"}</TableCell>
                  <TableCell className="text-center font-bold text-red-400">-{m.quantidade}</TableCell>
                  <TableCell className="text-xs text-slate-300">{m.motivo} {m.observacao && <span className="text-[10px] text-slate-500">({m.observacao})</span>}</TableCell>
                  <TableCell className="text-xs text-slate-400">{m.usuario_nome}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {activeTab === "inventarios" && (
        <div className="glass overflow-hidden rounded-2xl">
          <Table>
            <TableHeader>
              <TableRow className="border-slate-800 hover:bg-transparent">
                <TableHead className="text-xs uppercase text-slate-500">Data/Hora</TableHead>
                <TableHead className="text-xs uppercase text-slate-500">Responsável</TableHead>
                <TableHead className="text-xs uppercase text-slate-500 text-center">Total de Ajustes</TableHead>
                <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {inventarios.length === 0 && <TableRow><TableCell colSpan={4} className="py-10 text-center text-slate-500">Nenhum inventário registrado.</TableCell></TableRow>}
              {inventarios.map((inv) => (
                <TableRow key={inv.id} className="border-slate-800/70">
                  <TableCell className="text-xs text-slate-400 font-mono">{inv.data_hora.replace("T", " ").substring(0, 16)}</TableCell>
                  <TableCell className="font-medium text-slate-200">{inv.usuario_nome}</TableCell>
                  <TableCell className="text-center font-bold text-amber-400">{inv.total_ajustes} itens</TableCell>
                  <TableCell className="text-center">
                    <div className="flex gap-1 justify-center">
                      <Button size="icon-sm" variant="ghost" onClick={() => setViewInv(inv)} title="Visualizar/Imprimir"><Eye className="size-4 text-sky-400" /></Button>
                      <Button size="icon-sm" variant="ghost" className="text-amber-400" onClick={() => { if(confirm("Deseja reverter este inventário? O estoque voltará ao estado anterior.")) reverterInv.mutate(inv.id); }} title="Reverter Inventário"><RefreshCw className="size-4" /></Button>
                      <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirInvId(inv.id)} title="Excluir Histórico"><Trash2 className="size-4" /></Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Modal de Cadastro de Peça (Mantido do script anterior, omitido aqui por brevidade) */}
      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Package className="size-5 text-sky-400" /> {editingId ? "Editar Peça" : "Entrada / Cadastro de Peça"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-4" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 md:col-span-1 grid gap-1.5"><Label>Nome da Peça *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} required /></div>
            <div className="col-span-2 md:col-span-1 grid gap-1.5"><Label>Código Interno</Label><Input value={form.codigo} onChange={(e) => setForm(s => ({ ...s, codigo: e.target.value }))} /></div>
            <div className="col-span-2 md:col-span-1 grid gap-1.5"><Label>Código de Barras</Label><Input value={form.codigo_barras} onChange={(e) => setForm(s => ({ ...s, codigo_barras: e.target.value }))} placeholder="EAN-13..." /></div>
            <div className="grid gap-1.5"><Label>Qtd. a Adicionar</Label><Input type="number" value={form.quantidade_estoque} onChange={(e) => setForm(s => ({ ...s, quantidade_estoque: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Estoque Mínimo</Label><Input type="number" value={form.estoque_minimo} onChange={(e) => setForm(s => ({ ...s, estoque_minimo: e.target.value }))} /></div>
            <div className="col-span-2 grid grid-cols-3 gap-2 bg-slate-900/30 p-3 rounded-lg border border-slate-800">
              <div className="grid gap-1.5"><Label>Corredor</Label><Input value={form.corredor} onChange={(e) => setForm(s => ({ ...s, corredor: e.target.value }))} /></div>
              <div className="grid gap-1.5"><Label>Prateleira</Label><Input value={form.prateleira} onChange={(e) => setForm(s => ({ ...s, prateleira: e.target.value }))} /></div>
              <div className="grid gap-1.5"><Label>Caixa</Label><Input value={form.caixa} onChange={(e) => setForm(s => ({ ...s, caixa: e.target.value }))} /></div>
            </div>
            <div className="col-span-2 bg-sky-950/30 p-3 rounded-lg border border-sky-900/50">
              <Label className="text-sky-400 font-semibold mb-2 block">Fornecedor da Compra Atual</Label>
              <FieldSelect value={form.fornecedor_atual_id} onChange={(v) => setForm(s => ({ ...s, fornecedor_atual_id: v }))} options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} placeholder="Selecione" />
            </div>
            <div className="col-span-2 border-t border-slate-800 pt-3 mt-2">
              <div className="flex justify-between items-center mb-3">
                <Label className="text-sm font-semibold text-slate-200">Catálogo de Fornecedores e Cotações</Label>
                <Button type="button" variant="outline" size="sm" onClick={adicionarFornecedor}><Plus className="size-3 mr-1" /> Adicionar Cotação</Button>
              </div>
              {listaFornecedores.map((lf, idx) => (
                <div key={idx} className="flex gap-2 bg-slate-900/50 p-2 rounded border border-slate-800 items-end mb-2">
                  <div className="flex-1 grid gap-1">
                    <Label className="text-[10px] text-slate-400">Fornecedor</Label>
                    <FieldSelect value={lf.fornecedor_id} onChange={(v) => { const nova = [...listaFornecedores]; nova[idx].fornecedor_id = v; setListaFornecedores(nova); }} options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} placeholder="Selecione" />
                  </div>
                  <div className="w-28 grid gap-1"><Label className="text-[10px] text-slate-400">Preço Atual</Label><Input value={lf.preco_atual} onChange={(e) => atualizarPreco(idx, e.target.value)} placeholder="R$ 0,00" /></div>
                  <Button type="button" variant="secondary" size="sm" onClick={() => registrarPreco(idx)} className="h-9">Histórico</Button>
                  <div className="flex-1 grid gap-1"><Label className="text-[10px] text-slate-400">Últimos 3</Label><div className="flex gap-1 h-9 items-center">{lf.historico.map((h, i) => <span key={i} className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">{brl(h)}</span>)}</div></div>
                  <Button type="button" variant="ghost" size="icon" className="text-red-400 h-9" onClick={() => removerFornecedor(idx)}><Trash2 className="size-4" /></Button>
                </div>
              ))}
            </div>
            <DialogFooter className="col-span-2 mt-4"><Button type="submit" disabled={salvar.isPending || !form.nome}>Salvar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de Baixa de Estoque (Saída) */}
      <Dialog open={openMov} onOpenChange={setOpenMov}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><ArrowDownRight className="size-5 text-red-400" /> Baixa de Estoque (Saída)</DialogTitle></DialogHeader>
          <form className="grid gap-4" onSubmit={(e) => { e.preventDefault(); salvarMov.mutate(); }}>
            <div className="grid gap-1.5"><Label>Peça *</Label><FieldSelect value={movForm.peca_id} onChange={(v) => setMovForm(s => ({ ...s, peca_id: v, fornecedor_id: "" }))} options={rows.map((r: any) => ({ value: r.id, label: `${r.nome} (Estoque: ${r.quantidade_estoque})` }))} placeholder="Selecione a peça" /></div>
            
            <div className="grid gap-1.5"><Label>Fornecedor de Origem *</Label><FieldSelect value={movForm.fornecedor_id} onChange={(v) => setMovForm(s => ({ ...s, fornecedor_id: v }))} options={fornecedoresDaPeca as any[]} placeholder="Selecione o fornecedor" disabled={!movForm.peca_id} /></div>
            
            <div className="grid gap-1.5">
              <Label>Destino da Peça *</Label>
              <div className="flex gap-2 mb-1">
                <button type="button" onClick={() => setMovForm(s => ({ ...s, destino_tipo: "veiculo" }))} className={`px-3 py-1 text-xs rounded border ${movForm.destino_tipo === 'veiculo' ? 'bg-sky-500/20 border-sky-500 text-sky-300' : 'border-slate-700 text-slate-400'}`}>Veículo</button>
                <button type="button" onClick={() => setMovForm(s => ({ ...s, destino_tipo: "carreta" }))} className={`px-3 py-1 text-xs rounded border ${movForm.destino_tipo === 'carreta' ? 'bg-sky-500/20 border-sky-500 text-sky-300' : 'border-slate-700 text-slate-400'}`}>Carreta</button>
              </div>
              {movForm.destino_tipo === "veiculo" ? (
                <FieldSelect value={movForm.veiculo_id} onChange={(v) => setMovForm(s => ({ ...s, veiculo_id: v }))} options={veiculos.map((v:any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione o Veículo" />
              ) : (
                <FieldSelect value={movForm.carreta_id} onChange={(v) => setMovForm(s => ({ ...s, carreta_id: v }))} options={carretas.map((c:any) => ({ value: c.id, label: `${c.placa} - ${c.modelo}` }))} placeholder="Selecione a Carreta" />
              )}
            </div>

            <div className="grid gap-1.5 bg-slate-900/50 p-2 rounded border border-slate-800">
              <Label className="text-xs text-slate-400">Responsável pela Baixa</Label>
              <Input value={me?.nome || "Usuário Logado"} disabled className="h-8 bg-transparent border-0 px-0 text-sky-400 font-medium" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-1.5"><Label>Quantidade *</Label><Input type="number" min="1" max={pecaSelecionada?.quantidade_estoque || 0} value={movForm.quantidade} onChange={(e) => setMovForm(s => ({ ...s, quantidade: e.target.value }))} required /></div>
              <div className="grid gap-1.5"><Label>Motivo *</Label><Input value={movForm.motivo} onChange={(e) => setMovForm(s => ({ ...s, motivo: e.target.value }))} placeholder="Ex: Manutenção" required /></div>
            </div>
            
            <DialogFooter><Button type="submit" variant="destructive" disabled={salvarMov.isPending || !movForm.peca_id || !movForm.quantidade || !movForm.motivo || (movForm.destino_tipo === 'veiculo' && !movForm.veiculo_id) || (movForm.destino_tipo === 'carreta' && !movForm.carreta_id)}>Confirmar Baixa</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de Inventário */}
      <ConfirmDialog open={openInvConfirm} onOpenChange={setOpenInvConfirm} title="Confirmar Ajuste de Estoque?" description="Isso alterará a quantidade atual das peças para os valores informados e gerará um histórico." confirmLabel="Confirmar Ajuste" pending={salvarInv.isPending} onConfirm={() => { setOpenInvConfirm(false); salvarInv.mutate(); }} testId="inventario-confirmar" />

      <Dialog open={openInv} onOpenChange={(o) => { setOpenInv(o); if (!o) setInvContagens({}); }}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><ClipboardList className="size-5 text-sky-400" /> Inventário Cíclico</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-slate-400 mb-4">Digite a quantidade física. O sistema salvará no histórico e ajustará as diferenças.</p>
          <div className="max-h-[50vh] overflow-y-auto border border-slate-800 rounded-lg">
            <Table>
              <TableHeader><TableRow className="border-slate-800"><TableHead>Peça</TableHead><TableHead className="text-center">Qtd. Sistema</TableHead><TableHead className="text-center w-32">Qtd. Física</TableHead></TableRow></TableHeader>
              <TableBody>
                {rows.map((r: any) => (
                  <TableRow key={r.id}>
                    <TableCell className="text-sm">{r.nome}</TableCell>
                    <TableCell className="text-center font-bold text-slate-400">{r.quantidade_estoque}</TableCell>
                    <TableCell><Input type="number" placeholder={`Atual: ${r.quantidade_estoque}`} value={invContagens[r.id] || ""} onChange={(e) => setInvContagens(s => ({ ...s, [r.id]: e.target.value }))} className="h-8 text-center" /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter className="mt-4">
            <Button variant="ghost" onClick={() => setOpenInv(false)}>Cancelar</Button>
            <Button onClick={() => setOpenInvConfirm(true)} disabled={salvarInv.isPending || Object.keys(invContagens).length === 0}>Salvar Inventário</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Modal de Visualização de Inventário (Histórico) */}
      <Dialog open={viewInv !== null} onOpenChange={(o) => !o && setViewInv(null)}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between w-full">
              <span>Detalhes do Inventário</span>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => exportarExcel(viewInv)}><FileSpreadsheet className="size-4 mr-1" /> Excel</Button>
                <Button size="sm" variant="outline" onClick={() => imprimirPDF(viewInv)}><Printer className="size-4 mr-1" /> PDF</Button>
              </div>
            </DialogTitle>
          </DialogHeader>
          {viewInv && (
            <div>
              <p className="text-sm text-slate-400 mb-2">Responsável: <strong className="text-slate-200">{viewInv.usuario_nome}</strong> em {new Date(viewInv.data_hora).toLocaleString('pt-BR')}</p>
              <div className="border border-slate-800 rounded-lg overflow-hidden">
                <Table>
                  <TableHeader><TableRow className="border-slate-800"><TableHead>Peça</TableHead><TableHead className="text-center">Sistema</TableHead><TableHead className="text-center">Física</TableHead><TableHead className="text-center">Diferença</TableHead></TableRow></TableHeader>
                  <TableBody>
                    {viewInv.itens.map((i: any, idx: number) => (
                      <TableRow key={idx}>
                        <TableCell>{i.peca_nome}</TableCell>
                        <TableCell className="text-center">{i.qtd_anterior}</TableCell>
                        <TableCell className="text-center font-bold">{i.qtd_fisica}</TableCell>
                        <TableCell className={`text-center font-bold ${i.qtd_fisica - i.qtd_anterior < 0 ? 'text-red-400' : 'text-emerald-400'}`}>{i.qtd_fisica - i.qtd_anterior}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir peça?" description="Ação irreversível." confirmLabel="Excluir" destructive pending={excluir.isPending} onConfirm={() => excluirId && excluir.mutate(excluirId)} testId="peca-excluir" />
      <ConfirmDialog open={excluirInvId !== null} onOpenChange={(o) => !o && setExcluirInvId(null)} title="Excluir histórico de inventário?" description="O registro será apagado, mas o estoque atual NÃO será revertido." confirmLabel="Excluir" destructive pending={excluirInv.isPending} onConfirm={() => excluirInvId && excluirInv.mutate(excluirInvId)} testId="inventario-excluir" />
    </div>
  );
}
