import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Disc } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function PneuMedidas() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [form, setForm] = useState({ codigo: "", aro: "", tipo_construcao: "RADIAL", requer_camara: false });

  const { data: medidas = [] } = useQuery({ queryKey: ["pneu-medidas"], queryFn: () => apiGet<any[]>("/pneu-medidas") });

  const seed = useMutation({
    mutationFn: () => apiPost("/pneu-medidas/seed", {}),
    onSuccess: () => { toast.success("Medidas populadas!"); qc.invalidateQueries({ queryKey: ["pneu-medidas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const popularMedidas = () => {
    if (confirm("Isso vai adicionar as medidas padrão de pneus. Continuar?")) {
      seed.mutate();
    }
  };

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/pneu-medidas/${editingId}`, form) : apiPost("/pneu-medidas", form),
    onSuccess: () => { toast.success("Medida salva!"); setOpen(false); qc.invalidateQueries({ queryKey: ["pneu-medidas"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneu-medidas/${id}`),
    onSuccess: () => { toast.success("Medida excluída."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pneu-medidas"] }); }
  });

  const abrirNovo = () => { setEditingId(null); setForm({ codigo: "", aro: "", tipo_construcao: "RADIAL", requer_camara: false }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ ...r }); setOpen(true); };

  return (
    <div>
      <PageHeader eyebrow="Cadastros" title="Medidas de Pneus" description="Catálogo de medidas padronizadas." actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={popularMedidas} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
              {seed.isPending ? "Populando..." : "Popular Medidas"}
            </Button>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Medida</Button>
          </div>
        } />
      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader><TableRow className="border-slate-800"><TableHead className="text-xs uppercase text-slate-500">Código</TableHead><TableHead className="text-xs uppercase text-slate-500">Aro</TableHead><TableHead className="text-xs uppercase text-slate-500">Construção</TableHead><TableHead className="text-xs uppercase text-slate-500">Câmara</TableHead><TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead></TableRow></TableHeader>
          <TableBody>
            {medidas.map((m: any) => (
              <TableRow key={m.id} className="border-slate-800 hover:bg-slate-800/30">
                <TableCell className="font-mono text-slate-200">{m.codigo}</TableCell>
                <TableCell className="text-slate-400">{m.aro}"</TableCell>
                <TableCell className="text-slate-400">{m.tipo_construcao}</TableCell>
                <TableCell className="text-slate-400">{m.requer_camara ? "Sim" : "Não"}</TableCell>
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
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Medida" : "Nova Medida"}</h2>
            <div className="grid gap-4">
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Código *</Label><Input value={form.codigo} onChange={(e) => setForm(s => ({ ...s, codigo: e.target.value }))} placeholder="Ex: 295/80 R22.5" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Aro *</Label><Input value={form.aro} onChange={(e) => setForm(s => ({ ...s, aro: e.target.value }))} placeholder="Ex: 22.5" /></div>
              <div className="grid gap-1.5"><Label className="text-xs text-slate-400">Construção</Label><Input value={form.tipo_construcao} onChange={(e) => setForm(s => ({ ...s, tipo_construcao: e.target.value }))} placeholder="RADIAL" /></div>
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
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Medida?</h2>
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
