import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Disc, Ruler, Type } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function CadastrosPneus() {
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<"marcas" | "medidas" | "modelos">("marcas");
  const [novoValor, setNovoValor] = useState("");

  const { data: marcas = [] } = useQuery({ queryKey: ["marcas-pneus"], queryFn: () => apiGet<any[]>("/pneus/marcas") });
  const { data: medidas = [] } = useQuery({ queryKey: ["medidas-pneus"], queryFn: () => apiGet<any[]>("/pneus/medidas") });
  const { data: modelos = [] } = useQuery({ queryKey: ["modelos-pneus"], queryFn: () => apiGet<any[]>("/pneus/modelos") });

  const criar = useMutation({
    mutationFn: () => {
      const rota = abaAtiva === 'marcas' ? '/pneus/marcas' : abaAtiva === 'medidas' ? '/pneus/medidas' : '/pneus/modelos';
      const body = abaAtiva === 'medidas' ? { medida: novoValor } : { nome: novoValor };
      return apiPost(rota, body);
    },
    onSuccess: () => {
      toast.success("Cadastro realizado!");
      setNovoValor("");
      qc.invalidateQueries({ queryKey: ["marcas-pneus"] });
      qc.invalidateQueries({ queryKey: ["medidas-pneus"] });
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao cadastrar.")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => {
      const rota = abaAtiva === 'marcas' ? '/pneus/marcas' : abaAtiva === 'medidas' ? '/pneus/medidas' : '/pneus/modelos';
      return apiDelete(`${rota}/${id}`);
    },
    onSuccess: () => {
      toast.success("Cadastro excluído.");
      qc.invalidateQueries({ queryKey: ["marcas-pneus"] });
      qc.invalidateQueries({ queryKey: ["medidas-pneus"] });
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    }
  });

  const listaAtual = abaAtiva === 'marcas' ? marcas : abaAtiva === 'medidas' ? medidas : modelos;

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Tabelas de Pneus"
        description="Gerencie as marcas, medidas e modelos disponíveis no sistema."
      />

      <div className="flex gap-2 mb-4 border-b border-slate-800 pb-2">
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'marcas' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => { setAbaAtiva('marcas'); setNovoValor(''); }}
        >
          <Disc className="size-4 inline mr-2" /> Marcas
        </button>
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'medidas' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => { setAbaAtiva('medidas'); setNovoValor(''); }}
        >
          <Ruler className="size-4 inline mr-2" /> Medidas
        </button>
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'modelos' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => { setAbaAtiva('modelos'); setNovoValor(''); }}
        >
          <Type className="size-4 inline mr-2" /> Modelos
        </button>
      </div>

      <div className="glass p-4 rounded-xl mb-4 flex items-end gap-3">
        <div className="grid gap-1.5 flex-1 max-w-sm">
          <Label className="text-xs text-slate-400">
            Novo {abaAtiva === 'marcas' ? 'Marca' : abaAtiva === 'medidas' ? 'Medida' : 'Modelo'}
          </Label>
          <Input 
            value={novoValor} 
            onChange={(e) => setNovoValor(e.target.value)} 
            placeholder={abaAtiva === 'medidas' ? "Ex: 295/80 R22.5" : "Ex: Michelin"} 
            onKeyDown={(e) => e.key === 'Enter' && novoValor && criar.mutate()}
          />
        </div>
        <Button onClick={() => criar.mutate()} disabled={!novoValor || criar.isPending} className="bg-sky-600 hover:bg-sky-500 h-9">
          <Plus className="size-4 mr-2" /> Adicionar
        </Button>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Nome / Valor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center w-[100px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {listaAtual.length === 0 ? (
              <TableRow><TableCell colSpan={2} className="text-center py-6 text-slate-500">Nenhum registro encontrado.</TableCell></TableRow>
            ) : (
              listaAtual.map((item: any) => (
                <TableRow key={item.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="font-medium text-slate-200">
                    {abaAtiva === 'medidas' ? item.medida : item.nome}
                  </TableCell>
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
