import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link2, Plus, Pencil, Trash2 } from "lucide-react";
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
import { useMotoristas, useVeiculos } from "@/hooks/useCadastros";

export default function Acoplamentos() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const q = useQuery({ queryKey: ["acoplamentos"], queryFn: () => apiGet<any[]>("/acoplamentos") });
  const rows = q.data ?? [];
  const [form, setForm] = useState({ veiculo_id: "", motorista_id: "", data_inicio: "", data_fim: "" });

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/acoplamentos/${editingId}`, form) : apiPost("/acoplamentos", form),
    onSuccess: () => { toast.success("Salvo"); setOpen(false); setEditingId(null); qc.invalidateQueries({ queryKey: ["acoplamentos"] }); },
    onError: (e: any) => toast.error(e.message || "Erro"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/acoplamentos/${id}`),
    onSuccess: () => { toast.success("Removido"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["acoplamentos"] }); },
  });

  const abrirNovo = () => { setEditingId(null); setForm({ veiculo_id: "", motorista_id: "", data_inicio: new Date().toISOString().split("T")[0], data_fim: "" }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ veiculo_id: r.veiculo_id, motorista_id: r.motorista_id, data_inicio: r.data_inicio, data_fim: r.data_fim || "" }); setOpen(true); };

  return (
    <div>
      <PageHeader eyebrow="Operação" title="Acoplamentos" description="Vincule motoristas aos veículos." actions={<Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Novo</Button>} />
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead>Veículo</TableHead><TableHead>Motorista</TableHead><TableHead>Início</TableHead><TableHead>Fim</TableHead><TableHead className="text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((r: any) => (
              <TableRow key={r.id}>
                <TableCell>{r.veiculo_label}</TableCell>
                <TableCell>{r.motorista_label}</TableCell>
                <TableCell>{r.data_inicio}</TableCell>
                <TableCell>{r.data_fim || "—"}</TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Acoplamento</DialogTitle></DialogHeader>
          <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <FieldSelect value={form.veiculo_id} onChange={(v) => setForm(s => ({ ...s, veiculo_id: v }))} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: v.placa }))} placeholder="Veículo" />
            <FieldSelect value={form.motorista_id} onChange={(v) => setForm(s => ({ ...s, motorista_id: v }))} options={(motoristas.data ?? []).map((m: any) => ({ value: m.id, label: m.nome }))} placeholder="Motorista" />
            <Input type="date" value={form.data_inicio} onChange={(e) => setForm(s => ({ ...s, data_inicio: e.target.value }))} />
            <DialogFooter><Button type="submit">Salvar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Remover?" onConfirm={() => excluirId && excluir.mutate(excluirId)} confirmLabel="Remover" destructive pending={excluir.isPending} testId="excluir" />
    </div>
  );
}
