import os
import re

path_fin = os.path.join(os.getcwd(), "frontend", "src", "pages", "Financeiro.tsx")

conteudo = r'''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, DollarSign, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, X, Check, Filter } from "lucide-react";
import { apiGet, apiPost, apiPut, apiPatch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { brl } from "@/lib/format";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const CATEGORIAS = ["Combustível", "Manutenção", "Pneus", "Pedágio", "Seguro", "Frete", "Multa", "Outros"];

export default function Financeiro() {
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<"Pagar" | "Receber" | "Todos">("Todos");
  const [busca, setBusca] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<any>(null);
  const [form, setForm] = useState<any>({
    tipo: "Pagar", descricao: "", categoria: "Outros", valor: "", vencimento: "", status: "Pendente", vinculo: "", observacoes: ""
  });

  const { data: contas = [], isLoading } = useQuery({ queryKey: ["contas", abaAtiva], queryFn: () => apiGet<any[]>(`/financeiro/contas${abaAtiva !== "Todos" ? `?tipo=${abaAtiva}` : ""}`) });
  const { data: resumo = { a_pagar: 0, a_receber: 0, vencido: 0, total_pago: 0, saldo: 0 } } = useQuery({ queryKey: ["resumo-financeiro"], queryFn: () => apiGet<any>("/financeiro/resumo") });

  const salvar = useMutation({
    mutationFn: (payload: any) => editando ? apiPut(`/financeiro/contas/${editando.id}`, payload) : apiPost("/financeiro/contas", payload),
    onSuccess: () => {
      toast.success(editando ? "Conta atualizada!" : "Conta registrada!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["contas"] });
      qc.invalidateQueries({ queryKey: ["resumo-financeiro"] });
    }
  });

  const marcarPago = useMutation({
    mutationFn: (id: string) => apiPatch(`/financeiro/contas/${id}/pagar`, {}),
    onSuccess: () => {
      toast.success("Conta quitada!");
      qc.invalidateQueries({ queryKey: ["contas"] });
      qc.invalidateQueries({ queryKey: ["resumo-financeiro"] });
    }
  });

  const abrirNovo = () => {
    setEditando(null);
    setForm({ tipo: "Pagar", descricao: "", categoria: "Outros", valor: "", vencimento: "", status: "Pendente", vinculo: "", observacoes: "" });
    setModalOpen(true);
  };

  const abrirEdicao = (c: any) => {
    setEditando(c);
    setForm({ ...c, valor: String(c.valor) });
    setModalOpen(true);
  };

  const filtrados = contas.filter((c: any) =>
    (c.descricao || "").toLowerCase().includes(busca.toLowerCase()) ||
    (c.vinculo || "").toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Financeiro"
        description="Controle suas contas a pagar, a receber e o fluxo de caixa."
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder="Buscar conta..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-9 h-9 w-64" />
            </div>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">
              <Plus className="size-4 mr-2" /> Nova Conta
            </Button>
          </div>
        }
      />

      {/* Cards de Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="glass p-4 rounded-xl border border-rose-500/30">
          <p className="text-[11px] uppercase tracking-widest text-rose-400">A Pagar</p>
          <p className="text-2xl font-bold text-rose-400 mt-1">{brl(resumo.a_pagar)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-emerald-500/30">
          <p className="text-[11px] uppercase tracking-widest text-emerald-400">A Receber</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">{brl(resumo.a_receber)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-amber-500/30">
          <p className="text-[11px] uppercase tracking-widest text-amber-400">Saldo Projetado</p>
          <p className={cn("text-2xl font-bold mt-1", resumo.saldo >= 0 ? "text-emerald-400" : "text-rose-400")}>{brl(resumo.saldo)}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Vencidas</p>
          <p className="text-2xl font-bold text-slate-300 mt-1">{brl(resumo.vencido)}</p>
        </div>
      </div>

      {/* Filtro de Abas */}
      <div className="flex gap-1 bg-slate-900/50 p-1 rounded-lg mb-4 w-fit border border-slate-800">
        {["Todos", "Pagar", "Receber"].map((tipo) => (
          <button
            key={tipo}
            onClick={() => setAbaAtiva(tipo as any)}
            className={cn(
              "px-4 py-1.5 rounded-md text-sm font-medium transition-colors",
              abaAtiva === tipo ? "bg-sky-600 text-white" : "text-slate-400 hover:text-slate-200"
            )}
          >
            {tipo === "Todos" ? "Todas" : `Contas a ${tipo}`}
          </button>
        ))}
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-500">
              <th className="px-5 py-3 font-medium">Vencimento</th>
              <th className="px-3 py-3 font-medium">Descrição</th>
              <th className="px-3 py-3 font-medium">Categoria</th>
              <th className="px-3 py-3 font-medium">Vínculo</th>
              <th className="px-3 py-3 font-medium">Valor</th>
              <th className="px-3 py-3 font-medium">Status</th>
              <th className="px-3 py-3 text-right font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {isLoading ? (
              <tr><td colSpan={7} className="p-8 text-center text-slate-500">Carregando...</td></tr>
            ) : filtrados.length === 0 ? (
              <tr><td colSpan={7} className="p-8 text-center text-slate-500">Nenhuma conta encontrada.</td></tr>
            ) : (
              filtrados.map((c: any) => (
                <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-3 font-mono text-slate-300">{c.vencimento ? c.vencimento.split("-").reverse().join("/") : "—"}</td>
                  <td className="px-3 py-3">
                    <p className="text-slate-200">{c.descricao}</p>
                    <p className="text-xs text-slate-500">{c.observacoes}</p>
                  </td>
                  <td className="px-3 py-3 text-slate-400">{c.categoria}</td>
                  <td className="px-3 py-3 text-slate-400 font-mono text-xs">{c.vinculo || "—"}</td>
                  <td className={cn("px-3 py-3 font-mono font-bold", c.tipo === "Pagar" ? "text-rose-400" : "text-emerald-400")}>
                    {c.tipo === "Pagar" ? "-" : "+"}{brl(c.valor)}
                  </td>
                  <td className="px-3 py-3">
                    <Badge tone={c.status === "Pago" ? "ativo" : c.status === "Atrasado" ? "inativo" : "warning"}>
                      {c.status}
                    </Badge>
                  </td>
                  <td className="px-3 py-3 text-right">
                    {c.status !== "Pago" && (
                      <Button size="sm" variant="ghost" className="text-emerald-400 hover:bg-emerald-500/10" onClick={() => marcarPago.mutate(c.id)}>
                        <CheckCircle2 className="size-4 mr-1" /> Quitar
                      </Button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">{editando ? "Editar Conta" : "Nova Conta"}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="grid gap-1.5 md:col-span-2">
                <Label className="text-xs text-slate-400">Tipo de Conta</Label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    <input type="radio" checked={form.tipo === "Pagar"} onChange={() => setForm((s: any) => ({ ...s, tipo: "Pagar" }))} /> Conta a Pagar
                  </label>
                  <label className="flex items-center gap-2 text-sm text-slate-300">
                    <input type="radio" checked={form.tipo === "Receber"} onChange={() => setForm((s: any) => ({ ...s, tipo: "Receber" }))} /> Conta a Receber
                  </label>
                </div>
              </div>
              <div className="grid gap-1.5 md:col-span-2">
                <Label className="text-xs text-slate-400">Descrição *</Label>
                <Input value={form.descricao} onChange={(e) => setForm((s: any) => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Frete Campinas x SP" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Categoria</Label>
                <select value={form.categoria} onChange={(e) => setForm((s: any) => ({ ...s, categoria: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  {CATEGORIAS.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Valor (R$) *</Label>
                <Input type="number" value={form.valor} onChange={(e) => setForm((s: any) => ({ ...s, valor: e.target.value }))} placeholder="0,00" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Vencimento *</Label>
                <Input type="date" value={form.vencimento} onChange={(e) => setForm((s: any) => ({ ...s, vencimento: e.target.value }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Vínculo (Placa, OS, Contrato)</Label>
                <Input value={form.vinculo} onChange={(e) => setForm((s: any) => ({ ...s, vinculo: e.target.value }))} placeholder="Ex: QPN5139 / OS-1042" />
              </div>
              <div className="grid gap-1.5 md:col-span-2">
                <Label className="text-xs text-slate-400">Observações</Label>
                <Input value={form.observacoes} onChange={(e) => setForm((s: any) => ({ ...s, observacoes: e.target.value }))} />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate(form)} disabled={salvar.isPending || !form.descricao || !form.valor || !form.vencimento} className="bg-emerald-600 hover:bg-emerald-500 text-white">
                <Check className="size-4 mr-2" /> Salvar Conta
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''

with open(path_fin, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Página Financeiro.tsx criada.")

# Garantir rota no App.tsx
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "Financeiro" not in app_c:
    # Já deve existir a rota, mas vamos garantir o import
    if 'import Financeiro from "@/pages/Financeiro";' not in app_c:
        app_c = app_c.replace(
            'import Multas from "@/pages/Multas";',
            'import Multas from "@/pages/Multas";\nimport Financeiro from "@/pages/Financeiro";'
        )
        with open(app_path, "w", encoding="utf-8") as f:
            f.write(app_c)
        print("✅ Import do Financeiro adicionado ao App.tsx.")
    else:
        print("ℹ️ Import do Financeiro já existia.")