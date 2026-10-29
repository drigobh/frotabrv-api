import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FolderTree, Plus, Pencil, Trash2, Tag, Database } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function TiposFornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  
  const [form, setForm] = useState({ nome: "", categoria_pai_id: "" });
  const [searchTerm, setSearchTerm] = useState("");
  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });

  const q = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });
  const rows = q.data || [];
  const rowsFiltradas = rows.filter(r => r.nome.toLowerCase().includes(searchTerm.toLowerCase()));

  const categorias = rows.filter(r => !r.categoria_pai_id).map(r => ({ value: r.id, label: r.nome }));

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/tipos-fornecedores/${editingId}`, form) : apiPost("/tipos-fornecedores", form),
    onSuccess: () => { toast.success("Tipo salvo"); setOpen(false); qc.invalidateQueries({ queryKey: ["tipos-fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/tipos-fornecedores/${id}`),
    onSuccess: () => { toast.success("Tipo excluído"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["tipos-fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro"),
  });

  
  const seed = useMutation({
    mutationFn: async () => {
      const dados = [
        { nome: "1. Insumos Operacionais e Manutenção", sub: ["Combustíveis e lubrificantes", "Peças e componentes", "Oficinas e serviços mecânicos"] },
        { nome: "2. Serviços de Apoio e Gestão", sub: ["Tecnologia e rastreamento", "Pedágio e meios de pagamento", "Seguros", "Serviços gerais e administrativos"] },
        { nome: "3. Terceirização de Transporte (Agregados e Terceiros)", sub: ["Transportadores autônomos de cargas (TAC) / Agregados", "Empresas parceiras de apoio"] },
        { nome: "4. Infraestrutura e Movimentação de Carga", sub: ["Fabricantes de carrocerias e implementos", "Locadoras de veículos e frotas", "Equipamentos de movimentação", "Sistemas de armazenagem (Estruturas)"] },
        { nome: "5. Segurança e Gerenciamento de Risco (GR)", sub: ["Gerenciadoras de risco", "Empresas de pronta resposta", "Sistemas de segurança física"] },
        { nome: "6. Sustentabilidade e ESG", sub: ["Gestão de resíduos", "Consultorias de transição energética"] },
        { nome: "7. Recursos Humanos e Capacitação", sub: ["Treinamento e direção defensiva", "Agências de recrutamento especializadas", "Plataformas de saúde ocupacional"] }
      ];

      for (const cat of dados) {
        try {
          const res = await apiPost<any>("/tipos-fornecedores", { nome: cat.nome });
          for (const sub of cat.sub) {
            await apiPost("/tipos-fornecedores", { nome: sub, categoria_pai_id: res.id });
          }
        } catch (e: any) {
          if (e.message?.includes("409") || e.message?.includes("Já existe")) {
            console.log(`Categoria já existe: ${cat.nome}`);
          }
        }
      }
    },
    onSuccess: () => {
      toast.success("Lista base populada com sucesso!");
      qc.invalidateQueries({ queryKey: ["tipos-fornecedores"] });
    },
    onError: () => toast.error("Erro ao popular a lista.")
  });

  const popularLista = () => {
    if (confirm("Isso vai adicionar as 7 categorias e todas as subcategorias na base. Deseja continuar?")) {
      seed.mutate();
    }
  };

const abrirNovo = () => { setEditingId(null); setForm({ nome: "", categoria_pai_id: "" }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ nome: r.nome, categoria_pai_id: r.categoria_pai_id || "" }); setOpen(true); };

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Tipos de Fornecedores"
        description="Classificação para insumos, serviços, tecnologia e terceirização."
        actions={<div className="flex gap-2">
          {config?.mostrar_seed_fornecedores && (
            <Button variant="outline" onClick={popularLista} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10">
              <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Lista Base"}
            </Button>
          )}
          <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Tipo</Button>
        </div>}
      />

      <div className="mb-4 flex gap-2">
        <Input 
          placeholder="Pesquisar por categoria ou tipo..." 
          value={searchTerm} 
          onChange={e => setSearchTerm(e.target.value)} 
          className="w-72" 
        />
      </div>
      
      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Categoria Pai</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo de Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={3} className="text-center py-8 text-slate-500">Nenhum tipo cadastrado.</TableCell></TableRow>
            )}
            {rowsFiltradas.filter(r => !r.categoria_pai_id).map(cat => (
              <>
                <TableRow key={cat.id} className="border-slate-800 bg-slate-800/30">
                  <TableCell colSpan={3} className="font-bold text-slate-200 py-2">
                    <div className="flex items-center gap-2"><FolderTree className="size-4 text-sky-400"/> {cat.nome}</div>
                  </TableCell>
                </TableRow>
                {rowsFiltradas.filter(r => r.categoria_pai_id === cat.id).map(sub => (
                  <TableRow key={sub.id} className="border-slate-800/50 hover:bg-slate-800/20">
                    <TableCell className="text-slate-400 pl-10 text-xs">└─ Subcategoria</TableCell>
                    <TableCell className="text-slate-300 font-medium"><Tag className="size-3 inline mr-2 text-slate-500"/>{sub.nome}</TableCell>
                    <TableCell className="text-center">
                      <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(sub)}><Pencil className="size-4 text-sky-400" /></Button>
                      <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(sub.id)}><Trash2 className="size-4 text-red-300" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editingId ? "Editar Tipo" : "Novo Tipo"}</DialogTitle></DialogHeader>
          <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="grid gap-1.5">
              <Label>Categoria Pai (Opcional)</Label>
              <FieldSelect value={form.categoria_pai_id} onChange={(v) => setForm(s => ({ ...s, categoria_pai_id: v }))} options={[{ value: "", label: "Nenhuma (Criar Categoria Principal)" }, ...categorias]} />
            </div>
            <div className="grid gap-1.5">
              <Label>Nome do Tipo *</Label>
              <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: Peças e componentes" required />
            </div>
            <DialogFooter><Button type="submit">Salvar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      
      <Dialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Excluir Tipo?</DialogTitle></DialogHeader>
          <p className="text-sm text-slate-400">Tem certeza que deseja excluir este tipo de fornecedor?</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
            <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
