import { useState } from "react";
import {Database, Trash2, AlertTriangle, Disc} from "lucide-react";
import { toast } from "sonner";
import {apiPost, apiDelete} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const COLECOES = [
  { id: "veiculos", nome: "Veículos" },
  { id: "carretas", nome: "Carretas" },
  { id: "motoristas", nome: "Motoristas" },
  { id: "acoplamentos", nome: "Acoplamentos" },
  { id: "abastecimentos", nome: "Abastecimentos" },
  { id: "fornecedores", nome: "Fornecedores" },
];

export default function Base() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [colecaoAlvo, setColecaoAlvo] = useState<string | null>(null);
  const [confirmacao, setConfirmacao] = useState("");
  const [pending, setPending] = useState(false);

  const abrirDialogo = (id: string) => {
    setColecaoAlvo(id);
    setConfirmacao("");
    setOpen(true);
  };

  const limparBase = async () => {
    if (confirmacao !== "LIMPAR") {
      toast.error("Digite a palavra LIMPAR para confirmar.");
      return;
    }
    
    setPending(true);
    try {
      await apiPost(`/admin/limpar-base?colecao=${colecaoAlvo}`);
      toast.success(`Base de ${colecaoAlvo} limpa com sucesso! Backups gerados.`);
      setOpen(false);
    } catch (error: any) {
      toast.error(error.message || "Erro ao limpar a base.");
    } finally {
      setPending(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Administração</p>
        <h1 className="text-2xl font-bold text-slate-100 mt-1">Limpeza de Base</h1>
        <p className="text-sm text-slate-400 mt-1">Apague os dados de tabelas específicas. O sistema gera um backup automático.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {COLECOES.map((c) => (
          <div key={c.id} className="glass rounded-xl p-6 border border-slate-800 bg-[#0F172A]">
            <div className="flex items-center gap-2 text-slate-200 mb-2">
              <Database className="size-5 text-sky-400" />
              <h3 className="text-lg font-semibold">{c.nome}</h3>
            </div>
            <p className="text-sm text-slate-400 mb-4">Apaga todos os registros da tabela.</p>
            <Button variant="destructive" className="w-full" onClick={() => abrirDialogo(c.id)}>
              <Trash2 className="size-4 mr-2" /> Limpar {c.nome}
            </Button>
          </div>
        ))}
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-400">
              <AlertTriangle className="size-5" /> Atenção!
            </DialogTitle>
            <DialogDescription>
              Você está prestes a apagar <strong>TODOS</strong> os dados de <strong>{colecaoAlvo}</strong>.
              Um backup será gerado automaticamente, mas esta ação não pode ser desfeita pelo sistema.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-2 py-4">
            <Label>Digite <strong className="text-red-400">LIMPAR</strong> para confirmar:</Label>
            <Input value={confirmacao} onChange={(e) => setConfirmacao(e.target.value)} placeholder="LIMPAR" />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setOpen(false)}>Cancelar</Button>
            <Button variant="destructive" disabled={confirmacao !== "LIMPAR" || pending} onClick={limparBase}>
              {pending ? "Limpando..." : "Confirmar Exclusão"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
