import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "pecas.py")
    codigo = '''from pydantic import BaseModel, Field
from typing import Optional, List

class FornecedorPreco(BaseModel):
    fornecedor_id: str
    preco_atual: float = 0.0
    historico: List[float] = []

class PecaCreate(BaseModel):
    nome: str = Field(min_length=2)
    codigo: Optional[str] = None
    quantidade_estoque: int = 0
    estoque_minimo: int = 5
    fornecedor_atual_id: Optional[str] = None
    fornecedores_precos: List[FornecedorPreco] = []
    ativo: bool = True

class Peca(PecaCreate):
    id: str
    created_by_name: Optional[str] = None
    created_at: Optional[str] = None
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Backend atualizado: Adicionado 'fornecedor_atual_id'.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    
    codigo = r'''import { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Package, Plus, Pencil, Trash2, AlertTriangle, CheckCircle2, Search, MapPin, Info, Star } from "lucide-react";
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

  const [form, setForm] = useState({ nome: "", codigo: "", quantidade_estoque: "", estoque_minimo: "5", fornecedor_atual_id: "", ativo: true });
  const [listaFornecedores, setListaFornecedores] = useState<{ fornecedor_id: string, preco_atual: string, historico: number[] }[]>([]);

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
        quantidade_estoque: Number(form.quantidade_estoque) || 0, 
        estoque_minimo: Number(form.estoque_minimo) || 0,
        fornecedores_precos: listaFornecedores.map(f => ({
          fornecedor_id: f.fornecedor_id,
          preco_atual: Number(f.preco_atual.replace(",", ".")) || 0,
          historico: f.historico
        }))
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
    setForm({ nome: "", codigo: "", quantidade_estoque: "", estoque_minimo: "5", fornecedor_atual_id: "", ativo: true }); 
    setListaFornecedores([]);
    setOpen(true); 
  };

  const abrirEdicao = (r: any) => { 
    setEditingId(r.id); 
    setForm({ 
      nome: r.nome, codigo: r.codigo || "", quantidade_estoque: String(r.quantidade_estoque), 
      estoque_minimo: String(r.estoque_minimo), fornecedor_atual_id: r.fornecedor_atual_id || "", ativo: r.ativo 
    }); 
    setListaFornecedores((r.fornecedores_precos || []).map((f: any) => ({
      fornecedor_id: f.fornecedor_id,
      preco_atual: String(f.preco_atual),
      historico: f.historico || []
    })));
    setOpen(true); 
  };

  const adicionarFornecedor = () => setListaFornecedores([...listaFornecedores, { fornecedor_id: "", preco_atual: "", historico: [] }]);
  const removerFornecedor = (idx: number) => setListaFornecedores(listaFornecedores.filter((_, i) => i !== idx));
  
  const atualizarPreco = (idx: number, novoPreco: string) => {
    const nova = [...listaFornecedores];
    nova[idx].preco_atual = novoPreco;
    setListaFornecedores(nova);
  };

  const registrarPreco = (idx: number) => {
    const nova = [...listaFornecedores];
    const precoNum = Number(nova[idx].preco_atual.replace(",", "."));
    if (isNaN(precoNum) || precoNum <= 0) { toast.error("Preço inválido"); return; }
    
    if (precoNum > 0) {
      nova[idx].historico = [precoNum, ...nova[idx].historico].slice(0, 3);
    }
    nova[idx].preco_atual = "";
    setListaFornecedores(nova);
    toast.success("Preço registrado no histórico!");
  };

  const totalItens = rows.length;
  const itensBaixos = rows.filter(r => r.quantidade_estoque <= r.estoque_minimo).length;
  const valorTotal = rows.reduce((acc, r) => {
    if (!r.fornecedor_atual_id) return acc;
    const fp = (r.fornecedores_precos || []).find((f: any) => f.fornecedor_id === r.fornecedor_atual_id);
    const preco = fp ? fp.preco_atual : 0;
    return acc + (preco * r.quantidade_estoque);
  }, 0);

  const estadosOrigem = new Set(rows.flatMap(r => 
    (r.fornecedores_precos || []).map((fp: any) => {
      const f = fornecedores.find((x: any) => x.id === fp.fornecedor_id);
      return f?.estado;
    })
  ).filter(Boolean)).size;

  return (
    <div>
      <PageHeader eyebrow="Operação" title="Estoque de Peças" description="Controle de almoxarifado." actions={<Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Nova Peça</Button>} />

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
              <TableHead className="text-xs uppercase text-slate-500">Peça / Fornecedores</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Atual</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Qtd. Mínima</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-right">Preço (Compra Atual)</TableHead>
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
              
              // Achar o mais barato do catálogo
              let menorPrecoForn = null;
              if (r.fornecedores_precos && r.fornecedores_precos.length > 0) {
                const validos = r.fornecedores_precos.filter((f:any) => f.fornecedor_id && f.preco_atual > 0);
                if (validos.length > 0) {
                  const menor = validos.reduce((min:any, f:any) => f.preco_atual < min.preco_atual ? f : min, validos[0]);
                  const fObj = fornecedores.find((x:any) => x.id === menor.fornecedor_id);
                  if (fObj) menorPrecoForn = { nome: fObj.nome, preco: menor.preco_atual, avaliacao: fObj.avaliacao };
                }
              }
              
              return (
                <TableRow key={r.id} className="border-slate-800/70">
                  <TableCell className="font-medium text-slate-200">
                    <div>{r.nome}</div>
                    <div className="text-slate-500 font-mono text-xs">{r.codigo || "—"}</div>
                    
                    {fornAtual ? (
                      <div className="text-[10px] text-emerald-400 mt-1">Estoque comprado de: {fornAtual.nome}</div>
                    ) : (
                      <div className="text-[10px] text-slate-500 mt-1">Fornecedor do estoque não informado</div>
                    )}

                    {menorPrecoForn && (
                      <div className="text-[10px] text-sky-400 mt-0.5 flex items-center gap-1">
                        Melhor preço p/ compra: {menorPrecoForn.nome} ({brl(menorPrecoForn.preco)})
                        <span className="flex gap-0.5">
                          {[1,2,3,4,5].map(star => (
                            <Star key={star} className={`size-2.5 ${star <= (menorPrecoForn.avaliacao || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                          ))}
                        </span>
                      </div>
                    )}
                  </TableCell>
                  <TableCell className={`text-center font-bold ${estoqueBaixo ? 'text-red-400' : 'text-emerald-400'}`}>{r.quantidade_estoque}</TableCell>
                  <TableCell className="text-center text-slate-400">{r.estoque_minimo}</TableCell>
                  <TableCell className="text-right text-slate-300">{brl(precoAtual)}</TableCell>
                  <TableCell className="text-right font-medium text-slate-200">{brl(precoAtual * r.quantidade_estoque)}</TableCell>
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
        <DialogContent className="sm:max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Package className="size-5 text-sky-400" /> {editingId ? "Editar Peça" : "Nova Peça"}</DialogTitle></DialogHeader>
          <form className="grid grid-cols-2 gap-4" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            
            {/* Dados Básicos */}
            <div className="col-span-2 md:col-span-1 grid gap-1.5"><Label>Nome da Peça *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} required /></div>
            <div className="col-span-2 md:col-span-1 grid gap-1.5"><Label>Código / Referência</Label><Input value={form.codigo} onChange={(e) => setForm(s => ({ ...s, codigo: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Qtd. em Estoque</Label><Input type="number" value={form.quantidade_estoque} onChange={(e) => setForm(s => ({ ...s, quantidade_estoque: e.target.value }))} /></div>
            <div className="grid gap-1.5"><Label>Estoque Mínimo</Label><Input type="number" value={form.estoque_minimo} onChange={(e) => setForm(s => ({ ...s, estoque_minimo: e.target.value }))} /></div>
            
            {/* Fornecedor do Estoque Atual */}
            <div className="col-span-2 bg-sky-950/30 p-3 rounded-lg border border-sky-900/50">
              <Label className="text-sky-400 font-semibold mb-2 block">Fornecedor da Compra Atual</Label>
              <p className="text-[11px] text-slate-400 mb-2">De qual fornecedor você comprou as {form.quantidade_estoque || "0"} peças que estão no estoque agora?</p>
              <FieldSelect 
                value={form.fornecedor_atual_id} 
                onChange={(v) => setForm(s => ({ ...s, fornecedor_atual_id: v }))} 
                options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} 
                placeholder="Selecione o fornecedor da compra atual" 
              />
            </div>
            
            {/* Catálogo de Cotações */}
            <div className="col-span-2 border-t border-slate-800 pt-3 mt-2">
              <div className="flex justify-between items-center mb-3">
                <div>
                  <Label className="text-sm font-semibold text-slate-200">Catálogo de Fornecedores e Cotações</Label>
                  <p className="text-[10px] text-slate-500">Adicione os fornecedores que vendem esta peça para comparar preços.</p>
                </div>
                <Button type="button" variant="outline" size="sm" onClick={adicionarFornecedor}><Plus className="size-3 mr-1" /> Adicionar Cotação</Button>
              </div>
              
              {listaFornecedores.length === 0 ? (
                <p className="text-xs text-slate-500 italic">Nenhum fornecedor cadastrado no catálogo.</p>
              ) : (
                <div className="space-y-3">
                  {listaFornecedores.map((lf, idx) => {
                    const fornObj = fornecedores.find((x:any) => x.id === lf.fornecedor_id);
                    // Descobre o menor preço do catálogo para dar o selo
                    const precosValidos = listaFornecedores.map(f => Number(f.preco_atual.replace(",", ".")) || Infinity);
                    const menorPrecoGeral = Math.min(...precosValidos);
                    const isMenorPreco = Number(lf.preco_atual.replace(",", ".")) === menorPrecoGeral && menorPrecoGeral !== Infinity;

                    return (
                      <div key={idx} className={`flex flex-col md:flex-row gap-2 bg-slate-900/50 p-2 rounded border items-end ${isMenorPreco ? 'border-emerald-500/50' : 'border-slate-800'}`}>
                        <div className="flex-1 grid gap-1">
                          <Label className="text-[10px] text-slate-400 flex items-center gap-2">
                            Fornecedor
                            {isMenorPreco && <span className="bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded text-[9px]">Menor Preço</span>}
                          </Label>
                          <FieldSelect 
                            value={lf.fornecedor_id} 
                            onChange={(v) => {
                              const nova = [...listaFornecedores];
                              nova[idx].fornecedor_id = v;
                              setListaFornecedores(nova);
                            }} 
                            options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} 
                            placeholder="Selecione" 
                          />
                          {fornObj && (
                            <div className="flex gap-0.5 ml-1">
                              {[1,2,3,4,5].map(star => (
                                <Star key={star} className={`size-3 ${star <= (fornObj.avaliacao || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                              ))}
                            </div>
                          )}
                        </div>
                        <div className="w-28 grid gap-1">
                          <Label className="text-[10px] text-slate-400">Preço Atual</Label>
                          <Input value={lf.preco_atual} onChange={(e) => atualizarPreco(idx, e.target.value)} placeholder="R$ 0,00" />
                        </div>
                        <Button type="button" variant="secondary" size="sm" onClick={() => registrarPreco(idx)} className="h-9" title="Registrar no Histórico">
                          Histórico
                        </Button>
                        <div className="flex-1 grid gap-1">
                          <Label className="text-[10px] text-slate-400">Últimos 3 Preços</Label>
                          <div className="flex gap-1 h-9 items-center">
                            {lf.historico.length === 0 ? <span className="text-xs text-slate-600">—</span> : lf.historico.map((h, i) => <span key={i} className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400">{brl(h)}</span>)}
                          </div>
                        </div>
                        <Button type="button" variant="ghost" size="icon" className="text-red-400 h-9" onClick={() => removerFornecedor(idx)}>
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="flex items-center gap-2 mt-2">
              <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-4" />
              <Label>Peça Ativa</Label>
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
    print("✅ Estoque.tsx reescrito: Separado Fornecedor Atual do Catálogo, com Estrelas e Melhor Preço.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)