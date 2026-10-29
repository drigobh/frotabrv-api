import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {MessageCircle, Building2, User, MapPin, Star, Pencil, Trash2, Plus, Search, AlertTriangle, Wrench, CheckCircle2, Tag, XCircle} from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function Fornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const [filtroNome, setFiltroNome] = useState("");
  const [filtroCidade, setFiltroCidade] = useState("");
  const [filtroTipo, setFiltroTipo] = useState("__all__");
  const [filtroStatus, setFiltroStatus] = useState("__all__");
  const [filtroTipoForn, setFiltroTipoForn] = useState("__all__");
  const [filtroEmpresa, setFiltroEmpresa] = useState("__all__");

  const [isSearching, setIsSearching] = useState(false);
  const [form, setForm] = useState({
    nome: "", tipo_fornecedor_id: "", empresa_id: "", documento: "", tipo_pessoa: "PJ",
    telefone: "", contato: "", whatsapp: "", email: "", endereco: "", bairro: "", cidade: "", estado: "",
    avaliacao: 0, ativo: true
  });

  const { data: fornecedores = [], refetch } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });
  const { data: empresas = [] } = useQuery({ queryKey: ["empresas"], queryFn: () => apiGet<any[]>("/empresa") });

  const rowsFiltradas = useMemo(() => {
    let filtered = fornecedores;
    if (filtroNome) filtered = filtered.filter(f => f.nome.toLowerCase().includes(filtroNome.toLowerCase()) || (f.documento && f.documento.includes(filtroNome)));
    if (filtroCidade) filtered = filtered.filter(f => f.cidade && f.cidade.toLowerCase().includes(filtroCidade.toLowerCase()));
    if (filtroTipo !== "__all__") filtered = filtered.filter(f => f.tipo_pessoa === filtroTipo);
    if (filtroStatus !== "__all__") filtered = filtered.filter(f => f.ativo === (filtroStatus === "ativo"));
    if (filtroTipoForn !== "__all__") filtered = filtered.filter(f => f.tipo_fornecedor_id === filtroTipoForn);
    return filtered;
  }, [fornecedores, filtroNome, filtroCidade, filtroTipo, filtroStatus, filtroTipoForn, filtroEmpresa]);

  
  const buscarCNPJ = async () => {
    const cnpjLimpo = form.documento.replace(/\D/g, '');
    if (cnpjLimpo.length !== 14) {
      return toast.error("Digite um CNPJ válido com 14 dígitos.");
    }
    
    setIsSearching(true);
    try {
      const data = await apiGet<any>(`/empresa/cnpj/${cnpjLimpo}`);
      
      // Atualiza o formulário do fornecedor com os dados da API
      setForm((s: any) => ({
        ...s,
        nome: data.razao_social || s.nome, // No fornecedor, o nome principal é a Razão Social
        documento: data.cnpj || s.documento,
        telefone: data.ddd_telefone_1 || s.telefone,
        email: data.email || s.email,
        endereco: data.logradouro ? `${data.logradouro}, ${data.numero}` : s.endereco,
        bairro: data.bairro || s.bairro,
        cidade: data.municipio || s.cidade,
        estado: data.uf || s.estado
      }));
      toast.success("Dados preenchidos com sucesso!");
    } catch (err: any) {
      toast.error(err.message || "Erro ao buscar o CNPJ.");
    } finally {
      setIsSearching(false);
    }
  };
