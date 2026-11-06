import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Building2, Tag, X, Check } from "lucide-react";
import { apiGet, apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function CadastrosFinanceiros() {
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<"Bancos" | "Categorias">("Bancos");
  
  // Estados para Bancos
  const [modalBancoOpen, setModalBancoOpen] = useState(false);
  const [formBanco, setFormBanco] = useState({ nome: "", agencia: "", conta: "", saldo_inicial: "" });
  
  // Estados para Categorias
  const [modalCatOpen, setModalCatOpen] = useState(false);
  const [formCat, setFormCat] = useState({ nome: "", tipo: "Ambos" });

  const { data: bancos = [] } = useQuery({ queryKey: ["bancos"], queryFn: () => apiGet<any[]>("/cadastros-financeiros/bancos") });
  const { data: categorias = [] } = useQuery({ queryKey: ["categorias-financeiras"], queryFn: () => apiGet<any[]>("/cadastros-financeiros/categorias") });

  const salvarBanco = useMutation({
    mutationFn: (payload: any) => apiPost("/cadastros-financeiros/bancos", payload),
    onSuccess: () => {
      toast.success("Banco cadastrado!");
      setModalBancoOpen(false);
      qc.invalidateQueries({ queryKey: ["bancos"] });
    }
  });

  const salvarCat = useMutation({
    mutationFn: (payload: any) => apiPost("/cadastros-financeiros/categorias", payload),
    onSuccess: () => {
      toast.success("Categoria cadastrada!");
      setModalCatOpen(false);
      qc.invalidateQueries({ queryKey: ["categorias-financeiras"] });
    }
  });

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Financeiro"
        description="Gerencie os bancos e as categorias de lançamento."
      />

      <div className="flex gap-1 bg-slate-900/50 p-1 rounded-lg mb-4 w-fit border border-slate-800">
        <button onClick={() => setAbaAtiva("Bancos")} className={cn("px-4 py-1.5 rounded-md text-sm font-medium transition-colors", abaAtiva === "Bancos" ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200")}>
          <Building2 className="size-4 inline mr-2" /> Bancos
        </button>
        <button onClick={() => setAbaAtiva("Categorias")} className={cn("px-4 py-1.5 rounded-md text-sm font-medium transition-colors", abaAtiva === "Categorias" ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200")}>
          <Tag className="size-4 inline mr-2" /> Categorias
        </button>
      </div>

      {abaAtiva === "Bancos" && (
        <div>
          <div className="flex justify-end mb-4">
            <Button onClick={() => { setFormBanco({ nome: "", agencia: "", conta: "", saldo_inicial: "" }); setModalBancoOpen(true); }} className="bg-sky-600 hover:bg-sky-500 h-9">
              <Plus className="size-4 mr-2" /> Novo Banco
            </Button>
          </div>
          <div className="glass rounded-2xl overflow-hidden border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50">
                <tr className="text-[11px] uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3 font-medium">Nome do Banco</th>
                  <th className="px-3 py-3 font-medium">Agência</th>
                  <th className="px-3 py-3 font-medium">Conta</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {bancos.map((b: any) => (
                  <tr key={b.id}>
                    <td className="px-5 py-3 text-slate-200">{b.nome}</td>
                    <td className="px-3 py-3 text-slate-400">{b.agencia || "—"}</td>
                    <td className="px-3 py-3 text-slate-400">{b.conta || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {abaAtiva === "Categorias" && (
        <div>
          <div className="flex justify-end mb-4">
            <Button onClick={() => { setFormCat({ nome: "", tipo: "Ambos" }); setModalCatOpen(true); }} className="bg-sky-600 hover:bg-sky-500 h-9">
              <Plus className="size-4 mr-2" /> Nova Categoria
            </Button>
          </div>
          <div className="glass rounded-2xl overflow-hidden border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50">
                <tr className="text-[11px] uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3 font-medium">Nome da Categoria</th>
                  <th className="px-3 py-3 font-medium">Tipo</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {categorias.map((c: any) => (
                  <tr key={c.id}>
                    <td className="px-5 py-3 text-slate-200">{c.nome}</td>
                    <td className="px-3 py-3 text-slate-400">{c.tipo}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal de Banco */}
      {modalBancoOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Novo Banco</h2>
            <div className="space-y-4">
              <div className="grid gap-1.5"><Label>Nome do Banco *</Label><Input value={formBanco.nome} onChange={(e) => setFormBanco(s => ({ ...s, nome: e.target.value }))} /></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5"><Label>Número da Agência</Label><Input value={formBanco.agencia} onChange={(e) => setFormBanco(s => ({ ...s, agencia: e.target.value }))} /></div>
                <div className="grid gap-1.5"><Label>Número da Conta</Label><Input value={formBanco.conta} onChange={(e) => setFormBanco(s => ({ ...s, conta: e.target.value }))} /></div>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalBancoOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvarBanco.mutate(formBanco)} disabled={!formBanco.nome} className="bg-emerald-600 hover:bg-emerald-500 text-white">Salvar</Button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Categoria */}
      {modalCatOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">Nova Categoria</h2>
            <div className="space-y-4">
              <div className="grid gap-1.5"><Label>Nome da Categoria *</Label><Input value={formCat.nome} onChange={(e) => setFormCat(s => ({ ...s, nome: e.target.value }))} /></div>
              <div className="grid gap-1.5">
                <Label>Tipo</Label>
                <select value={formCat.tipo} onChange={(e) => setFormCat(s => ({ ...s, tipo: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md px-3">
                  <option value="Ambos">Ambos (Pagar e Receber)</option>
                  <option value="Pagar">Apenas Pagar</option>
                  <option value="Receber">Apenas Receber</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalCatOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvarCat.mutate(formCat)} disabled={!formCat.nome} className="bg-emerald-600 hover:bg-emerald-500 text-white">Salvar</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
