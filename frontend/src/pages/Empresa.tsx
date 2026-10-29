import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, Building, Upload, MapPin, Phone, Mail, Globe, FileText } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function Empresa() {
  const qc = useQueryClient();
  const { data: empresa, isLoading } = useQuery({
    queryKey: ["empresa"],
    queryFn: async () => {
      try { return await apiGet<any>("/empresa"); }
      catch { return null; }
    }
  });

  const [isSearching, setIsSearching] = useState(false);
  const [form, setForm] = useState<any>({
    razao_social: "", nome_fantasia: "", cnpj: "", ie: "", im: "",
    endereco: "", bairro: "", cidade: "", estado: "", cep: "",
    telefone: "", email: "", site: "", tipo_unidade: "Matriz", logo_base64: ""
  });

  useEffect(() => {
    if (empresa) setForm((s: any) => ({ ...s, ...empresa }));
  }, [empresa]);


  const buscarCNPJ = async () => {
    const cnpjLimpo = form.cnpj.replace(/\D/g, '');
    if (cnpjLimpo.length !== 14) {
      return toast.error("Digite um CNPJ válido com 14 dígitos.");
    }
    
    setIsSearching(true);
    try {
      const res = await fetch(`/api/empresa/cnpj/${cnpjLimpo}`);
      if (!res.ok) throw new Error("CNPJ não encontrado na base da Receita.");
      const data = await res.json();
      
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
      toast.error(err.message || "Erro ao buscar o CNPJ.");
    } finally {
      setIsSearching(false);
    }
  };
  const salvar = useMutation({
    mutationFn: () => apiPut("/empresa", form),
    onSuccess: () => { toast.success("Dados da empresa salvos!"); qc.invalidateQueries({ queryKey: ["empresa"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });

  const handleLogo = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setForm((s: any) => ({ ...s, logo_base64: reader.result as string }));
      reader.readAsDataURL(file);
    }
  };

  if (isLoading) return <div className="p-8 text-center text-slate-400">Carregando...</div>;

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Dados da Empresa"
        description="Cadastro da matriz e filiais, logomarca e identificação."
        actions={<Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="bg-sky-600 hover:bg-sky-500"><FileText className="size-4 mr-2" /> {salvar.isPending ? "Salvando..." : "Salvar Dados"}</Button>}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
        {/* COLUNA ESQUERDA: Logomarca e Tipo */}
        <div className="space-y-4">
          <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center text-center">
            <div className="size-32 rounded-2xl border-2 border-dashed border-slate-700 bg-slate-900/50 flex items-center justify-center mb-4 overflow-hidden relative">
              {form.logo_base64 ? (
                <img src={form.logo_base64} alt="Logo" className="w-full h-full object-contain" />
              ) : (
                <Building className="size-12 text-slate-600" />
              )}
            </div>
            <Label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2">
              <Upload className="size-4" /> Alterar Logomarca
              <input type="file" accept="image/*" className="hidden" onChange={handleLogo} />
            </Label>
            <p className="text-[10px] text-slate-500 mt-2">PNG ou JPG, máx 2MB.</p>
          </div>

          <div className="glass rounded-2xl p-4">
            <Label className="text-xs mb-2 block">Tipo de Unidade</Label>
            <FieldSelect value={form.tipo_unidade} onChange={(v) => setForm((s: any) => ({ ...s, tipo_unidade: v }))} options={[{ value: "Matriz", label: "Matriz" }, { value: "Filial", label: "Filial" }, { value: "Ponto de Apoio", label: "Ponto de Apoio" }, { value: "Parceiro", label: "Parceiro" }]} />
          </div>
        </div>

        {/* COLUNA DIREITA: Formulário */}
        <div className="md:col-span-2 glass rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2 flex items-center gap-2"><Building className="size-4 text-sky-400" /> Dados Cadastrais</h3>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Razão Social *</Label><Input value={form.razao_social} onChange={e => setForm((s: any) => ({ ...s, razao_social: e.target.value }))} className="h-9" required /></div>
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Nome Fantasia</Label><Input value={form.nome_fantasia} onChange={e => setForm((s: any) => ({ ...s, nome_fantasia: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5">
              <Label className="text-xs">CNPJ *</Label>
              <div className="flex gap-2">
                <Input 
                  value={form.cnpj} 
                  onChange={e => setForm((s: any) => ({ ...s, cnpj: e.target.value }))} 
                  placeholder="00.000.000/0000-00"
                  className="h-9 flex-1" 
                  required 
                />
                <Button 
                  type="button" 
                  onClick={buscarCNPJ} 
                  disabled={isSearching} 
                  className="h-9 px-3 bg-sky-600 hover:bg-sky-500"
                >
                  <Search className="size-4" />
                </Button>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1.5"><Label className="text-xs">I.E.</Label><Input value={form.ie} onChange={e => setForm((s: any) => ({ ...s, ie: e.target.value }))} className="h-9" /></div>
              <div className="grid gap-1.5"><Label className="text-xs">I.M.</Label><Input value={form.im} onChange={e => setForm((s: any) => ({ ...s, im: e.target.value }))} className="h-9" /></div>
            </div>
          </div>

          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2 flex items-center gap-2 mt-6"><MapPin className="size-4 text-sky-400" /> Endereço</h3>
          
          <div className="grid grid-cols-4 gap-3">
            <div className="col-span-3 grid gap-1.5"><Label className="text-xs">Endereço</Label><Input value={form.endereco} onChange={e => setForm((s: any) => ({ ...s, endereco: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">CEP</Label><Input value={form.cep} onChange={e => setForm((s: any) => ({ ...s, cep: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">Bairro</Label><Input value={form.bairro} onChange={e => setForm((s: any) => ({ ...s, bairro: e.target.value }))} className="h-9" /></div>
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Cidade</Label><Input value={form.cidade} onChange={e => setForm((s: any) => ({ ...s, cidade: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">UF</Label><Input value={form.estado} onChange={e => setForm((s: any) => ({ ...s, estado: e.target.value }))} maxLength={2} className="h-9 uppercase" /></div>
          </div>

          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2 flex items-center gap-2 mt-6"><Phone className="size-4 text-sky-400" /> Contato</h3>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5"><Label className="text-xs">Telefone</Label><Input value={form.telefone} onChange={e => setForm((s: any) => ({ ...s, telefone: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={e => setForm((s: any) => ({ ...s, email: e.target.value }))} className="h-9" /></div>
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Site</Label><Input value={form.site} onChange={e => setForm((s: any) => ({ ...s, site: e.target.value }))} placeholder="https://" className="h-9" /></div>
          </div>
        </div>
      </div>
    </div>
  );
}
