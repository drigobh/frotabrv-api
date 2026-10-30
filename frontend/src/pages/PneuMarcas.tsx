import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Tag } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

const TIPOS_MARCA = [
  { value: "FABRICANTE_NOVO", label: "Fabricante de Pneu Novo" },
  { value: "SISTEMA_REFORMA", label: "Sistema de Reforma (Recapagem)" },
  { value: "AMBOS", label: "Ambos (Novo e Reforma)" },
];

const TIERS = [
  { value: "TIER_1", label: "Tier 1 (Premium)" },
  { value: "TIER_2", label: "Tier 2 (Intermediário)" },
  { value: "TIER_3", label: "Tier 3 (Econômico)" },
];

export default function PneuMarcas() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [form, setForm] = useState({ nome: "", tipo: "FABRICANTE_NOVO", tier: "TIER_1" });

  const { data: marcas = [] } = useQuery({ queryKey: ["pneu-marcas"], queryFn: () => apiGet<any[]>("/pneu-marcas") });
  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });

  const seed = useMutation({
    mutationFn: () => apiPost("/pneu-marcas/seed", {}),
    onSuccess: () => { toast.success("Marcas populadas!"); qc.invalidateQueries({ queryKey: ["pneu-marcas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const popularMarcas = () => {
    if (confirm("Isso vai adicionar as marcas padrão de pneus. Continuar?")) {
      seed.mutate();
    }
  };

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/pneu-marcas/${editingId}`, form) : apiPost("/pneu-marcas", form),
    onSuccess: () => { toast.success("Marca salva!"); setOpen(false); qc.invalidateQueries({ queryKey: ["pneu-marcas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneu-marcas/${id}`),
    onSuccess: () => { toast.success("Marca excluída."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pneu-marcas"] }); }
  });

  const abrirNovo = () => { setEditingId(null); setForm({ nome: "", tipo: "FABRICANTE_NOVO", tier: "TIER_1" }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ ...r }); setOpen(true); };

  return (
    <div>
      <PageHeader 
        eyebrow="Cadastros" 
        title="Marcas de Pneus" 
        description="Catálogo de fabricantes e sistemas de reforma." 
        actions={
          <div className="flex gap-2">
            {config?.mostrar_seed_marcas && (
              <Button variant="outline" onClick={popularMarcas} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
                {seed.isPending ? "Populando..." : "Popular Marcas"}
              </Button>
            )}
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Marca</Button>
          </div>
        } 
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Nome</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tier</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {marcas.map((m: any) => (
              <TableRow key={m.id} className="border-slate-800 hover:bg-slate-800/30">
                <TableCell className="font-medium text-slate-200">{m.nome}</TableCell>
                <TableCell className="text-slate-400">{m.tipo === "FABRICANTE_NOVO" ? "Novo" : m.tipo === "SISTEMA_REFORMA" ? "Reforma" : "Ambos"}</TableCell>
                <TableCell className="text-slate-400">{m.tier ? m.tier.replace("TIER_", "Tier ") : "—"}</TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(m)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(m.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Marca" : "Nova Marca"}</h2>
            <div className="grid gap-4">
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Nome *</Label><Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: Michelin" /></div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Tipo</Label>
                <FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_MARCA} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-500">Tier de Mercado</Label>
                <FieldSelect value={form.tier} onChange={(v) => setForm(s => ({ ...s, tier: v }))} options={TIERS} />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar"}</Button>
            </div>
          </div>
        </div>
      )}

      {excluirId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Marca?</h2>
            <div className="flex justify-end gap-3 mt-4">
              <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
              <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
