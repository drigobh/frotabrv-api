import os
import re

def fix_fornecedores(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    
    codigo = r'''import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Truck, Plus, Pencil, Trash2, Search, Loader2, CheckCircle2, XCircle, MapPin, Building2, Phone, Mail } from "lucide-react";
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

// Função de validação de CNPJ
export function validaCNPJ(cnpj: string) {
  cnpj = cnpj.replace(/[^\d]/g, '');
  if (cnpj.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(cnpj)) return false;
  
  let tamanho = cnpj.length - 2;
  let numeros = cnpj.substring(0, tamanho);
  let digitos = cnpj.substring(tamanho);
  let soma = 0;
  let pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  let resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
  if (resultado != parseInt(digitos.charAt(0))) return false;
  
  tamanho = tamanho + 1;
  numeros = cnpj.substring(0, tamanho);
  soma = 0;
  pos = tamanho - 7;
  for (let i = tamanho; i >= 1; i--) {
    soma += parseInt(numeros.charAt(tamanho - i)) * pos--;
    if (pos < 2) pos = 9;
  }
  resultado = soma % 11 < 2 ? 0 : 11 - soma % 11;
  if (resultado != parseInt(digitos.charAt(1))) return false;
  
  return true;
}

const formatCnpj = (value: string) => {
  return value
    .replace(/\D/g, '')
    .replace(/^(\d{2})(\d)/, '$1.$2')
    .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
    .replace(/\.(\d{3})(\d)/, '.$1/$2')
    .replace(/(\d{4})(\d)/, '$1-$2')
    .slice(0, 18);
};

export default function Fornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [buscandoCnpj, setBuscandoCnpj] = useState(false);
  const [excluirId, setExcluirId] = useState<string | null>(null);

  // Estados dos Filtros
  const [filtroNome, setFiltroNome] = useState("");
  const [filtroCidade, setFiltroCidade] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroCnae, setFiltroCnae] = useState("");
  const [filtroStatus, setFiltroStatus] = useState("__all__");

  // Estado do formulário
  const [form, setForm] = useState({
    nome: "",
    cnpj: "",
    telefone: "",
    email: "",
    endereco: "",
    cidade: "",
    estado: "",
    atividade: "",
    ativo: true,
  });

  const q = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const rows = q.data ?? [];

  // Lógica dos Filtros
  const rowsFiltradas = useMemo(() => {
    return rows.filter(r => {
      if (filtroNome && !r.nome.toLowerCase().includes(filtroNome.toLowerCase()) && !r.cnpj?.includes(filtroNome)) return false;
      if (filtroCidade && !r.cidade?.toLowerCase().includes(filtroCidade.toLowerCase())) return false;
      if (filtroEstado && r.estado?.toUpperCase() !== filtroEstado.toUpperCase()) return false;
      if (filtroCnae && !r.atividade?.toLowerCase().includes(filtroCnae.toLowerCase())) return false;
      if (filtroStatus === "ativo" && !r.ativo) return false;
      if (filtroStatus === "inativo" && r.ativo) return false;
      return true;
    });
  }, [rows, filtroNome, filtroCidade, filtroEstado, filtroCnae, filtroStatus]);

  const salvar = useMutation({
    mutationFn: () => {
      if (editingId) return apiPut(`/fornecedores/${editingId}`, form);
      return apiPost("/fornecedores", form);
    },
    onSuccess: () => {
      toast.success(editingId ? "Fornecedor atualizado" : "Fornecedor cadastrado");
      setOpen(false); setEditingId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] });
    },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/fornecedores/${id}`),
    onSuccess: () => { toast.success("Fornecedor excluído"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["fornecedores"] }); },
    onError: (e: any) => toast.error(e.body?.detail || e.message || "Erro ao excluir"),
  });

  const buscarCnpj = async () => {
    const cnpjLimpo = form.cnpj.replace(/[^\d]/g, '');
    if (cnpjLimpo.length !== 14) { toast.error("Digite um CNPJ com 14 dígitos."); return; }
    if (!validaCNPJ(cnpjLimpo)) { toast.error("CNPJ inválido."); return; }
    
    setBuscandoCnpj(true);
    try {
      const res = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpjLimpo}`);
      if (!res.ok) throw new Error("Erro ao buscar CNPJ");
      const data = await res.json();
      
      setForm(s => ({
        ...s,
        nome: data.razao_social || s.nome,
        telefone: data.ddd_telefone_1 || s.telefone,
        email: data.email || s.email,
        endereco: `${data.logradouro || ''}, ${data.numero || ''} - ${data.bairro || ''}`.trim() || s.endereco,
        cidade: data.municipio || data.cidade || s.cidade,
        estado: data.uf || data.estado || s.estado,
        atividade: data.cnae_fiscal_descricao || s.atividade,
      }));
      toast.success("Dados do CNPJ carregados!");
    } catch (error) {
      toast.error("Não foi possível buscar o CNPJ.");
    } finally {
      setBuscandoCnpj(false);
    }
  };

  const abrirNovo = () => { 
    setEditingId(null); 
    setForm({ nome: "", cnpj: "", telefone: "", email: "", endereco: "", cidade: "", estado: "", atividade: "", ativo: true }); 
    setOpen(true); 
  };
  
  const abrirEdicao = (r: any) => { 
    setEditingId(r.id); 
    setForm({ 
      nome: r.nome, cnpj: r.cnpj || "", telefone: r.telefone || "", email: r.email || "", 
      endereco: r.endereco || "", cidade: r.cidade || "", estado: r.estado || "", atividade: r.atividade || "", ativo: r.ativo 
    }); 
    setOpen(true); 
  };

  return (
    <div>
      <PageHeader eyebrow="Cadastros" title="Fornecedores" description="Gerencie oficinas, postos e prestadores de serviço." actions={<Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Novo Fornecedor</Button>} />
      
      {/* Cards de Resumo */}
      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-4">
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Total de Fornecedores</p>
            <p className="text-2xl font-bold text-slate-100 mt-1">{rows.length}</p>
          </div>
          <div className="size-10 rounded-lg bg-sky-500/10 flex items-center justify-center"><Truck className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Ativos</p>
            <p className="text-2xl font-bold text-emerald-400 mt-1">{rows.filter(r => r.ativo).length}</p>
          </div>
          <div className="size-10 rounded-lg bg-emerald-500/10 flex items-center justify-center"><CheckCircle2 className="size-5 text-emerald-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Inativos</p>
            <p className="text-2xl font-bold text-red-400 mt-1">{rows.filter(r => !r.ativo).length}</p>
          </div>
          <div className="size-10 rounded-lg bg-red-500/10 flex items-center justify-center"><XCircle className="size-5 text-red-400" /></div>
        </div>
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 font-medium">Estados Atendidos</p>
            <p className="text-2xl font-bold text-purple-400 mt-1">{new Set(rows.filter(r => r.estado).map(r => r.estado)).size}</p>
          </div>
          <div className="size-10 rounded-lg bg-purple-500/10 flex items-center justify-center"><MapPin className="size-5 text-purple-400" /></div>
        </div>
      </div>

      {/* Filtros */}
      <div className="mb-4 grid grid-cols-1 md:grid-cols-5 gap-2">
        <Input placeholder="Buscar por Nome ou CNPJ..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} />
        <Input placeholder="Cidade..." value={filtroCidade} onChange={(e) => setFiltroCidade(e.target.value)} />
        <Input placeholder="UF (ex: MG)..." value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)} maxLength={2} className="uppercase" />
        <Input placeholder="CNAE / Atividade..." value={filtroCnae} onChange={(e) => setFiltroCnae(e.target.value)} />
        <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: "__all__", label: "Todos os Status" }, { value: "ativo", label: "Apenas Ativos" }, { value: "inativo", label: "Apenas Inativos" }]} testId="filtro-status" />
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Fornecedor / CNPJ</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Contato</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Localização</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">CNAE / Atividade</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && <TableRow><TableCell colSpan={6} className="py-10 text-center text-slate-500">Nenhum fornecedor encontrado com os filtros atuais.</TableCell></TableRow>}
            {rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-medium text-slate-200">
                  <div className="flex items-center gap-2">
                    <Building2 className="size-4 text-slate-500" />
                    <div>
                      <div>{r.nome}</div>
                      <div className="text-slate-500 font-mono text-xs">{r.cnpj || "—"}</div>
                    </div>
                  </div>
                </TableCell>
                <TableCell className="text-slate-400 text-xs">
                  <div className="flex flex-col gap-1">
                    {r.telefone && <span className="flex items-center gap-1"><Phone className="size-3" /> {r.telefone}</span>}
                    {r.email && <span className="flex items-center gap-1"><Mail className="size-3" /> {r.email}</span>}
                    {!r.telefone && !r.email && "—"}
                  </div>
                </TableCell>
                <TableCell className="text-slate-400 text-xs">
                  <div className="flex items-center gap-1">
                    <MapPin className="size-3" />
                    {r.cidade ? `${r.cidade}/${r.estado}` : "—"}
                  </div>
                </TableCell>
                <TableCell className="text-slate-400 text-xs truncate max-w-[250px]" title={r.atividade}>{r.atividade || "—"}</TableCell>
                <TableCell className="text-center">
                  {r.ativo ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400"><CheckCircle2 className="size-3" /> Ativo</span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400"><XCircle className="size-3" /> Inativo</span>
                  )}
                </TableCell>
                <TableCell className="text-center">
                  <div className="flex gap-1 justify-center">
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
        <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Truck className="size-5 text-sky-400" /> {editingId ? "Editar Fornecedor" : "Novo Fornecedor"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { 
            e.preventDefault(); 
            if (form.cnpj && !validaCNPJ(form.cnpj)) { toast.error("O CNPJ informado é inválido."); return; }
            salvar.mutate(); 
          }}>
            
            <div className="col-span-2 grid gap-1.5 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
              <Label className="text-sky-400 font-semibold">CNPJ *</Label>
              <div className="flex gap-2">
                <Input 
                  value={form.cnpj} 
                  onChange={(e) => setForm(s => ({ ...s, cnpj: formatCnpj(e.target.value) }))} 
                  placeholder="00.000.000/0000-00" 
                  className="font-mono text-lg h-11"
                  maxLength={18}
                />
                <Button 
                  type="button" variant="default" onClick={buscarCnpj} 
                  disabled={buscandoCnpj || form.cnpj.length < 18}
                  className="h-11 px-6 bg-sky-600 hover:bg-sky-500 transition-all"
                >
                  {buscandoCnpj ? <Loader2 className="size-4 animate-spin mr-2" /> : <Search className="size-4 mr-2" />}
                  {buscandoCnpj ? "Buscando..." : "Buscar"}
                </Button>
              </div>
            </div>

            <div className="col-span-2 grid gap-1.5"><Label>Razão Social / Nome *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} required /></div>
            
            <div className="grid gap-1.5"><Label>Telefone</Label><Input value={form.telefone} onChange={(e) => setForm(s => ({ ...s, telefone: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} /></div>
            
            <div className="col-span-2 grid gap-1.5"><Label>Endereço</Label><Input value={form.endereco} onChange={(e) => setForm(s => ({ ...s, endereco: e.target.value }))} /></div>
            
            <div className="grid gap-1.5"><Label>Cidade</Label><Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Estado (UF)</Label><Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="uppercase" /></div>
            
            <div className="col-span-2 grid gap-1.5"><Label>Atividade Principal (CNAE)</Label><Input value={form.atividade} onChange={(e) => setForm(s => ({ ...s, atividade: e.target.value }))} placeholder="Ex: Comércio varejista de combustíveis" /></div>
            
            <div className="col-span-2 flex items-center gap-3 mt-2">
              <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-4" />
              <Label>Ativo</Label>
            </div>
            
            <DialogFooter className="col-span-2 mt-4">
              <Button type="submit" disabled={salvar.isPending || !form.nome}>{editingId ? "Salvar Alterações" : "Cadastrar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      
      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir fornecedor?" description="Ação irreversível." confirmLabel="Excluir" destructive pending={excluir.isPending} onConfirm={() => excluirId && excluir.mutate(excluirId)} testId="fornecedor-excluir" />
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Tela de Fornecedores reescrita com Filtros, Ícones e Cards de Resumo.")

if __name__ == "__main__":
    fix_fornecedores(os.getcwd())