import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Truck, Plus, Pencil, Trash2, Search, Loader2, CheckCircle2, XCircle, MapPin, Building2, Phone, Mail, Printer, Star, User, FileText, AlertTriangle, Briefcase } from "lucide-react";
import { toast } from "sonner";
import { brl } from "@/lib/format";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { FieldSelect } from "@/components/common/FieldSelect";

export function validaCNPJ(cnpj: string) {
  cnpj = cnpj.replace(/[^\d]/g, '');
  if (cnpj.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(cnpj)) return false;
  let tamanho = cnpj.length - 2;
  let numeros = cnpj.substring(0, tamanho);
  let digitos = cnpj.substring(tamanho);
  let soma = 0;
  let pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) { soma += parseInt(numeros.charAt(tamanho - i)) * pos--; if (pos < 2) pos = 9; }
  let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
  if (resultado != parseInt(digitos.charAt(0))) return false;
  tamanho = tamanho + 1; numeros = cnpj.substring(0, tamanho); soma = 0; pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) { soma += parseInt(numeros.charAt(tamanho - i)) * pos--; if (pos < 2) pos = 9; }
  resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
  if (resultado != parseInt(digitos.charAt(1))) return false;
  return true;
}

export function validaCPF(cpf: string) {
  cpf = cpf.replace(/[^\d]/g, '');
  if (cpf.length !== 11) return false;
  if (/^(\d)\1{10}$/.test(cpf)) return false;
  let soma = 0, resto;
  for (let i = 1; i <= 9; i++) soma = soma + parseInt(cpf.substring(i-1, i)) * (11 - i);
  resto = (soma * 10) % 11;
  if ((resto == 10) || (resto == 11)) resto = 0;
  if (resto != parseInt(cpf.substring(9, 10))) return false;
  soma = 0;
  for (let i = 1; i <= 10; i++) soma = soma + parseInt(cpf.substring(i-1, i)) * (12 - i);
  resto = (soma * 10) % 11;
  if ((resto == 10) || (resto == 11)) resto = 0;
  if (resto != parseInt(cpf.substring(10, 11))) return false;
  return true;
}

const formatDoc = (value: string, tipo: string) => {
  const nums = value.replace(/\D/g, '');
  if (tipo === "PJ") {
    return nums.replace(/^(\d{2})(\d)/, '$1.$2').replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3').replace(/\.(\d{3})(\d)/, '.$1/$2').replace(/(\d{4})(\d)/, '$1-$2').slice(0, 18);
  } else {
    return nums.replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d)/, '$1.$2').replace(/(\d{3})(\d{1,2})/, '$1-$2').slice(0, 14);
  }
};

