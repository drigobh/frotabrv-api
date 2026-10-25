import os

def fix_backend(raiz):
    # 1. Adicionar Auditoria no Modelo
    caminho = os.path.join(raiz, "app", "backend", "models", "pecas.py")
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel, Field
from typing import Optional

class PecaCreate(BaseModel):
    nome: str = Field(min_length=2)
    codigo: Optional[str] = None
    preco_custo: float = 0.0
    quantidade_estoque: int = 0
    estoque_minimo: int = 5
    fornecedor_id: Optional[str] = None
    ativo: bool = True

class Peca(PecaCreate):
    id: str
    created_by_name: Optional[str] = None
    created_at: Optional[str] = None
''')

    # 2. Atualizar Router para salvar o auditor
    caminho_router = os.path.join(raiz, "app", "backend", "routers", "pecas.py")
    with open(caminho_router, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'created_by_name' not in c:
        c = c.replace(
            '@router.post("", response_model=Peca, status_code=201)\nasync def criar(body: PecaCreate, _u: dict = Depends(require("write"))):',
            '@router.post("", response_model=Peca, status_code=201)\nasync def criar(body: PecaCreate, user: dict = Depends(require("write"))):'
        )
        c = c.replace(
            'doc["created_at"] = now_iso()',
            'doc["created_by_name"] = user.get("nome", user.get("email", "Sistema"))\n    doc["created_at"] = now_iso()'
        )
        
        # Manter auditoria no update
        c = c.replace(
            'doc = body.model_dump()\n    await db.pecas.update_one({"id": id}, {"$set": doc})',
            'doc = body.model_dump()\n    doc["created_by_name"] = existe.get("created_by_name", "Sistema")\n    doc["created_at"] = existe.get("created_at", now_iso())\n    await db.pecas.update_one({"id": id}, {"$set": doc})'
        )
        with open(caminho_router, 'w', encoding='utf-8') as f:
            f.write(c)
    print("✅ Backend atualizado com Auditoria (created_by_name).")

def fix_frontend_estoque(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    codigo = r'''import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Package, Plus, Pencil, Trash2, AlertTriangle, CheckCircle2, Search, MapPin, Info } from "lucide-react";
import { toast } from "sonner";
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

