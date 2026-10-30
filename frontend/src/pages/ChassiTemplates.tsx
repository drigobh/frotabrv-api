import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Layers } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

const CATEGORIAS = [
  { value: "CAVALO", label: "Cavalo Mecânico" },
  { value: "CARRETA", label: "Carreta / Semirreboque" },
];

const FUNCOES = [
  { value: "DIRECIONAL", label: "Direcional" },
  { value: "TRACAO", label: "Tração" },
  { value: "TRUCK", label: "Truck Auxiliar" },
  { value: "LIVRE", label: "Livre (Carreta)" },
];

const RODAGENS = [
  { value: "SIMPLES", label: "Simples (2 pneus)" },
  { value: "DUPLA", label: "Dupla (4 pneus)" },
];

export default function ChassiTemplates() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [form, setForm] = useState({ nome: "", categoria: "CAVALO", qtd_estepes: 0, eixos: [] as any[] });

  const { data: templates = [] } = useQuery({ queryKey: ["chassi-templates"], queryFn: () => apiGet<any[]>("/chassi-templates") });
  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });

  const seed = useMutation({
    mutationFn: () => apiPost("/chassi-templates/seed", {}),
    onSuccess: () => { toast.success("Templates populados!"); qc.invalidateQueries({ queryKey: ["chassi-templates"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/chassi-templates/${editingId}`, form) : apiPost("/chassi-templates", form),
    onSuccess: () => { toast.success("Template salvo!"); setOpen(false); qc.invalidateQueries({ queryKey: ["chassi-templates"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/chassi-templates/${id}`),
    onSuccess: () => { toast.success("Template excluído."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["chassi-templates"] }); }
  });

  const abrirNovo = () => { setEditingId(null); setForm({ nome: "", categoria: "CAVALO", qtd_estepes: 0, eixos: [] }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ ...r, eixos: r.eixos || [] }); setOpen(true); };

  const addEixo = () => {
    setForm(s => ({
      ...s,
      eixos: [...s.eixos, { numero_eixo: s.eixos.length + 1, tipo_rodagem: "DUPLA", funcao_mecanica: "LIVRE", tem_suspensor: false }]
    }));
  };

  const removeEixo = (idx: number) => {
    setForm(s => ({
      ...s,
      eixos: s.eixos.filter((_: any, i: number) => i !== idx).map((e: any, i: number) => ({ ...e, numero_eixo: i + 1 }))
    }));
  };

  const updateEixo = (idx: number, campo: string, valor: any) => {
    setForm(s => {
      const novos = [...s.eixos];
      novos[idx] = { ...novos[idx], [campo]: valor };
      return { ...s, eixos: novos };
    });
  };

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Templates de Chassi"
        description="Configurador topológico de eixos e estepes."
        actions={<div className="flex gap-2">
          {config?.mostrar_seed_templates && (
            <Button variant="outline" onClick={() => { if(confirm("Adicionar templates padrão?")) seed.mutate(); }} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
              {seed.isPending ? "Populando..." : "Popular Templates"}
            </Button>
          )}
          <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Template</Button>
        </div>}
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Nome</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Categoria</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Eixos</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Estepes</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {templates.map((t: any) => (
              <TableRow key={t.id} className="border-slate-800 hover:bg-slate-800/30">
                <TableCell className="font-medium text-slate-200">{t.nome}</TableCell>
                <TableCell className="text-slate-400">{t.categoria === "CAVALO" ? "Cavalo" : "Carreta"}</TableCell>
                <TableCell className="text-slate-400">{t.eixos?.length || 0}</TableCell>
                <TableCell className="text-slate-400">{t.qtd_estepes}</TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(t)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(t.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Template" : "Novo Template"}</h2>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">Nome do Template *</Label>
                <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: Cavalo 6x2 Trucado Standard" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Categoria</Label>
                <FieldSelect value={form.categoria} onChange={(v) => setForm(s => ({ ...s, categoria: v }))} options={CATEGORIAS} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Qtd. Estepes</Label>
                <Input type="number" value={form.qtd_estepes} onChange={(e) => setForm(s => ({ ...s, qtd_estepes: Number(e.target.value) }))} />
              </div>
            </div>

            <div className="border-t border-slate-800 pt-4">
              <div className="flex justify-between items-center mb-3">
                <Label className="text-sm font-bold text-slate-200">Configuração dos Eixos</Label>
                <Button type="button" variant="outline" size="sm" onClick={addEixo}><Plus className="size-3 mr-1" /> Adicionar Eixo</Button>
              </div>
              {form.eixos.length === 0 ? (
                <p className="text-xs text-slate-500 italic text-center py-4">Nenhum eixo adicionado. Clique em "Adicionar Eixo".</p>
              ) : (
                <div className="space-y-3">
                  {form.eixos.map((e: any, idx: number) => (
                    <div key={idx} className="flex gap-3 items-end bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                      <div className="grid gap-1 w-16"><Label className="text-[10px] text-slate-500">Eixo</Label><Input value={e.numero_eixo} disabled className="text-center h-8" /></div>
                      <div className="grid gap-1 flex-1"><Label className="text-[10px] text-slate-500">Rodagem</Label><FieldSelect value={e.tipo_rodagem} onChange={(v) => updateEixo(idx, "tipo_rodagem", v)} options={RODAGENS} /></div>
                      <div className="grid gap-1 flex-1"><Label className="text-[10px] text-slate-500">Função</Label><FieldSelect value={e.funcao_mecanica} onChange={(v) => updateEixo(idx, "funcao_mecanica", v)} options={FUNCOES} /></div>
                      <div className="grid gap-1 w-24"><Label className="text-[10px] text-slate-500">Suspensor</Label>
                        <FieldSelect value={e.tem_suspensor ? "sim" : "nao"} onChange={(v) => updateEixo(idx, "tem_suspensor", v === "sim")} options={[{ value: "nao", label: "Não" }, { value: "sim", label: "Sim" }]} />
                      </div>
                      <Button type="button" variant="ghost" size="icon" onClick={() => removeEixo(idx)}><Trash2 className="size-4 text-red-400" /></Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar Template"}</Button>
            </div>
          </div>
        </div>
      )}

      {excluirId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Template?</h2>
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
