import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Check, X } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function Combustiveis() {
  const qc = useQueryClient();
  const [nome, setNome] = useState("");
  const [isArla, setIsArla] = useState(false);

  const q = useQuery({ queryKey: ["combustiveis"], queryFn: () => apiGet<any[]>("/combustiveis") });
  const rows = q.data ?? [];

  const criar = useMutation({
    mutationFn: () => apiPost("/combustiveis", { nome, is_arla: isArla, ativo: true }),
    onSuccess: () => { toast.success("Cadastrado"); setNome(""); setIsArla(false); qc.invalidateQueries({ queryKey: ["combustiveis"] }); },
    onError: (e: any) => toast.error(e.message),
  });

  return (
    <div>
      <PageHeader eyebrow="Cadastros" title="Tipos de Combustível" description="Gerencie os combustíveis. Arla não entra no cálculo de média." />
      <div className="mb-6 flex items-end gap-3 glass p-4 rounded-xl">
        <div className="grid gap-1.5 flex-1">
          <Label>Nome do Combustível</Label>
          <Input value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Ex: Diesel S-10" />
        </div>
        <div className="flex items-center gap-2 mb-2">
          <input type="checkbox" checked={isArla} onChange={(e) => setIsArla(e.target.checked)} className="size-4" />
          <Label>É Arla? (Não calcula média)</Label>
        </div>
        <Button onClick={() => criar.mutate()} disabled={!nome}><Plus className="size-4 mr-2" /> Adicionar</Button>
      </div>
      <div className="glass rounded-2xl overflow-hidden">
        <Table>
          <TableHeader><TableRow><TableHead>Nome</TableHead><TableHead>É Arla?</TableHead></TableRow></TableHeader>
          <TableBody>
            {rows.map(r => (
              <TableRow key={r.id}>
                <TableCell>{r.nome}</TableCell>
                <TableCell>{r.is_arla ? "Sim" : "Não"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