export default function Estoque() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [busca, setBusca] = useState("");

  const [form, setForm] = useState({ nome: "", codigo: "", preco_custo: "", quantidade_estoque: "", estoque_minimo: "5", fornecedor_id: "", ativo: true });

  const q = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas") });
  const fornQ = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  
  const rows = q.data ?? [];
  const fornecedores = fornQ.data ?? [];

  const rowsFiltradas = useMemo(() => {
    return rows.filter(r => r.nome.toLowerCase().includes(busca.toLowerCase()) || (r.codigo && r.codigo.toLowerCase().includes(busca.toLowerCase())));
  }, [rows, busca]);

  const salvar = useMutation({
    mutationFn: () => {
      const payload = { 
        ...form, 
        preco_custo: Number(form.preco_custo.replace(",", ".")) || 0, 
        quantidade_estoque: Number(form.quantidade_estoque) || 0, 
        estoque_minimo: Number(form.estoque_minimo) || 0 
      };
      if (editingId) return apiPut(`/pecas/${editingId}`, payload);
      return apiPost("/pecas", payload);
    },
    onSuccess: () => { 
      toast.success(editingId ? "Peça atualizada" : "Peça cadastrada"); 
      setOpen(false); setEditingId(null); qc.invalidateQueries({ queryKey: ["pecas"] }); 
    },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pecas/${id}`),
    onSuccess: () => { toast.success("Peça excluída"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pecas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao excluir"),
  });

  const abrirNovo = () => { 
    setEditingId(null); 
    setForm({ nome: "", codigo: "", preco_custo: "", quantidade_estoque: "", estoque_minimo: "5", fornecedor_id: "", ativo: true }); 
    setOpen(true); 
  };

  const abrirEdicao = (r: any) => { 
    setEditingId(r.id); 
    setForm({ nome: r.nome, codigo: r.codigo || "", preco_custo: String(r.preco_custo), quantidade_estoque: String(r.quantidade_estoque), estoque_minimo: String(r.estoque_minimo), fornecedor_id: r.fornecedor_id || "", ativo: r.ativo }); 
    setOpen(true); 
  };

  // Cálculos
  const totalItens = rows.length;
  const valorTotal = rows.reduce((s, r) => s + (r.preco_custo * r.quantidade_estoque), 0);
  const itensBaixos = rows.filter(r => r.quantidade_estoque <= r.estoque_minimo).length;
  
  // Conta os estados únicos baseados nos fornecedores das peças
  const estadosOrigem = new Set(
    rows.map(r => {
      const f = fornecedores.find((x: any) => x.id === r.fornecedor_id);
      return f?.estado;
    }).filter(Boolean)
  ).size;

  return (
    <div>
      <PageHeader 
        eyebrow="Operação" title="Estoque de Peças" description="Controle de almoxarifado." 
        actions={<Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Nova Peça</Button>} 
      />

      {/* Cards Menores e Mais Compactos */}
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
              <TableHead className="text-xs uppercase text-slate-500">Peça / Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Atual</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Mínima</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-right">Preço Custo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-right">Valor Total</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rowsFiltradas.length === 0 && <TableRow><TableCell colSpan={7} className="py-10 text-center text-slate-500">Nenhuma peça encontrada.</TableCell></TableRow>}
            {rowsFiltradas.map((r) => {
              const estoqueBaixo = r.quantidade_estoque <= r.estoque_minimo;
              const forn = fornecedores.find((f: any) => f.id === r.fornecedor_id);
              return (
                <TableRow key={r.id} className="border-slate-800/70">
                  <TableCell className="font-medium text-slate-200">
                    <div>{r.nome}</div>
                    <div className="text-slate-500 font-mono text-xs">{r.codigo || "—"}</div>
                    {forn && <div className="text-[10px] text-sky-400 mt-0.5">Fornecedor: {forn.nome} {forn.estado && `(${forn.estado})`}</div>}
                  </TableCell>
                  <TableCell className={`text-center font-bold ${estoqueBaixo ? 'text-red-400' : 'text-emerald-400'}`}>{r.quantidade_estoque}</TableCell>
                  <TableCell className="text-center text-slate-400">{r.estoque_minimo}</TableCell>
                  <TableCell className="text-right text-slate-300">{brl(r.preco_custo)}</TableCell>
                  <TableCell className="text-right font-medium text-slate-200">{brl(r.preco_custo * r.quantidade_estoque)}</TableCell>
                  <TableCell className="text-center">
                    {estoqueBaixo ? (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/20 text-red-400"><AlertTriangle className="size-3" /> Baixo</span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400"><CheckCircle2 className="size-3" /> OK</span>
                    )}
                  </TableCell>
                  <TableCell className="text-center">
                    <div className="flex gap-1 justify-center">
                      <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Cadastrado por: ${r.created_by_name || 'Sistema'}`}>
                        <Info className="size-4 text-slate-400" />
                      </Button>
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

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Package className="size-5 text-sky-400" /> {editingId ? "Editar Peça" : "Nova Peça"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="col-span-2 grid gap-1.5"><Label>Nome da Peça *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} required /></div>
            <div className="col-span-2 grid gap-1.5"><Label>Código / Referência</Label><Input value={form.codigo} onChange={(e) => setForm(s => ({ ...s, codigo: e.target.value }))} /></div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Fornecedor</Label>
              <FieldSelect value={form.fornecedor_id} onChange={(v) => setForm(s => ({ ...s, fornecedor_id: v }))} options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} placeholder="Selecione" />
            </div>
            <div className="grid gap-1.5"><Label>Preço de Custo (R$)</Label><Input inputMode="decimal" value={form.preco_custo} onChange={(e) => setForm(s => ({ ...s, preco_custo: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Qtd. em Estoque</Label><Input type="number" value={form.quantidade_estoque} onChange={(e) => setForm(s => ({ ...s, quantidade_estoque: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Estoque Mínimo</Label><Input type="number" value={form.estoque_minimo} onChange={(e) => setForm(s => ({ ...s, estoque_minimo: e.target.value }))} /></div>
            <div className="flex items-center gap-2 mt-6">
              <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-4" />
              <Label>Ativa</Label>
            </div>
            <DialogFooter className="col-span-2 mt-4"><Button type="submit" disabled={salvar.isPending || !form.nome}>{editingId ? "Salvar" : "Cadastrar"}</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Excluir peça?" description="Ação irreversível." confirmLabel="Excluir" destructive pending={excluir.isPending} onConfirm={() => excluirId && excluir.mutate(excluirId)} testId="peca-excluir" />
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend: Estoque atualizado (Cards compactos, Auditoria e UF).")

def criar_relatorio(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "RelatorioEstoque.tsx")
    codigo = r'''import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Package, Search, AlertTriangle, CheckCircle2 } from "lucide-react";
import { apiGet } from "@/lib/api";
import { brl } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function RelatorioEstoque() {
  const [busca, setBusca] = useState("");
  const [filtroFornecedor, setFiltroFornecedor] = useState("__all__");
  const [filtroStatus, setFiltroStatus] = useState("__all__");

  const { data: pecas = [] } = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas") });
  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });

  const filtradas = useMemo(() => {
    return pecas.filter((p: any) => {
      if (busca && !p.nome.toLowerCase().includes(busca.toLowerCase())) return false;
      if (filtroFornecedor !== "__all__" && p.fornecedor_id !== filtroFornecedor) return false;
      
      const baixo = p.quantidade_estoque <= p.estoque_minimo;
      if (filtroStatus === "baixo" && !baixo) return false;
      if (filtroStatus === "ok" && baixo) return false;
      
      return true;
    });
  }, [pecas, busca, filtroFornecedor, filtroStatus]);

  return (
    <div>
      <PageHeader eyebrow="Relatórios" title="Relatório de Estoque" description="Análise detalhada de peças, fornecedores e status." />

      <div className="mb-6 flex flex-wrap gap-3 glass p-4 rounded-xl items-end">
        <div className="w-64">
          <Label>Buscar Peça</Label>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 size-4 text-slate-500" />
            <Input placeholder="Nome da peça..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-8" />
          </div>
        </div>
        <div className="w-56">
          <Label>Fornecedor</Label>
          <FieldSelect value={filtroFornecedor} onChange={setFiltroFornecedor} options={[{ value: "__all__", label: "Todos os Fornecedores" }, ...fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))]} testId="filtro-relatorio-fornecedor" />
        </div>
        <div className="w-48">
          <Label>Status</Label>
          <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: "__all__", label: "Todos" }, { value: "ok", label: "Estoque OK" }, { value: "baixo", label: "Estoque Baixo" }]} testId="filtro-relatorio-status" />
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Peça</TableHead>
              <TableHead>Fornecedor</TableHead>
              <TableHead className="text-center">Qtd. Atual</TableHead>
              <TableHead className="text-center">Qtd. Mín.</TableHead>
              <TableHead className="text-right">Preço Custo</TableHead>
              <TableHead className="text-right">Total em Estoque</TableHead>
              <TableHead className="text-center">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtradas.map((r: any) => {
              const baixo = r.quantidade_estoque <= r.estoque_minimo;
              const forn = fornecedores.find((f: any) => f.id === r.fornecedor_id);
              return (
                <TableRow key={r.id}>
                  <TableCell className="font-medium">
                    {r.nome}
                    <div className="text-xs text-slate-500 font-mono">{r.codigo || "—"}</div>
                  </TableCell>
                  <TableCell className="text-slate-400 text-xs">{forn ? `${forn.nome} ${forn.estado ? `(${forn.estado})` : ''}` : "—"}</TableCell>
                  <TableCell className="text-center font-bold">{r.quantidade_estoque}</TableCell>
                  <TableCell className="text-center">{r.estoque_minimo}</TableCell>
                  <TableCell className="text-right">{brl(r.preco_custo)}</TableCell>
                  <TableCell className="text-right font-bold text-amber-400">{brl(r.preco_custo * r.quantidade_estoque)}</TableCell>
                  <TableCell className="text-center">
                    {baixo ? <span className="text-[10px] font-bold bg-red-500/20 text-red-400 px-2 py-0.5 rounded inline-flex gap-1 items-center"><AlertTriangle className="size-3"/> Baixo</span> : <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded inline-flex gap-1 items-center"><CheckCircle2 className="size-3"/> OK</span>}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Tela de Relatório de Estoque criada.")

def fix_rotas_menu(raiz):
    # 1. Rota App.tsx
    caminho_app = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(caminho_app, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'import RelatorioEstoque' not in c:
        c = c.replace('import Estoque from', 'import RelatorioEstoque from "@/pages/RelatorioEstoque";\nimport Estoque from')
    if '/relatorios/estoque' not in c:
        c = c.replace('<Route path="/relatorios/fornecedores"', '<Route path="/relatorios/estoque" element={<RelatorioEstoque />} />\n              <Route path="/relatorios/fornecedores"')
    with open(caminho_app, 'w', encoding='utf-8') as f:
        f.write(c)

    # 2. Menu Sidebar.tsx
    caminho_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(caminho_sidebar, 'r', encoding='utf-8') as f:
        c = f.read()
    if '/relatorios/estoque' not in c:
        c = c.replace('{ label: "Performance de Fornecedores", icon: BarChart3, path: "/relatorios/fornecedores" },', '{ label: "Performance de Fornecedores", icon: BarChart3, path: "/relatorios/fornecedores" },\n      { label: "Relatório de Estoque", icon: Package, path: "/relatorios/estoque" },')
    with open(caminho_sidebar, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Rotas e Menu atualizados com o Relatório de Estoque.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend_estoque(raiz)
    criar_relatorio(raiz)
    fix_rotas_menu(raiz)