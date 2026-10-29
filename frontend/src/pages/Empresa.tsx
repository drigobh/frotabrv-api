import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Building, Upload, MapPin, Phone, Search, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FieldSelect } from "@/components/common/FieldSelect";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export default function Empresa() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const { data: empresas = [], isLoading } = useQuery({
    queryKey: ["empresas"],
    queryFn: () => apiGet<any[]>("/empresa")
  });

  const [form, setForm] = useState<any>({
    razao_social: "", nome_fantasia: "", cnpj: "", ie: "", im: "",
    endereco: "", bairro: "", cidade: "", estado: "", cep: "",
    telefone: "", email: "", site: "", tipo_unidade: "Matriz", logo_base64: ""
  });

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/empresa/${editingId}`, form) : apiPost("/empresa", form),
    onSuccess: () => { 
      toast.success(editingId ? "Unidade atualizada!" : "Unidade cadastrada!"); 
      setOpen(false); 
      setEditingId(null);
      qc.invalidateQueries({ queryKey: ["empresas"] }); 
    },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/empresa/${id}`),
    onSuccess: () => { toast.success("Unidade removida."); qc.invalidateQueries({ queryKey: ["empresas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao excluir"),
  });

  const handleLogo = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setForm((s: any) => ({ ...s, logo_base64: reader.result as string }));
      reader.readAsDataURL(file);
    }
  };

  const buscarCNPJ = async () => {
    const cnpjLimpo = form.cnpj.replace(/\D/g, '');
    if (cnpjLimpo.length !== 14) return toast.error("Digite um CNPJ válido.");
    
    setIsSearching(true);
    try {
      const data = await apiGet<any>(`/empresa/cnpj/${cnpjLimpo}`);
      setForm((s: any) => ({
        ...s,
        razao_social: data.razao_social || s.razao_social,
        nome_fantasia: data.nome_fantasia || s.nome_fantasia,
        cep: data.cep || s.cep,
        endereco: data.logradouro ? `${data.logradouro}, ${data.numero}` : s.endereco,
        bairro: data.bairro || s.bairro,
        cidade: data.municipio || s.cidade,
        estado: data.uf || s.estado,
        telefone: data.ddd_telefone_1 || s.telefone,
        email: data.email || s.email
      }));
      toast.success("Dados preenchidos com sucesso!");
    } catch (err: any) {
      toast.error(err.message || "Erro ao buscar CNPJ.");
    } finally {
      setIsSearching(false);
    }
  };

  const abrirNovo = () => {
    setEditingId(null);
    setForm({ razao_social: "", nome_fantasia: "", cnpj: "", ie: "", im: "", endereco: "", bairro: "", cidade: "", estado: "", cep: "", telefone: "", email: "", site: "", tipo_unidade: "Matriz", logo_base64: "" });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({ ...r });
    setOpen(true);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Empresas e Unidades"
        description="Gerencie a matriz, filiais, pontos de apoio e parceiros."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Nova Unidade</Button>}
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Nome Fantasia / Razão</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">CNPJ</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Cidade/UF</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Tipo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && <TableRow><TableCell colSpan={5} className="text-center py-8 text-slate-500">Carregando...</TableCell></TableRow>}
            {!isLoading && empresas.length === 0 && (
              <TableRow><TableCell colSpan={5} className="text-center py-8 text-slate-500">Nenhuma unidade cadastrada.</TableCell></TableRow>
            )}
            {empresas.map((e: any) => (
              <TableRow key={e.id} className="border-slate-800/70">
                <TableCell className="font-medium text-slate-200">
                  <div className="flex items-center gap-3">
                    {e.logo_base64 ? (
                      <img src={e.logo_base64} className="size-8 rounded object-contain bg-slate-800 p-1" />
                    ) : (
                      <Building className="size-5 text-slate-600" />
                    )}
                    <div>
                      <div>{e.nome_fantasia || e.razao_social}</div>
                      <div className="text-[10px] text-slate-500">{e.razao_social}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-xs font-mono text-slate-400">{e.cnpj}</TableCell>
                <TableCell className="text-xs text-slate-400">{e.cidade ? `${e.cidade}/${e.estado}` : "—"}</TableCell>
                <TableCell className="text-center">
                  <span className={`px-2 py-1 rounded text-[10px] font-bold ${e.tipo_unidade === 'Matriz' ? 'bg-amber-500/20 text-amber-400' : 'bg-sky-500/20 text-sky-400'}`}>
                    {e.tipo_unidade}
                  </span>
                </TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(e)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => { if(confirm("Excluir esta unidade?")) excluir.mutate(e.id); }}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      
      {/* MODAL CUSTOMIZADO - CONTROLE TOTAL */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-3xl flex flex-col max-h-[90vh]">
            
            {/* Cabeçalho */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h2 className="text-lg font-bold text-slate-100">{editingId ? "Editar Unidade" : "Nova Unidade"}</h2>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>

            {/* Corpo com Scroll */}
            <div className="flex-1 overflow-y-auto p-5">
              <div className="flex flex-col lg:flex-row gap-6">
                
                {/* COLUNA ESQUERDA: LOGO E TIPO */}
                <div className="w-full lg:w-[180px] shrink-0 flex flex-col gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-32 h-32 rounded-2xl border-2 border-dashed border-slate-700 bg-slate-950 flex items-center justify-center mb-4 overflow-hidden">
                      {form.logo_base64 ? (
                        <img src={form.logo_base64} className="w-full h-full object-contain p-2" />
                      ) : (
                        <Building className="size-14 text-slate-600" />
                      )}
                    </div>
                    <label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 w-full">
                      <Upload className="size-4" /> Alterar Logo
                      <input type="file" accept="image/*" className="hidden" onChange={handleLogo} />
                    </label>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label className="text-xs font-semibold text-slate-400 uppercase">Tipo de Unidade</Label>
                    <FieldSelect 
                      value={form.tipo_unidade} 
                      onChange={(v) => setForm((s: any) => ({ ...s, tipo_unidade: v }))} 
                      options={[
                        { value: "Matriz", label: "Matriz" }, 
                        { value: "Filial", label: "Filial" }, 
                        { value: "Ponto de Apoio", label: "Ponto de Apoio" }, 
                        { value: "Parceiro", label: "Parceiro" }
                      ]} 
                    />
                  </div>
                </div>

                {/* COLUNA DIREITA: FORMULÁRIO */}
                <div className="flex-1 flex flex-col gap-4">
                  
                  {/* Linha 1: Razão e Fantasia */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Razão Social *</Label>
                      <Input value={form.razao_social} onChange={e => setForm((s: any) => ({ ...s, razao_social: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" required />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Nome Fantasia</Label>
                      <Input value={form.nome_fantasia} onChange={e => setForm((s: any) => ({ ...s, nome_fantasia: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 2: CNPJ, IE, IM */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="md:col-span-2 flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">CNPJ *</Label>
                      <div className="flex gap-2">
                        <Input value={form.cnpj} onChange={e => setForm((s: any) => ({ ...s, cnpj: e.target.value }))} className="h-9 bg-slate-950 border-slate-700 flex-1" required />
                        <Button type="button" onClick={buscarCNPJ} disabled={isSearching} className="h-9 w-12 bg-sky-600 hover:bg-sky-500 shrink-0"><Search className="size-5" /></Button>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">I.E.</Label>
                      <Input value={form.ie} onChange={e => setForm((s: any) => ({ ...s, ie: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">I.M.</Label>
                      <Input value={form.im} onChange={e => setForm((s: any) => ({ ...s, im: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 3: Endereço e CEP */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="md:col-span-3 flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Endereço</Label>
                      <Input value={form.endereco} onChange={e => setForm((s: any) => ({ ...s, endereco: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">CEP</Label>
                      <Input value={form.cep} onChange={e => setForm((s: any) => ({ ...s, cep: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 4: Bairro, Cidade, UF */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Bairro</Label>
                      <Input value={form.bairro} onChange={e => setForm((s: any) => ({ ...s, bairro: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="md:col-span-2 flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Cidade</Label>
                      <Input value={form.cidade} onChange={e => setForm((s: any) => ({ ...s, cidade: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">UF</Label>
                      <Input value={form.estado} onChange={e => setForm((s: any) => ({ ...s, estado: e.target.value }))} maxLength={2} className="h-9 bg-slate-950 border-slate-700 uppercase" />
                    </div>
                  </div>

                  {/* Linha 5: Telefone, Email, Maps */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Telefone</Label>
                      <div className="flex gap-2">
                        <Input value={form.telefone} onChange={e => setForm((s: any) => ({ ...s, telefone: e.target.value }))} className="h-9 bg-slate-950 border-slate-700 flex-1" />
                        {form.endereco && form.cidade && (
                          <Button 
                            type="button" 
                            onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${form.endereco}, ${form.bairro}, ${form.cidade} - ${form.estado}`)}`, "_blank")} 
                            className="h-9 px-4 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 shrink-0"
                            title="Abrir no Google Maps"
                          >
                            <MapPin className="size-5" />
                          </Button>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">E-mail</Label>
                      <Input value={form.email} onChange={e => setForm((s: any) => ({ ...s, email: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                </div>
              </div>
            </div>

            {/* Rodapé */}
            <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900/50">
              <Button variant="outline" onClick={() => setOpen(false)} className="h-9">Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="h-9 bg-sky-600 hover:bg-sky-500 font-semibold">
                {salvar.isPending ? "Salvando..." : "Salvar Unidade"}
              </Button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