export default function Fornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [buscandoDoc, setBuscandoDoc] = useState(false);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [histFornecedor, setHistFornecedor] = useState<any | null>(null);
  const [erroDoc, setErroDoc] = useState(false);

  const [filtroNome, setFiltroNome] = useState("");
  const [filtroCidade, setFiltroCidade] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("__all__");
  const [filtroStatus, setFiltroStatus] = useState("__all__");

  const [form, setForm] = useState({
    tipo_pessoa: "PJ", nome: "", documento: "", telefone: "", email: "", 
    endereco: "", bairro: "", cidade: "", estado: "", atividade: "", latitude: "", longitude: "", avaliacao: 0, ativo: true
  });

  const q = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const rows = q.data ?? [];
  const manutencoes = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });

  const rowsFiltradas = useMemo(() => {
    return rows.filter(r => {
      if (filtroNome && !r.nome.toLowerCase().includes(filtroNome.toLowerCase()) && !r.documento?.includes(filtroNome)) return false;
      if (filtroCidade && !r.cidade?.toLowerCase().includes(filtroCidade.toLowerCase())) return false;
      if (filtroTipo !== "__all__" && r.tipo_pessoa !== filtroTipo) return false;
      if (filtroStatus === "ativo" && !r.ativo) return false;
      if (filtroStatus === "inativo" && r.ativo) return false;
      return true;
    });
  }, [rows, filtroNome, filtroCidade, filtroTipo, filtroStatus]);

  const mediaAvaliacao = useMemo(() => {
    const comAvaliacao = rows.filter(r => r.avaliacao > 0);
    if (comAvaliacao.length === 0) return 0;
    return comAvaliacao.reduce((acc, r) => acc + r.avaliacao, 0) / comAvaliacao.length;
  }, [rows]);

  const salvar = useMutation({
    mutationFn: () => {
      if (editingId) return apiPut(`/fornecedores/${editingId}`, form);
      return apiPost("/fornecedores", form);
    },
    onSuccess: () => { toast.success(editingId ? "Fornecedor atualizado" : "Fornecedor cadastrado"); setOpen(false); setEditingId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/fornecedores/${id}`),
    onSuccess: () => { toast.success("Fornecedor excluído"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao excluir"),
  });

  const handleDocChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = formatDoc(e.target.value, form.tipo_pessoa);
    setForm(s => ({ ...s, documento: val }));
    setErroDoc(false);
  };

  const validarDocumento = (doc: string) => {
    if (!doc) { setErroDoc(true); return false; }
    if (form.tipo_pessoa === "PJ" && !validaCNPJ(doc)) { setErroDoc(true); return false; }
    if (form.tipo_pessoa === "PF" && !validaCPF(doc)) { setErroDoc(true); return false; }
    setErroDoc(false);
    return true;
  };

  const buscarDoc = async () => {
    if (!validarDocumento(form.documento)) {
      toast.error(`Documento ${form.tipo_pessoa} inválido.`);
      return;
    }
    
    if (form.tipo_pessoa === "PJ") {
      setBuscandoDoc(true);
      try {
        const docLimpo = form.documento.replace(/\D/g, '');
        const res = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${docLimpo}`);
        if (!res.ok) throw new Error("Erro ao buscar CNPJ");
        const data = await res.json();
        setForm(s => ({
          ...s,
          nome: data.razao_social || s.nome, telefone: data.ddd_telefone_1 || s.telefone, email: data.email || s.email,
          endereco: `${data.logradouro || ''}, ${data.numero || ''}`.trim() || s.endereco, bairro: data.bairro || s.bairro,
          cidade: data.municipio || data.cidade || s.cidade, estado: data.uf || data.estado || s.estado, atividade: data.cnae_fiscal_descricao || s.atividade,
        }));
        toast.success("Dados do CNPJ carregados!");
      } catch (error) { toast.error("Não foi possível buscar o CNPJ."); } finally { setBuscandoDoc(false); }
    } else {
      toast.success("CPF válido. Preencha os dados restantes.");
    }
  };

  const verNoMapa = (e: React.MouseEvent, r: any) => {
    e.stopPropagation();
    const query = r.latitude && r.longitude ? `${r.latitude},${r.longitude}` : encodeURIComponent(`${r.endereco || ''}, ${r.bairro || ''}, ${r.cidade || ''} - ${r.estado || ''}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, '_blank');
  };

  const imprimirLista = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;
    const html = `
      <html><head><title>Lista de Fornecedores</title><style>body{font-family:sans-serif;font-size:12px;}table{width:100%;border-collapse:collapse;margin-top:20px;}th,td{border:1px solid #ccc;padding:8px;text-align:left;}th{background-color:#f0f0f0;}h1{font-size:18px;}</style></head>
      <body><h1>Lista de Fornecedores - FrotaBRV</h1><p>Gerado em: ${new Date().toLocaleDateString('pt-BR')}</p>
      <table><thead><tr><th>Nome</th><th>Tipo</th><th>Documento</th><th>Cidade/UF</th><th>Telefone</th><th>Status</th></tr></thead>
      <tbody>${rowsFiltradas.map(r => `<tr><td>${r.nome}</td><td>${r.tipo_pessoa}</td><td>$<div className="flex flex-col items-center justify-center">
                <span>{r.documento || "—"}</span>
                {(!r.documento || String(r.documento).trim() === "") && (
                  <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center justify-center gap-1 mt-1">
                    <AlertTriangle className="size-3" /> CNPJ Pendente
                  </span>
                )}
              </div></td><td>${r.cidade ? `${r.cidade}/${r.estado}` : "—"}</td><td>${r.telefone || "—"}</td><td>${r.ativo ? "Ativo" : "Inativo"}</td></tr>`).join('')}</tbody></table></body></html>`;
    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.print();
  };

  const abrirNovo = () => { 
    setEditingId(null); setErroDoc(false);
    setForm({ tipo_pessoa: "PJ", nome: "", documento: "", telefone: "", email: "", endereco: "", bairro: "", cidade: "", estado: "", atividade: "", latitude: "", longitude: "", avaliacao: 0, ativo: true }); 
    setOpen(true); 
  };
  
  const abrirEdicao = (r: any) => { 
    setEditingId(r.id); setErroDoc(false);
    setForm({ 
      tipo_pessoa: r.tipo_pessoa || "PJ", nome: r.nome, documento: r.documento || "", telefone: r.telefone || "", email: r.email || "", 
      endereco: r.endereco || "", bairro: r.bairro || "", cidade: r.cidade || "", estado: r.estado || "", atividade: r.atividade || "", 
      latitude: r.latitude || "", longitude: r.longitude || "", avaliacao: r.avaliacao || 0, ativo: r.ativo 
    }); 
    setOpen(true); 
  };

  return (
    <div>
      <PageHeader 
        eyebrow="Cadastros" title="Fornecedores" description="Gerencie oficinas, postos e prestadores de serviço." 
        actions={<div className="flex gap-2"><Button variant="outline" onClick={imprimirLista}><Printer className="size-4 mr-2" /> Imprimir</Button><Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Novo Fornecedor</Button></div>} 
      />
      
      {/* Cards de Resumo */}
      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-4">
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div><p className="text-xs text-slate-500 font-medium">Total de Fornecedores</p><p className="text-2xl font-bold text-slate-100 mt-1">{rows.length}</p></div>
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><Truck className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div><p className="text-xs text-slate-500 font-medium">Ativos</p><p className="text-2xl font-bold text-emerald-400 mt-1">{rows.filter(r => r.ativo).length}</p></div>
          <div className="size-10 rounded-lg bg-emerald-500/10 flex items-center justify-center"><CheckCircle2 className="size-5 text-emerald-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div><p className="text-xs text-slate-500 font-medium">Inativos</p><p className="text-2xl font-bold text-red-400 mt-1">{rows.filter(r => !r.ativo).length}</p></div>
          <div className="size-10 rounded-lg bg-red-500/10 flex items-center justify-center"><XCircle className="size-5 text-red-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div><p className="text-xs text-slate-500 font-medium">Média de Avaliação</p><p className="text-2xl font-bold text-amber-400 mt-1">{mediaAvaliacao.toFixed(1)} / 5</p></div>
          <div className="size-10 rounded-lg bg-amber-500/10 flex items-center justify-center"><Star className="size-5 text-amber-400" /></div>
        </div>
      </div>

      <div className="mb-4 grid grid-cols-1 md:grid-cols-5 gap-2">
        <Input placeholder="Buscar por Nome ou Documento..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} />
        <Input placeholder="Cidade..." value={filtroCidade} onChange={(e) => setFiltroCidade(e.target.value)} />
        <FieldSelect value={filtroTipo} onChange={setFiltroTipo} options={[{ value: "__all__", label: "PJ e PF" }, { value: "PJ", label: "Apenas PJ" }, { value: "PF", label: "Apenas PF" }]} testId="filtro-tipo" />
        <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: "__all__", label: "Todos os Status" }, { value: "ativo", label: "Apenas Ativos" }, { value: "inativo", label: "Apenas Inativos" }]} testId="filtro-status" />
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Localização</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Avaliação</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && <TableRow><TableCell colSpan={5} className="py-10 text-center text-slate-500">Nenhum fornecedor encontrado.</TableCell></TableRow>}
            {rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-medium text-slate-200">
                  <div className="flex items-center gap-2">
                    {r.tipo_pessoa === 'PJ' ? <Building2 className="size-4 text-sky-400" /> : <User className="size-4 text-purple-400" />}
                    <div>
                      <div className="flex items-center gap-2">{r.nome}<span className="text-[9px] font-bold bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{r.tipo_pessoa}</span></div>
                      <div className="text-slate-500 font-mono text-xs"><div className="flex flex-col items-center justify-center">
                <span>{r.documento || "—"}</span>
                {(!r.documento || String(r.documento).trim() === "") && (
                  <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center justify-center gap-1 mt-1">
                    <AlertTriangle className="size-3" /> CNPJ Pendente
                  </span>
                )}
              </div></div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-slate-400 text-xs">
                  <div className="flex flex-col gap-1">
                    <span className="flex items-center gap-1"><MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}</span>
                    <button onClick={(e) => verNoMapa(e, r)} className="text-sky-400 hover:underline text-[10px] text-left w-fit">Abrir no Maps</button>
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex justify-center gap-0.5">{[1, 2, 3, 4, 5].map(star => (<Star key={star} className={`size-3 ${star <= (r.avaliacao || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />))}</div>
                </TableCell>
                <TableCell className="text-center">
                  {r.ativo ? <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400"><CheckCircle2 className="size-3" /> Ativo</span> : <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400"><XCircle className="size-3" /> Inativo</span>}
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => setHistFornecedor(r)} title="Ver Histórico">
                      <FileText className="size-4 text-emerald-400" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                    <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4" /></Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Truck className="size-5 text-sky-400" /> {editingId ? "Editar Fornecedor" : "Novo Fornecedor"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-2" onSubmit={(e) => { 
            e.preventDefault(); 
            if (!form.nome.trim()) { toast.error("O nome é obrigatório."); return; }
            if (!validarDocumento(form.documento)) { toast.error(`Documento ${form.tipo_pessoa} inválido.`); return; }
            salvar.mutate(); 
          }}>
            
            <div className="col-span-2 bg-slate-900/50 p-2 rounded-lg border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <Label className="text-sky-400 font-semibold text-xs">Documento *</Label>
                <div className="flex bg-slate-800 rounded p-0.5">
                  <button type="button" onClick={() => setForm(s => ({ ...s, tipo_pessoa: 'PJ', documento: '' }))} className={`px-2 py-0.5 text-[10px] font-bold rounded ${form.tipo_pessoa === 'PJ' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}>PJ</button>
                  <button type="button" onClick={() => setForm(s => ({ ...s, tipo_pessoa: 'PF', documento: '' }))} className={`px-2 py-0.5 text-[10px] font-bold rounded ${form.tipo_pessoa === 'PF' ? 'bg-sky-600 text-white' : 'text-slate-400'}`}>PF</button>
                </div>
              </div>
              <div className="flex gap-1">
                <Input value={form.documento} onChange={handleDocChange} onBlur={() => validarDocumento(form.documento)} placeholder={form.tipo_pessoa === 'PJ' ? "00.000.000/0000-00" : "000.000.000-00"} className={`font-mono text-sm h-9 ${erroDoc ? 'border-red-500' : ''}`} maxLength={form.tipo_pessoa === 'PJ' ? 18 : 14} required />
                <Button type="button" variant="default" onClick={buscarDoc} disabled={buscandoDoc} className="h-9 px-3 bg-sky-600 hover:bg-sky-500">
                  {buscandoDoc ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
                </Button>
              </div>
              {erroDoc && <p className="text-[10px] text-red-400 mt-1">Documento inválido.</p>}
            </div>

            <div className="col-span-2 grid gap-1"><Label className="text-xs">Nome / Razão Social *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} className="h-9" required /></div>
            
            <div className="grid gap-1"><Label className="text-xs">Telefone</Label><Input value={form.telefone} onChange={(e) => setForm(s => ({ ...s, telefone: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9" /></div>
            
            <div className="col-span-2 grid gap-1"><Label className="text-xs">Endereço</Label><Input value={form.endereco} onChange={(e) => setForm(s => ({ ...s, endereco: e.target.value }))} className="h-9" /></div>
            
            <div className="grid gap-1"><Label className="text-xs">Bairro</Label><Input value={form.bairro} onChange={(e) => setForm(s => ({ ...s, bairro: e.target.value }))} className="h-9" /></div>
            <div className="grid grid-cols-3 gap-1">
              <div className="col-span-2 grid gap-1"><Label className="text-xs">Cidade</Label><Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} className="h-9" /></div>
              <div className="grid gap-1"><Label className="text-xs">UF</Label><Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="uppercase h-9" /></div>
            </div>

            <div className="col-span-2 grid gap-1">
              <Label className="text-xs">Avaliação</Label>
              <div className="flex gap-1 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-5 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-[10px] text-slate-400 ml-2">{form.avaliacao === 0 ? "Sem avaliação" : `${form.avaliacao} de 5`}</span>
              </div>
            </div>

            {editingId && manutencoes.data && (
              <div className="col-span-2">
                <Label className="text-slate-400 mb-1 flex items-center gap-1 text-xs"><FileText className="size-3" /> Histórico</Label>
                <div className="bg-slate-950/50 border border-slate-800 rounded-lg p-2 max-h-24 overflow-y-auto">
                  {manutencoes.data.filter((m: any) => m.fornecedor_id === editingId).length === 0 ? (
                    <p className="text-[10px] text-slate-500">Nenhum serviço registrado.</p>
                  ) : (
                    <ul className="space-y-0.5">
                      {manutencoes.data.filter((m: any) => m.fornecedor_id === editingId).map((m: any) => (
                        <li key={m.id} className="text-[10px] text-slate-300 border-b border-slate-800/50 pb-1 last:border-0">
                          <span className="font-mono text-slate-500">{m.data}</span> - <span className="font-bold">{m.veiculo_label.split(" · ")[0]}</span>: {m.descricao}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}

            <div className="col-span-2 flex items-center gap-2 mt-1">
              <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-3.5" />
              <Label className="text-xs">Ativo</Label>
            </div>
            
            <DialogFooter className="col-span-2 mt-2">
              <Button type="submit" className="h-9" disabled={salvar.isPending || !form.nome || !form.documento}>{editingId ? "Salvar" : "Cadastrar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      
      
      {/* Dialog de Histórico */}
      <Dialog open={histFornecedor !== null} onOpenChange={(o) => !o && setHistFornecedor(null)}>
        <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="size-5 text-emerald-400" /> Histórico de Serviços
            </DialogTitle>
            <p className="text-sm text-slate-400">{histFornecedor?.nome}</p>
          </DialogHeader>
          
          <div className="py-2">
            {!manutencoes.data || manutencoes.data.filter((m: any) => m.fornecedor_id === histFornecedor?.id).length === 0 ? (
              <p className="text-center text-sm text-slate-500 py-6">Nenhuma manutenção registrada para este fornecedor.</p>
            ) : (
              <div className="space-y-2">
                <div className="flex justify-between bg-slate-900/50 p-2 rounded-lg text-xs font-bold text-slate-300">
                  <span>Total de Serviços: {manutencoes.data.filter((m: any) => m.fornecedor_id === histFornecedor?.id).length}</span>
                  <span>Total Gasto: {brl(manutencoes.data.filter((m: any) => m.fornecedor_id === histFornecedor?.id).reduce((s: any, m: any) => s + (m.custo || 0), 0))}</span>
                </div>
                
                {manutencoes.data.filter((m: any) => m.fornecedor_id === histFornecedor?.id).map((m: any) => (
                  <div key={m.id} className="bg-slate-950/40 border border-slate-800 rounded-lg p-3">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-mono text-xs text-slate-400">{m.data}</span>
                      <span className="font-bold text-xs text-amber-300">{brl(m.custo)}</span>
                    </div>
                    <div className="text-sm text-slate-200 font-medium">{m.descricao}</div>
                    <div className="text-[10px] text-slate-500 mt-1">{m.veiculo_label}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir fornecedor?" description="Ação irreversível." confirmLabel="Excluir" destructive pending={excluir.isPending} onConfirm={() => excluirId && excluir.mutate(excluirId)} testId="fornecedor-excluir" />
    </div>
  );
}