const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/fornecedores/${editingId}`, form) : apiPost("/fornecedores", form),
    onSuccess: () => { toast.success("Fornecedor salvo"); setOpen(false); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });


  
  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/fornecedores/${id}`),
    onSuccess: () => { toast.success("Fornecedor excluído"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao excluir"),
  });

  

  const abrirNovo = () => {
    setEditingId(null);
    setForm({ nome: "", tipo_fornecedor_id: "", empresa_id: "", documento: "", tipo_pessoa: "PJ", telefone: "", contato: "", whatsapp: "", email: "", endereco: "", bairro: "", cidade: "", estado: "", avaliacao: 0, ativo: true });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({
      nome: r.nome, tipo_fornecedor_id: r.tipo_fornecedor_id || "", empresa_id: r.empresa_id || "", documento: r.documento || "", tipo_pessoa: r.tipo_pessoa || "PJ",
      telefone: r.telefone || "", contato: r.contato || "", whatsapp: r.whatsapp || "", email: r.email || "", endereco: r.endereco || "", bairro: r.bairro || "", cidade: r.cidade || "", estado: r.estado || "",
      avaliacao: r.avaliacao || 0, ativo: r.ativo
    });
    setOpen(true);
  };


  

  

  const stats = useMemo(() => {
    const total = fornecedores.length;
    const ativos = fornecedores.filter(r => r.ativo).length;
    
    const tiposCount: Record<string, number> = {};
    fornecedores.forEach(r => {
      if (r.tipo_fornecedor_id) {
        const t = tipos.find((x:any) => x.id === r.tipo_fornecedor_id)?.nome || "Outros";
        tiposCount[t] = (tiposCount[t] || 0) + 1;
      }
    });
    const maiorTipo = Object.entries(tiposCount).sort((a,b) => b[1] - a[1])[0];

    const estadosCount: Record<string, number> = {};
    fornecedores.forEach(r => {
      if (r.estado) estadosCount[r.estado] = (estadosCount[r.estado] || 0) + 1;
    });
    const maiorEstado = Object.entries(estadosCount).sort((a,b) => b[1] - a[1])[0];
    const menorEstado = Object.entries(estadosCount).sort((a,b) => a[1] - b[1])[0];

    return {
      total, ativos, inativos: total - ativos,
      tipoNome: maiorTipo ? maiorTipo[0] : "—", tipoQtd: maiorTipo ? maiorTipo[1] : 0,
      estadoNome: maiorEstado ? maiorEstado[0] : "—", estadoQtd: maiorEstado ? maiorEstado[1] : 0,
      menorEstadoNome: menorEstado ? menorEstado[0] : "—", menorEstadoQtd: menorEstado ? menorEstado[1] : 0,
    };
  }, [fornecedores, tipos]);

  

  const [mapaAberto, setMapaAberto] = useState(false);
  const [estadoSelecionado, setEstadoSelecionado] = useState("");

  const abrirMapaCompleto = () => {
    setMapaAberto(true);
  };

    const irParaGoogleMaps = () => {
    if (!estadoSelecionado) return toast.error("Selecione um estado.");
    
    if (estadoSelecionado === "TODOS") {
      window.open("https://www.google.com/maps/search/?api=1&query=Fornecedores+Brasil", "_blank");
      setMapaAberto(false);
      return;
    }
    
    const fornecedoresEstado = fornecedores.filter(f => f.estado === estadoSelecionado && f.endereco && f.cidade);
    if (fornecedoresEstado.length === 0) return toast.error("Nenhum fornecedor com endereço completo neste estado.");

    const query = encodeURIComponent(`Fornecedores em ${estadoSelecionado}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, "_blank");
    setMapaAberto(false);
  };
  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Fornecedores"
        description="Gerencie oficinas, postos e prestadores de serviço."
        actions={<div className="flex gap-2">
          
          <Button variant="outline" onClick={abrirMapaCompleto} className="border-indigo-500/40 text-indigo-400 hover:bg-indigo-500/10 h-9">
          <MapPin className="size-4 mr-2" /> Mapa dos Fornecedores
        </Button>
        
        <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Fornecedor</Button>
        </div>}
      />

      <div className="mb-5 grid gap-2 sm:grid-cols-2 lg:grid-cols-6">
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase text-slate-400">Total</p><p className="text-xl font-bold text-slate-100">{stats.total}</p></div>
          <div className="p-1.5 bg-sky-500/10 rounded-lg"><Building2 className="size-4 text-sky-400" /></div>
        </div>
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase text-slate-400">Ativos</p><p className="text-xl font-bold text-emerald-400">{stats.ativos}</p></div>
          <div className="p-1.5 bg-emerald-500/10 rounded-lg"><CheckCircle2 className="size-4 text-emerald-400" /></div>
        </div>
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase text-slate-400">Inativos</p><p className="text-xl font-bold text-rose-400">{stats.inativos}</p></div>
          <div className="p-1.5 bg-rose-500/10 rounded-lg"><XCircle className="size-4 text-rose-400" /></div>
        </div>
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div className="overflow-hidden"><p className="text-[10px] uppercase text-slate-400">Maior Tipo</p><p className="text-xs font-bold text-amber-400 truncate w-24" title={stats.tipoNome}>{stats.tipoNome}</p></div>
          <div className="p-1.5 bg-amber-500/10 rounded-lg shrink-0"><Tag className="size-4 text-amber-400" /></div>
        </div>
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase text-slate-400">Top Estado</p><p className="text-xl font-bold text-indigo-400">{stats.estadoNome} <span className="text-[10px] text-slate-500">({stats.estadoQtd})</span></p></div>
          <div className="p-1.5 bg-indigo-500/10 rounded-lg"><MapPin className="size-4 text-indigo-400" /></div>
        </div>
        <div className="glass p-3 rounded-xl flex justify-between items-center">
          <div><p className="text-[10px] uppercase text-slate-400">Menor Estado</p><p className="text-xl font-bold text-slate-400">{stats.menorEstadoNome} <span className="text-[10px] text-slate-500">({stats.menorEstadoQtd})</span></p></div>
          <div className="p-1.5 bg-slate-800 rounded-lg"><MapPin className="size-4 text-slate-500" /></div>
        </div>
      </div>

      <div className="mb-4 grid grid-cols-1 md:grid-cols-6 gap-2">
        <Input placeholder="Buscar por Nome ou Documento..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} className="h-9" />
        <Input placeholder="Cidade..." value={filtroCidade} onChange={(e) => setFiltroCidade(e.target.value)} className="h-9" />
        <FieldSelect value={filtroTipo} onChange={setFiltroTipo} options={[{ value: "__all__", label: "PJ e PF" }, { value: "PJ", label: "Apenas PJ" }, { value: "PF", label: "Apenas PF" }]} />
        <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: "__all__", label: "Todos os Status" }, { value: "ativo", label: "Apenas Ativos" }, { value: "inativo", label: "Apenas Inativos" }]} />
        <FieldSelect value={filtroEmpresa} onChange={setFiltroEmpresa} options={[{ value: "__all__", label: "Todas as Empresas" }, ...empresas.map((e: any) => ({ value: e.id, label: e.nome_fantasia || e.razao_social }))]} />
        <FieldSelect value={filtroTipoForn} onChange={setFiltroTipoForn} options={[{ value: "__all__", label: "Todos os Tipos" }, ...tipos.filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))]} />
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Empresa / Unidade</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo de Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Rota</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Localização</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Contato</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Avaliação</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && (
              <TableRow><TableCell colSpan={9} className="py-10 text-center text-slate-500">Nenhum fornecedor encontrado.</TableCell></TableRow>
            )}
            {rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                
                <TableCell className="font-medium text-slate-200">
                  <div className="flex items-center gap-2">
                    {r.tipo_pessoa === 'PJ' ? <Building2 className="size-4 text-sky-400" /> : <User className="size-4 text-purple-400" />}
                    <div>
                      <div className="flex items-center gap-2">
                        {r.nome}
                        <span className="text-[9px] font-bold bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{r.tipo_pessoa}</span>
                      </div>
                      <div className="text-slate-500 font-mono text-xs flex flex-col">
                        <span>{r.documento || "—"}</span>
                        {(!r.documento || String(r.documento).trim() === "") && (
                          <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center gap-1 mt-1">
                            <AlertTriangle className="size-3" /> CNPJ Pendente
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </TableCell>
                
                <TableCell className="text-xs text-slate-400">
                  {empresas.find((e: any) => e.id === r.empresa_id)?.nome_fantasia || "—"}
                </TableCell>
                
                <TableCell className="text-xs text-slate-400">
                  {tipos.find((t: any) => t.id === r.tipo_fornecedor_id)?.nome || "—"}
                </TableCell>
                
                <TableCell className="text-xs text-slate-400 text-center">
                  {(() => {
                    if (!r.endereco || !r.cidade) return "—";
                    const emp = empresas.find((e: any) => e.id === r.empresa_id);
                    if (!emp || !emp.endereco) return "—";
                    const origem = encodeURIComponent(`${emp.endereco}, ${emp.cidade}, ${emp.estado}`);
                    const destino = encodeURIComponent(`${r.endereco}, ${r.cidade}, ${r.estado}`);
                    return (
                      <a href={`https://www.google.com/maps/dir/?api=1&origin=${origem}&destination=${destino}`} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline flex items-center justify-center gap-1">
                        <MapPin className="size-3" /> Ver Rota
                      </a>
                    );
                  })()}
                </TableCell>
                
                <TableCell className="text-slate-400 text-xs">
                  <span className="flex items-center gap-1">
                    <MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}
                  </span>
                </TableCell>
                
                <TableCell className="text-xs text-slate-400 text-center">
                  <div className="flex flex-col items-center justify-center">
                    <span className="font-medium text-slate-300">{r.contato || "—"}</span>
                    {r.whatsapp && (
                      <a href={`https://wa.me/55${r.whatsapp.replace(/\D/g, '')}`} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 mt-1">
                        <MessageCircle className="size-4 animate-pulse" />
                        <span className="text-[10px]">{r.whatsapp}</span>
                      </a>
                    )}
                  </div>
                </TableCell>
                
                <TableCell className="text-center">
                  <div className="flex justify-center gap-0.5">
                    {[1, 2, 3, 4, 5].map(star => (
                      <Star key={star} className={`size-3 ${star <= (r.avaliacao || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-700'}`} />
                    ))}
                  </div>
                </TableCell>
                
                <TableCell className="text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${r.ativo ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                    {r.ativo ? "Ativo" : "Inativo"}
                  </span>
                </TableCell>
                
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-4xl flex flex-col max-h-[90vh]">
            
            {/* Cabeçalho */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h2 className="text-lg font-bold text-slate-100">{editingId ? "Editar Fornecedor" : "Novo Fornecedor"}</h2>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>

            {/* Corpo com Scroll */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex flex-col lg:flex-row gap-6">
                
                {/* COLUNA ESQUERDA: Avaliação e Ativo */}
                <div className="w-full lg:w-[180px] shrink-0 flex flex-col gap-6 border-r border-slate-800 pr-6">
                  <div className="flex flex-col gap-2">
                    <Label className="text-xs text-slate-400 font-semibold uppercase">Avaliação</Label>
                    <div className="flex gap-1 items-center">
                      {[1, 2, 3, 4, 5].map(star => (
                        <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110 transition-transform">
                          <Star className={`size-6 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                        </button>
                      ))}
                    </div>
                    <span className="text-[10px] text-slate-500">{form.avaliacao === 0 ? "Sem avaliação" : `${form.avaliacao} de 5`}</span>
                  </div>

                  <div className="flex items-center gap-2 mt-auto pt-4 border-t border-slate-800">
                    <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-4 accent-sky-500" id="ativo-forn" />
                    <Label htmlFor="ativo-forn" className="text-sm font-medium text-slate-200 cursor-pointer">Fornecedor Ativo</Label>
                  </div>
                </div>

                {/* COLUNA DIREITA: Formulário */}
                <div className="flex-1 flex flex-col gap-4">
                  
                  {/* Linha 1: Tipo e Empresa */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Tipo de Fornecedor *</Label>
                      <FieldSelect value={form.tipo_fornecedor_id} onChange={(v) => setForm(s => ({ ...s, tipo_fornecedor_id: v }))} options={tipos.filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))} placeholder="Selecione o tipo..." />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Empresa / Unidade</Label>
                      <FieldSelect value={form.empresa_id} onChange={(v) => setForm(s => ({ ...s, empresa_id: v }))} options={empresas.map((e: any) => ({ value: e.id, label: e.nome_fantasia || e.razao_social }))} placeholder="Vincular a uma empresa..." />
                    </div>
                  </div>

                  {/* Linha 2: Nome e Documento */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="col-span-2 flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Nome / Razão Social *</Label>
                      <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" required />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Documento / CNPJ</Label>
                      <div className="flex gap-2">
                        <Input value={form.documento} onChange={(e) => setForm(s => ({ ...s, documento: e.target.value }))} placeholder="00.000.000/0000-00" className="h-9 bg-slate-950 border-slate-700 flex-1" />
                        <Button 
                          type="button" 
                          onClick={buscarCNPJ} 
                          disabled={isSearching} 
                          className="h-9 w-12 px-0 bg-sky-600 hover:bg-sky-500 shrink-0"
                          title="Buscar CNPJ na Receita"
                        >
                          <Search className="size-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Linha 3: Tipo Pessoa, Telefone, Email */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Tipo Pessoa</Label>
                      <FieldSelect value={form.tipo_pessoa} onChange={(v) => setForm(s => ({ ...s, tipo_pessoa: v }))} options={[{ value: "PJ", label: "PJ" }, { value: "PF", label: "PF" }]} />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Telefone</Label>
                      <Input value={form.telefone} onChange={(e) => setForm(s => ({ ...s, telefone: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="col-span-2 flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">E-mail</Label>
                      <Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 4: Contato e WhatsApp */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Contato</Label>
                      <Input value={form.contato} onChange={(e) => setForm(s => ({ ...s, contato: e.target.value }))} placeholder="Nome do contato" className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1"><MessageCircle className="size-3 text-emerald-500" /> WhatsApp</Label>
                      <Input value={form.whatsapp} onChange={(e) => setForm(s => ({ ...s, whatsapp: e.target.value }))} placeholder="(00) 00000-0000" className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 5: Endereço */}
                  <div className="flex flex-col gap-1.5">
                    <Label className="text-xs text-slate-400">Endereço</Label>
                    <Input value={form.endereco} onChange={(e) => setForm(s => ({ ...s, endereco: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                  </div>

                  {/* Linha 6: Bairro, Cidade, UF */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Bairro</Label>
                      <Input value={form.bairro} onChange={(e) => setForm(s => ({ ...s, bairro: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="col-span-2 flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Cidade</Label>
                      <Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">UF</Label>
                      <Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="h-9 bg-slate-950 border-slate-700 uppercase" />
                    </div>
                  </div>

                </div>
              </div>
            </div>

            {/* Rodapé */}
            <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900/50">
              <Button variant="outline" onClick={() => setOpen(false)} className="h-9">Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending || !form.nome || !form.tipo_fornecedor_id} className="h-9 bg-sky-600 hover:bg-sky-500 font-semibold">
                {salvar.isPending ? "Salvando..." : (editingId ? "Salvar Alterações" : "Cadastrar Fornecedor")}
              </Button>
            </div>
          </div>
        </div>
      )}


      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir Fornecedor?" onConfirm={() => excluirId && excluir.mutate(excluirId)} confirmLabel="Excluir" destructive pending={excluir.isPending} />

      {/* Modal de Filtro do Mapa */}
      {mapaAberto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Selecione o Estado para o Mapa</h2>
            
            <div className="flex flex-col gap-3">
              <Label className="text-xs text-slate-400">Estado (UF)</Label>
              <select 
                value={estadoSelecionado} 
                onChange={(e) => setEstadoSelecionado(e.target.value)}
                className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-200 px-3 w-full"
              >
                <option value="">Selecione...</option>
                <option value="TODOS">Todos os Estados</option>
                {[...new Set(fornecedores.map(f => f.estado))].filter(Boolean).sort().map(uf => (
                  <option key={uf} value={uf}>{uf} ({fornecedores.filter(f => f.estado === uf).length} fornecedores)</option>
                ))}
              </select>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setMapaAberto(false)}>Cancelar</Button>
              <Button onClick={irParaGoogleMaps} className="bg-sky-600 hover:bg-sky-500">
                <MapPin className="size-4 mr-2" /> Abrir no Google Maps
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
