import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function ModelosPneus() {
  const qc = useQueryClient();
  const [novoModelo, setNovoModelo] = useState("");

  // Busca a configuração de parametrização para saber se o botão deve aparecer
  const { data: config } = useQuery({ 
    queryKey: ["parametrizacao-meta"], 
    queryFn: () => apiGet<any>("/parametrizacao/meta") 
  });

  // Busca os modelos cadastrados
  const { data: modelos = [] } = useQuery({ 
    queryKey: ["modelos-pneus"], 
    queryFn: () => apiGet<any[]>("/pneus/modelos") 
  });

  // Mutation para criar um modelo individual
  const criar = useMutation({
    mutationFn: () => apiPost("/pneus/modelos", { nome: novoModelo }),
    onSuccess: () => {
      toast.success("Modelo cadastrado!");
      setNovoModelo("");
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao cadastrar.")
  });

  // Mutation para excluir um modelo
  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneus/modelos/${id}`),
    onSuccess: () => {
      toast.success("Modelo excluído.");
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    }
  });

  // Mutation para popular os dados iniciais
  const popular = useMutation({
    mutationFn: () => apiPost("/pneus/seed", {}),
    onSuccess: () => {
      toast.success("Modelos populados com sucesso!");
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    }
  });

  return (
    <div>
      <PageHeader 
        eyebrow="Cadastros" 
        title="Modelos de Pneus" 
        description="Gerencie os modelos de pneus disponíveis no sistema." 
        actions={
          config?.mostrar_seed_modelos && (
            <Button 
              onClick={() => popular.mutate()} 
              disabled={popular.isPending} 
              variant="outline" 
              className="border-amber-500/40 text-amber-500 hover:bg-amber-500/10 h-9"
            >
              <RefreshCw className={`size-4 mr-2 ${popular.isPending ? 'animate-spin' : ''}`} /> 
              Popular Modelos
            </Button>
          )
        }
      />

      <div className="glass p-4 rounded-xl mb-4 flex items-end gap-3">
        <div className="grid gap-1.5 flex-1 max-w-sm">
          <Label className="text-xs text-slate-400">Novo Modelo</Label>
          <Input 
            value={novoModelo} 
            onChange={(e) => setNovoModelo(e.target.value)} 
            placeholder="Ex: X Multi Z" 
            onKeyDown={(e) => e.key === 'Enter' && novoModelo && criar.mutate()} 
          />
        </div>
        <Button 
          onClick={() => criar.mutate()} 
          disabled={!novoModelo || criar.isPending} 
          className="bg-sky-600 hover:bg-sky-500 h-9"
        >
          <Plus className="size-4 mr-2" /> Adicionar
        </Button>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Modelo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center w-[100px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {modelos.length === 0 ? (
              <TableRow>
                <TableCell colSpan={2} className="text-center py-6 text-slate-500">
                  Nenhum modelo encontrado.
                </TableCell>
              </TableRow>
            ) : (
              modelos.map((item: any) => (
                <TableRow key={item.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="font-medium text-slate-200">{item.nome}</TableCell>
                  <TableCell className="text-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => excluir.mutate(item.id)}>
                      <Trash2 className="size-4 text-red-300" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}