import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, ShieldCheck, ShoppingCart, Save, X, Edit, Trash2, History, Users, TrendingUp } from "lucide-react";
import { apiGet, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { brl } from "@/lib/format";
import { toast } from "sonner";

export default function GestaoCompras() {
  const qc = useQueryClient();
  const [busca, setBusca] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [usuarioEdicao, setUsuarioEdicao] = useState<any>(null);

  const [podeComprar, setPodeComprar] = useState(false);
  const [limiteCompra, setLimiteCompra] = useState(0);
  const [podeAprovar, setPodeAprovar] = useState(false);
  const [modalHistoricoOpen, setModalHistoricoOpen] = useState(false);
  const [historico, setHistorico] = useState<any[]>([]);
  const [limiteAprovacao, setLimiteAprovacao] = useState(0);

  const { data: usuarios = [] } = useQuery({
    queryKey: ["usuarios-compras"],
    queryFn: () => apiGet<any[]>("/compras/usuarios")
  });

  const salvar = useMutation({
    mutationFn: (payload: any) => apiPut(`/compras/usuarios/${usuarioEdicao.id}`, payload),
    onSuccess: () => {
      toast.success("Permissões atualizadas!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["usuarios-compras"] });
    }
  });

  const abrirEdicao = (u: any) => {
    setUsuarioEdicao(u);
    setPodeComprar(u.pode_comprar || false);
    setLimiteCompra(u.limite_compra || 0);
    setPodeAprovar(u.pode_aprovar_compras || false);
    setLimiteAprovacao(u.limite_aprovacao || 0);
    setModalOpen(true);
  };

  const handleSalvar = () => {
    salvar.mutate({
      pode_comprar: podeComprar,
      limite_compra: limiteCompra,
      pode_aprovar_compras: podeAprovar,
      limite_aprovacao: limiteAprovacao
    });
  };

  const filtrados = usuarios.filter((u: any) => 
    (u.nome || "").toLowerCase().includes(busca.toLowerCase()) || 
    (u.email || "").toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Administração"
        title="Cadastro de Compras"
        description="Gerencie quem pode comprar e quem pode aprovar, com seus respectivos limites."
        actions={
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
            <Input placeholder="Buscar usuário..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-9 h-9 w-64" />
          </div>
        }
      />

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-400">
              <th className="px-5 py-3 font-medium">Usuário</th>
              <th className="px-3 py-3 font-medium">Comprador</th>
              <th className="px-3 py-3 font-medium">Limite Compra</th>
              <th className="px-3 py-3 font-medium">Aprovador</th>
              <th className="px-3 py-3 font-medium">Limite Aprovação</th>
              <th className="px-3 py-3 text-right font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filtrados.map((u: any) => (
              <tr key={u.id} className="hover:bg-slate-800/30">
                <td className="px-5 py-3">
                  <p className="text-slate-200 font-medium">{u.nome}</p>
                  <p className="text-xs text-slate-400">{u.email}</p>
                </td>
                <td className="px-3 py-3">
                  {u.pode_comprar ? <span className="text-emerald-400 font-medium flex items-center gap-1"><ShoppingCart className="size-3"/> Sim</span> : <span className="text-slate-600">Não</span>}
                </td>
                <td className="px-3 py-3 text-slate-300 font-mono">{u.pode_comprar ? brl(u.limite_compra) : "—"}</td>
                <td className="px-3 py-3">
                  {u.pode_aprovar_compras ? <span className="text-sky-400 font-medium flex items-center gap-1"><ShieldCheck className="size-3"/> Sim</span> : <span className="text-slate-600">Não</span>}
                </td>
                <td className="px-3 py-3 text-slate-300 font-mono">{u.pode_aprovar_compras ? brl(u.limite_aprovacao) : "—"}</td>
                <td className="px-3 py-3 flex gap-1 justify-end">
                  <Button size="sm" variant="ghost" className="text-sky-400 hover:bg-sky-500/10 h-8 px-2" onClick={() => abrirEdicao(u)} title="Editar">
                    <Edit className="size-4" />
                  </Button>
                  <Button size="sm" variant="ghost" className="text-purple-400 hover:bg-purple-500/10 h-8 px-2" onClick={() => { apiGet<any[]>(`/compras/historico/${u.id}`).then(setHistorico); setModalHistoricoOpen(true); }} title="Histórico">
                    <History className="size-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modalOpen && usuarioEdicao && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Gerenciar: {usuarioEdicao.nome}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>
            
            <div className="space-y-6">
              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div className="flex items-center gap-2 mb-3">
                  <input type="checkbox" checked={podeComprar} onChange={(e) => setPodeComprar(e.target.checked)} className="rounded border-slate-700 bg-slate-900 size-4" />
                  <Label className="text-sm font-bold text-slate-200 m-0">Habilitar como Comprador</Label>
                </div>
                {podeComprar && (
                  <div>
                    <Label className="text-xs text-slate-400">Limite de Compra (R$)</Label>
                    <Input type="number" value={limiteCompra} onChange={(e) => setLimiteCompra(parseFloat(e.target.value) || 0)} className="bg-slate-950 mt-1" />
                  </div>
                )}
              </div>

              <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                <div className="flex items-center gap-2 mb-3">
                  <input type="checkbox" checked={podeAprovar} onChange={(e) => setPodeAprovar(e.target.checked)} className="rounded border-slate-700 bg-slate-900 size-4" />
                  <Label className="text-sm font-bold text-slate-200 m-0">Habilitar como Aprovador</Label>
                </div>
                {podeAprovar && (
                  <div>
                    <Label className="text-xs text-slate-400">Limite de Aprovação (R$)</Label>
                    <Input type="number" value={limiteAprovacao} onChange={(e) => setLimiteAprovacao(parseFloat(e.target.value) || 0)} className="bg-slate-950 mt-1" />
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleSalvar} disabled={salvar.isPending} className="bg-emerald-600 hover:bg-emerald-500"><Save className="size-4 mr-2"/> Salvar</Button>
            </div>
          </div>
        </div>
      )}

      {modalHistoricoOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">Histórico de Alterações</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalHistoricoOpen(false)}><X className="size-5" /></Button>
            </div>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {historico.length === 0 ? (
                <p className="text-center text-slate-500 text-sm">Nenhuma alteração registrada.</p>
              ) : (
                historico.map((h: any, i: number) => (
                  <div key={i} className="bg-slate-800/50 p-3 rounded-lg border border-slate-700 text-sm">
                    <p className="font-bold text-sky-400">{h.alterado_por}</p>
                    <p className="text-xs text-slate-400">{new Date(h.data).toLocaleString("pt-BR")}</p>
                    <ul className="mt-2 text-xs text-slate-300 list-disc list-inside">
                      {h.mudancas.map((m: string, j: number) => <li key={j}>{m}</li>)}
                    </ul>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
