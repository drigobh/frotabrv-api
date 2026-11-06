import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Building2, Tag, X, Check, Pencil, Power, Trash2, Search, ArrowUpCircle, ArrowDownCircle, CircleDot } from "lucide-react";
import { apiGet, apiPost, apiPut, apiPatch, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function CadastrosFinanceiros() {
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<"Bancos" | "Categorias">("Bancos");
  const [buscaBanco, setBuscaBanco] = useState("");
  const [buscaCat, setBuscaCat] = useState("");
  const [filtroCat, setFiltroCat] = useState("Todos");

  // --- BANCO STATES ---
  const [modalBancoOpen, setModalBancoOpen] = useState(false);
  const [editandoBanco, setEditandoBanco] = useState<any>(null);
  const [formBanco, setFormBanco] = useState({ nome: "", agencia: "", numero_agencia: "", conta: "", telefone: "", contato: "", whatsapp: "" });

  // --- CATEGORIA STATES ---
  const [modalCatOpen, setModalCatOpen] = useState(false);
  const [editandoCat, setEditandoCat] = useState<any>(null);
  const [formCat, setFormCat] = useState({ nome: "", tipo: "Ambos" });

  // --- QUERIES ---
  const { data: bancos = [] } = useQuery({ queryKey: ["bancos"], queryFn: () => apiGet<any[]>("/cadastros-financeiros/bancos") });
  const { data: categorias = [] } = useQuery({ queryKey: ["categorias-financeiras"], queryFn: () => apiGet<any[]>("/cadastros-financeiros/categorias") });

  // --- MUTATIONS BANCO ---
  const salvarBanco = useMutation({
    mutationFn: (payload: any) => editandoBanco ? apiPut(`/cadastros-financeiros/bancos/${editandoBanco.id}`, payload) : apiPost("/cadastros-financeiros/bancos", payload),
    onSuccess: () => { toast.success(editandoBanco ? "Banco atualizado!" : "Banco cadastrado!"); setModalBancoOpen(false); qc.invalidateQueries({ queryKey: ["bancos"] }); }
  });

  const alternarStatusBanco = useMutation({
    mutationFn: ({ id, ativo }: { id: string, ativo: boolean }) => apiPatch(`/cadastros-financeiros/bancos/${id}/status`, { ativo }),
    onSuccess: () => { toast.success("Status alterado!"); qc.invalidateQueries({ queryKey: ["bancos"] }); }
  });

  const excluirBanco = useMutation({
    mutationFn: (id: string) => apiDelete(`/cadastros-financeiros/bancos/${id}`),
    onSuccess: () => { toast.success("Banco excluído!"); qc.invalidateQueries({ queryKey: ["bancos"] }); }
  });

  // --- MUTATIONS CATEGORIA ---
  const salvarCat = useMutation({
    mutationFn: (payload: any) => editandoCat ? apiPut(`/cadastros-financeiros/categorias/${editandoCat.id}`, payload) : apiPost("/cadastros-financeiros/categorias", payload),
    onSuccess: () => { toast.success(editandoCat ? "Categoria atualizada!" : "Categoria cadastrada!"); setModalCatOpen(false); qc.invalidateQueries({ queryKey: ["categorias-financeiras"] }); }
  });

  const alternarStatusCat = useMutation({
    mutationFn: ({ id, ativo }: { id: string, ativo: boolean }) => apiPatch(`/cadastros-financeiros/categorias/${id}/status`, { ativo }),
    onSuccess: () => { toast.success("Status alterado!"); qc.invalidateQueries({ queryKey: ["categorias-financeiras"] }); }
  });

  const excluirCat = useMutation({
    mutationFn: (id: string) => apiDelete(`/cadastros-financeiros/categorias/${id}`),
    onSuccess: () => { toast.success("Categoria excluída!"); qc.invalidateQueries({ queryKey: ["categorias-financeiras"] }); }
  });

  // --- FILTROS ---
  const bancosFiltrados = bancos.filter((b: any) =>
    (b.nome || "").toLowerCase().includes(buscaBanco.toLowerCase()) ||
    (b.agencia || "").toLowerCase().includes(buscaBanco.toLowerCase()) ||
    (b.conta || "").toLowerCase().includes(buscaBanco.toLowerCase())
  );

  const categoriasFiltradas = categorias.filter((c: any) => {
    const matchBusca = (c.nome || "").toLowerCase().includes(buscaCat.toLowerCase());
    const matchTipo = filtroCat === "Todos" || c.tipo === filtroCat;
    return matchBusca && matchTipo;
  });

  // --- HANDLERS ---
  const abrirNovoBanco = () => { setEditandoBanco(null); setFormBanco({ nome: "", agencia: "", numero_agencia: "", conta: "", telefone: "", contato: "", whatsapp: "" }); setModalBancoOpen(true); };
  const abrirEdicaoBanco = (b: any) => { setEditandoBanco(b); setFormBanco({ ...b }); setModalBancoOpen(true); };
  const abrirNovaCat = () => { setEditandoCat(null); setFormCat({ nome: "", tipo: "Ambos" }); setModalCatOpen(true); };
  const abrirEdicaoCat = (c: any) => { setEditandoCat(c); setFormCat({ ...c }); setModalCatOpen(true); };

  return (
    <div>
      <PageHeader eyebrow="Cadastros" title="Financeiro" description="Gerencie os bancos e as categorias de lançamento." />

      <div className="flex gap-1 bg-slate-900/50 p-1 rounded-lg mb-4 w-fit border border-slate-800">
        <button onClick={() => setAbaAtiva("Bancos")} className={cn("px-4 py-1.5 rounded-md text-sm font-medium transition-colors", abaAtiva === "Bancos" ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200")}>
          <Building2 className="size-4 inline mr-2" /> Bancos
        </button>
        <button onClick={() => setAbaAtiva("Categorias")} className={cn("px-4 py-1.5 rounded-md text-sm font-medium transition-colors", abaAtiva === "Categorias" ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200")}>
          <Tag className="size-4 inline mr-2" /> Categorias
        </button>
      </div>

      {/* ABA BANCOS */}
      {abaAtiva === "Bancos" && (
        <div>
          <div className="flex gap-2 justify-between items-center mb-4">
            <div className="relative w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder="Buscar banco..." value={buscaBanco} onChange={(e) => setBuscaBanco(e.target.value)} className="pl-9 h-9" />
            </div>
            <Button onClick={abrirNovoBanco} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Banco</Button>
          </div>

          <div className="glass rounded-2xl overflow-hidden border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50">
                <tr className="text-[11px] uppercase tracking-wider text-slate-400">
                  <th className="px-5 py-3 font-medium">Nome</th>
                  <th className="px-3 py-3 font-medium">Agência</th>
                  <th className="px-3 py-3 font-medium">Nº Agência</th>
                  <th className="px-3 py-3 font-medium">Conta</th>
                  <th className="px-3 py-3 font-medium">Telefone</th>
                  <th className="px-3 py-3 font-medium">WhatsApp</th>
                  <th className="px-3 py-3 font-medium">Contato</th>
                  <th className="px-3 py-3 text-right font-medium">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {bancosFiltrados.length === 0 ? (
                  <tr><td colSpan={8} className="p-8 text-center text-slate-400">Nenhum banco encontrado.</td></tr>
                ) : (
                  bancosFiltrados.map((b: any) => (
                    <tr key={b.id} className={cn("hover:bg-slate-800/30 transition-colors", !b.ativo && "opacity-50")}>
                      <td className="px-5 py-3 text-slate-200 font-medium">{b.nome}</td>
                      <td className="px-3 py-3 text-slate-300">{b.agencia || "—"}</td>
                      <td className="px-3 py-3 text-slate-300">{b.numero_agencia || "—"}</td>
                      <td className="px-3 py-3 text-slate-300">{b.conta || "—"}</td>
                      <td className="px-3 py-3 text-slate-300">{b.telefone || "—"}</td>
                      <td className="px-3 py-3 text-slate-300">{b.whatsapp || "—"}</td>
                      <td className="px-3 py-3 text-slate-300">{b.contato || "—"}</td>
                      <td className="px-3 py-3 text-right flex justify-end gap-1">
                        <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicaoBanco(b)}><Pencil className="size-4 text-sky-400" /></Button>
                        <Button size="icon-sm" variant="ghost" onClick={() => alternarStatusBanco.mutate({ id: b.id, ativo: !b.ativo })} className={b.ativo ? "text-amber-400" : "text-emerald-400"}>
                          <Power className="size-4" />
                        </Button>
                        <Button size="icon-sm" variant="ghost" onClick={() => { if (confirm("Excluir banco?")) excluirBanco.mutate(b.id); }}><Trash2 className="size-4 text-rose-400" /></Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ABA CATEGORIAS */}
      {abaAtiva === "Categorias" && (
        <div>
          <div className="flex gap-2 justify-between items-center mb-4">
            <div className="flex gap-2">
              <div className="relative w-72">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
                <Input placeholder="Buscar categoria..." value={buscaCat} onChange={(e) => setBuscaCat(e.target.value)} className="pl-9 h-9" />
              </div>
              <select value={filtroCat} onChange={(e) => setFiltroCat(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                <option value="Todos">Todos os Tipos</option>
                <option value="Pagar">Pagar</option>
                <option value="Receber">Receber</option>
                <option value="Ambos">Ambos</option>
              </select>
            </div>
            <Button onClick={abrirNovaCat} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Categoria</Button>
          </div>

          <div className="glass rounded-2xl overflow-hidden border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50">
                <tr className="text-[11px] uppercase tracking-wider text-slate-400">
                  <th className="px-5 py-3 font-medium text-slate-200">Nome</th>
                  <th className="px-3 py-3 font-medium text-slate-200">Tipo</th>
                  <th className="px-3 py-3 text-right font-medium text-slate-200">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {categoriasFiltradas.length === 0 ? (
                  <tr><td colSpan={3} className="p-8 text-center text-slate-300">Nenhuma categoria encontrada.</td></tr>
                ) : (
                  categoriasFiltradas.map((c: any) => (
                    <tr key={c.id} className={cn("hover:bg-slate-800/30 transition-colors", !c.ativo && "opacity-50")}>
                      <td className="px-5 py-3 text-slate-200 font-medium">{c.nome}</td>
                      <td className="px-3 py-3">
                        <span className={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide",
                          c.tipo === "Pagar" ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" :
                          c.tipo === "Receber" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" :
                          "bg-sky-500/20 text-sky-400 border border-sky-500/30"
                        )}>
                          {c.tipo === "Pagar" && <ArrowUpCircle className="size-3.5" />}
                          {c.tipo === "Receber" && <ArrowDownCircle className="size-3.5" />}
                          {c.tipo === "Ambos" && <CircleDot className="size-3.5" />}
                          {c.tipo}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right flex justify-end gap-1">
                        <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicaoCat(c)}><Pencil className="size-4 text-sky-400" /></Button>
                        <Button size="icon-sm" variant="ghost" onClick={() => alternarStatusCat.mutate({ id: c.id, ativo: !c.ativo })} className={c.ativo ? "text-amber-400" : "text-emerald-400"}>
                          <Power className="size-4" />
                        </Button>
                        <Button size="icon-sm" variant="ghost" onClick={() => { if (confirm("Excluir categoria?")) excluirCat.mutate(c.id); }}><Trash2 className="size-4 text-rose-400" /></Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}{/* MODAL BANCO */}
      {modalBancoOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">{editandoBanco ? "Editar Banco" : "Novo Banco"}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalBancoOpen(false)}><X className="size-5" /></Button>
            </div>
            <div className="space-y-4">
              <div className="grid gap-1.5"><Label>Nome do Banco *</Label><Input value={formBanco.nome} onChange={(e) => setFormBanco(s => ({ ...s, nome: e.target.value }))} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5"><Label>Agência</Label><Input value={formBanco.agencia} onChange={(e) => setFormBanco(s => ({ ...s, agencia: e.target.value }))} /></div>
                <div className="grid gap-1.5"><Label>Nº da Agência</Label><Input value={formBanco.numero_agencia} onChange={(e) => setFormBanco(s => ({ ...s, numero_agencia: e.target.value }))} /></div>
              </div>
              <div className="grid gap-1.5"><Label>Conta</Label><Input value={formBanco.conta} onChange={(e) => setFormBanco(s => ({ ...s, conta: e.target.value }))} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5"><Label>Telefone</Label><Input value={formBanco.telefone} onChange={(e) => setFormBanco(s => ({ ...s, telefone: e.target.value }))} /></div>
                <div className="grid gap-1.5"><Label>WhatsApp</Label><Input value={formBanco.whatsapp} onChange={(e) => setFormBanco(s => ({ ...s, whatsapp: e.target.value }))} /></div>
              </div>
              <div className="grid gap-1.5"><Label>Contato</Label><Input value={formBanco.contato} onChange={(e) => setFormBanco(s => ({ ...s, contato: e.target.value }))} /></div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalBancoOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvarBanco.mutate(formBanco)} disabled={!formBanco.nome} className="bg-emerald-600 hover:bg-emerald-500 text-white">Salvar</Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL CATEGORIA */}
      {modalCatOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">{editandoCat ? "Editar Categoria" : "Nova Categoria"}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalCatOpen(false)}><X className="size-5" /></Button>
            </div>
            <div className="space-y-4">
              <div className="grid gap-1.5"><Label>Nome da Categoria *</Label><Input value={formCat.nome} onChange={(e) => setFormCat(s => ({ ...s, nome: e.target.value }))} /></div>
              <div className="grid gap-1.5">
                <Label>Tipo</Label>
                <select value={formCat.tipo} onChange={(e) => setFormCat(s => ({ ...s, tipo: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md px-3">
                  <option value="Ambos">Ambos (Pagar e Receber)</option>
                  <option value="Pagar">Apenas Pagar</option>
                  <option value="Receber">Apenas Receber</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalCatOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvarCat.mutate(formCat)} disabled={!formCat.nome} className="bg-emerald-600 hover:bg-emerald-500 text-white">Salvar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
