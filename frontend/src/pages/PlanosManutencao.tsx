import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Wrench, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { useVeiculos } from "@/hooks/useCadastros";

const FAMILIAS = ["Lubrificação e Filtros", "Linha Pesada e Transmissão", "Segurança e Rodagem", "Sistemas de Emissões", "Outros"];
const TIPOS_GATILHO = [
  { value: "km", label: "Por Quilometragem (KM)" },
  { value: "horas", label: "Por Horímetro (Horas)" },
  { value: "dias", label: "Por Tempo (Dias)" }
];

export default function PlanosManutencao() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  
  const veiculos = useVeiculos();
  const { data: planos = [], refetch } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });

  const [form, setForm] = useState({
    veiculo_id: "", familia: FAMILIAS[0], descricao: "", tipo_gatilho: "km", intervalo: "", ultima_execucao_km: "", ultima_execucao_data: ""
  });

  const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        ...form,
        intervalo: Number(form.intervalo),
        ultima_execucao_km: form.ultima_execucao_km ? Number(form.ultima_execucao_km) : null
      };
      return editingId ? apiPut(`/planos-manutencao/${editingId}`, payload) : apiPost("/planos-manutencao", payload);
    },
    onSuccess: () => { toast.success("Plano salvo!"); setOpen(false); qc.invalidateQueries({ queryKey: ["planos-manutencao"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/planos-manutencao/${id}`),
    onSuccess: () => { toast.success("Plano excluído."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["planos-manutencao"] }); }
  });

  const abrirNovo = () => {
    setEditingId(null);
    setForm({ veiculo_id: "", familia: FAMILIAS[0], descricao: "", tipo_gatilho: "km", intervalo: "", ultima_execucao_km: "", ultima_execucao_data: "" });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({ ...r, intervalo: String(r.intervalo), ultima_execucao_km: String(r.ultima_execucao_km || "") });
    setOpen(true);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Cadastro de Planos Preventivos"
        description="Defina os gatilhos e intervalos por família de componentes."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Plano</Button>}
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Família</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Descrição</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Gatilho</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {planos.map((p: any) => (
              <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                <TableCell className="text-slate-200 font-medium">{p.veiculo_label}</TableCell>
                <TableCell className="text-slate-400">{p.familia}</TableCell>
                <TableCell className="text-slate-400">{p.descricao}</TableCell>
                <TableCell className="text-xs text-slate-400">
                  A cada {p.intervalo} {p.tipo_gatilho === 'km' ? 'km' : p.tipo_gatilho === 'horas' ? 'horas' : 'dias'}
                </TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(p)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(p.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Plano" : "Novo Plano"}</h2>
            
            <div className="space-y-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Veículo</Label>
                <FieldSelect value={form.veiculo_id} onChange={(v) => setForm(s => ({ ...s, veiculo_id: v }))} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione..." />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Família de Componentes</Label>
                <select value={form.familia} onChange={(e) => setForm(s => ({ ...s, familia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                  {FAMILIAS.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Descrição do Serviço</Label>
                <Input value={form.descricao} onChange={(e) => setForm(s => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Troca de óleo e filtro" />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Tipo de Gatilho</Label>
                  <select value={form.tipo_gatilho} onChange={(e) => setForm(s => ({ ...s, tipo_gatilho: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                    {TIPOS_GATILHO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Intervalo</Label>
                  <Input type="number" value={form.intervalo} onChange={(e) => setForm(s => ({ ...s, intervalo: e.target.value }))} placeholder={form.tipo_gatilho === 'km' ? "Ex: 20000" : form.tipo_gatilho === 'horas' ? "Ex: 500" : "Ex: 180"} />
                </div>
              </div>

              {form.tipo_gatilho === 'km' && (
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Última Execução (KM)</Label>
                  <Input type="number" value={form.ultima_execucao_km} onChange={(e) => setForm(s => ({ ...s, ultima_execucao_km: e.target.value }))} />
                </div>
              )}
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
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Plano?</h2>
            <p className="text-sm text-slate-400 mb-6">Tem certeza que deseja remover este plano preventivo?</p>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
              <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
