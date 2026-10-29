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

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle>{editingId ? "Editar Unidade" : "Nova Unidade"}</DialogTitle></DialogHeader>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
            {/* Coluna Esquerda: Logo e Tipo */}
            <div className="space-y-4">
              <div className="glass rounded-xl p-4 flex flex-col items-center justify-center text-center border border-slate-800">
                <div className="size-24 rounded-xl border-2 border-dashed border-slate-700 bg-slate-900/50 flex items-center justify-center mb-3 overflow-hidden relative">
                  {form.logo_base64 ? <img src={form.logo_base64} className="w-full h-full object-contain" /> : <Building className="size-8 text-slate-600" />}
                </div>
                <label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded text-xs font-medium transition-colors flex items-center gap-1">
                  <Upload className="size-3" /> Alterar Logo
                  <input type="file" accept="image/*" className="hidden" onChange={handleLogo} />
                </label>
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs">Tipo de Unidade</Label>
                <FieldSelect value={form.tipo_unidade} onChange={(v) => setForm((s: any) => ({ ...s, tipo_unidade: v }))} options={[{ value: "Matriz", label: "Matriz" }, { value: "Filial", label: "Filial" }, { value: "Ponto de Apoio", label: "Ponto de Apoio" }, { value: "Parceiro", label: "Parceiro" }]} />
              </div>
            </div>

            {/* Coluna Direita: Formulário */}
            <div className="md:col-span-2 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Razão Social *</Label><Input value={form.razao_social} onChange={e => setForm((s: any) => ({ ...s, razao_social: e.target.value }))} className="h-9" required /></div>
                <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Nome Fantasia</Label><Input value={form.nome_fantasia} onChange={e => setForm((s: any) => ({ ...s, nome_fantasia: e.target.value }))} className="h-9" /></div>
                
                <div className="grid gap-1.5">
                  <Label className="text-xs">CNPJ *</Label>
                  <div className="flex gap-2">
                    <Input value={form.cnpj} onChange={e => setForm((s: any) => ({ ...s, cnpj: e.target.value }))} className="h-9 flex-1" required />
                    <Button type="button" onClick={buscarCNPJ} disabled={isSearching} className="h-9 px-3 bg-sky-600 hover:bg-sky-500"><Search className="size-4" /></Button>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="grid gap-1.5"><Label className="text-xs">I.E.</Label><Input value={form.ie} onChange={e => setForm((s: any) => ({ ...s, ie: e.target.value }))} className="h-9" /></div>
                  <div className="grid gap-1.5"><Label className="text-xs">I.M.</Label><Input value={form.im} onChange={e => setForm((s: any) => ({ ...s, im: e.target.value }))} className="h-9" /></div>
                </div>
                
                <div className="col-span-2 grid grid-cols-4 gap-3">
                  <div className="col-span-3 grid gap-1.5"><Label className="text-xs">Endereço</Label><Input value={form.endereco} onChange={e => setForm((s: any) => ({ ...s, endereco: e.target.value }))} className="h-9" /></div>
                  <div className="grid gap-1.5"><Label className="text-xs">CEP</Label><Input value={form.cep} onChange={e => setForm((s: any) => ({ ...s, cep: e.target.value }))} className="h-9" /></div>
                </div>
                
                <div className="grid gap-1.5"><Label className="text-xs">Bairro</Label><Input value={form.bairro} onChange={e => setForm((s: any) => ({ ...s, bairro: e.target.value }))} className="h-9" /></div>
                <div className="grid grid-cols-3 gap-2">
                  <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Cidade</Label><Input value={form.cidade} onChange={e => setForm((s: any) => ({ ...s, cidade: e.target.value }))} className="h-9" /></div>
                  <div className="grid gap-1.5"><Label className="text-xs">UF</Label><Input value={form.estado} onChange={e => setForm((s: any) => ({ ...s, estado: e.target.value }))} maxLength={2} className="h-9 uppercase" /></div>
                </div>
                
                <div className="grid gap-1.5"><Label className="text-xs">Telefone</Label><Input value={form.telefone} onChange={e => setForm((s: any) => ({ ...s, telefone: e.target.value }))} className="h-9" /></div>
                <div className="grid gap-1.5"><Label className="text-xs">E-mail</Label><Input value={form.email} onChange={e => setForm((s: any) => ({ ...s, email: e.target.value }))} className="h-9" /></div>
              </div>
            </div>
          </div>

          <DialogFooter className="mt-6">
            <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar Unidade"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
