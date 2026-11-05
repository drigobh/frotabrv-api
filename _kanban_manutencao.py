import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Manutencoes.tsx")

conteudo = r'''import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { 
  Check, Clock, Plus, X 
} from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { brl } from "@/lib/format";
import { cn } from "@/lib/utils";

const COLUNAS = [
  { id: "Aguardando aprovação", label: "Aguardando Aprovação", color: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/30" },
  { id: "Aguardando peça", label: "Aguardando Peça", color: "text-sky-500", bg: "bg-sky-500/10", border: "border-sky-500/30" },
  { id: "Em execução", label: "Em Execução", color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/30" },
  { id: "Concluída", label: "Concluída", color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30" },
];

export default function Manutencoes() {
  const qc = useQueryClient();
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });

  const alterarStatus = useMutation({
    mutationFn: ({ id, novo_status }: { id: string, novo_status: string }) => {
      return apiPut(`/manutencoes/${id}`, { status: novo_status });
    },
    onSuccess: () => {
      toast.success("Status atualizado com sucesso!");
      qc.invalidateQueries({ queryKey: ["manutencoes"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao atualizar.")
  });

  const getCards = (status: string) => {
    return manutencoes.filter((m: any) => m.status === status);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Gestão de Manutenção"
        description="Aprove ordens de serviço, acompanhe peças e libere veículos."
        actions={
          <Button className="bg-sky-600 hover:bg-sky-500 h-9">
            <Plus className="size-4 mr-2" /> Nova OS
          </Button>
        }
      />

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        {COLUNAS.map((col) => (
          <div key={col.id} className={cn("glass p-3 rounded-xl border", col.border, "bg-slate-900/50")}>
            <p className={cn("text-[11px] uppercase tracking-widest font-bold", col.color)}>{col.label}</p>
            <p className="mt-2 font-mono text-2xl font-bold text-slate-100">{getCards(col.id).length}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 items-start">
        {COLUNAS.map((col) => {
          const cards = getCards(col.id);
          return (
            <div key={col.id} className={cn("rounded-2xl border p-3 flex flex-col gap-3", col.border, col.bg)}>
              <div className="flex items-center justify-between px-1">
                <h3 className={cn("text-xs font-bold uppercase tracking-wider", col.color)}>{col.label}</h3>
                <span className="text-xs font-mono text-slate-400">{cards.length}</span>
              </div>

              <div className="flex flex-col gap-3">
                {cards.length === 0 ? (
                  <div className="text-center py-6 text-xs text-slate-500 border border-dashed border-slate-700 rounded-lg">
                    Nenhuma OS nesta etapa.
                  </div>
                ) : (
                  cards.map((m: any) => (
                    <div key={m.id} className="glass p-4 rounded-xl border border-slate-700/50 bg-slate-900/80 hover:border-slate-500 transition-colors shadow-lg">
                      <div className="flex items-start justify-between mb-2">
                        <span className="font-mono text-[10px] font-bold text-slate-400">{m.id.slice(0,6).toUpperCase()}</span>
                        <span className="text-[10px] text-slate-500">{m.veiculo_placa || "Veículo"}</span>
                      </div>
                      
                      <p className="text-sm font-bold text-slate-200 leading-snug mb-1">{m.descricao || "Manutenção"}</p>
                      <p className="text-xs text-slate-400 line-clamp-2 mb-3">{m.fornecedor_nome || "Fornecedor"}</p>
                      
                      <div className="flex items-center justify-between border-t border-slate-800 pt-3 mt-1">
                        <span className="font-mono text-sm font-bold text-slate-100">{brl(m.valor || 0)}</span>
                        
                        {col.id === "Aguardando aprovação" && (
                          <div className="flex gap-1">
                            <Button size="icon" variant="ghost" className="size-7 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400" onClick={() => alterarStatus.mutate({ id: m.id, novo_status: "Em execução" })}>
                              <Check className="size-3.5" />
                            </Button>
                            <Button size="icon" variant="ghost" className="size-7 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400" onClick={() => alterarStatus.mutate({ id: m.id, novo_status: "Concluída" })}>
                              <X className="size-3.5" />
                            </Button>
                          </div>
                        )}
                        {col.id === "Em execução" && (
                          <Button size="sm" variant="outline" className="text-[10px] h-7 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10" onClick={() => alterarStatus.mutate({ id: m.id, novo_status: "Concluída" })}>
                            Concluir
                          </Button>
                        )}
                      </div>
                      
                      <div className="mt-3 flex items-center gap-1 text-[10px] text-slate-500">
                        <Clock className="size-3" /> 
                        <span>Aguardando atualização...</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
'''
with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✅ Tela do Kanban (Manutencoes.tsx) reescrita!")