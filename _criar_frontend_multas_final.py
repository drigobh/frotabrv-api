import os
import re

path_multas = os.path.join(os.getcwd(), "frontend", "src", "pages", "Multas.tsx")

conteudo = r'''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Search, AlertTriangle, X, Check, DollarSign, Gauge } from "lucide-react";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { brl } from "@/lib/format";
import { toast } from "sonner";

export default function Multas() {
  const qc = useQueryClient();
  const [busca, setBusca] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<any>(null);
  const [form, setForm] = useState<any>({
    veiculo_id: "", motorista_id: "", data_infracao: "", hora_infracao: "", local: "",
    descricao: "", valor: "", pontos: "", orgao_autuador: "", numero_ait: "", status: "Pendente"
  });

  const { data: multas = [] } = useQuery({ queryKey: ["multas"], queryFn: () => apiGet<any[]>("/multas") });
  const { data: veiculos = [] } = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<any[]>("/veiculos") });
  const { data: motoristas = [] } = useQuery({ queryKey: ["motoristas"], queryFn: () => apiGet<any[]>("/motoristas") });

  const salvar = useMutation({
    mutationFn: (payload: any) => editando ? apiPut(`/multas/${editando.id}`, payload) : apiPost("/multas", payload),
    onSuccess: () => {
      toast.success(editando ? "Multa atualizada!" : "Multa registrada!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["multas"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar.")
  });

  const abrirNovo = () => {
    setEditando(null);
    setForm({
      veiculo_id: "", motorista_id: "", data_infracao: "", hora_infracao: "", local: "",
      descricao: "", valor: "", pontos: "", orgao_autuador: "", numero_ait: "", status: "Pendente"
    });
    setModalOpen(true);
  };

  const abrirEdicao = (m: any) => {
    setEditando(m);
    setForm({ ...m, valor: String(m.valor), pontos: String(m.pontos) });
    setModalOpen(true);
  };

  const filtrados = multas.filter((m: any) =>
    (m.descricao || "").toLowerCase().includes(busca.toLowerCase()) ||
    (m.numero_ait || "").toLowerCase().includes(busca.toLowerCase())
  );

  const totalPendente = multas.filter((m: any) => m.status === "Pendente").reduce((acc, m) => acc + (m.valor || 0), 0);
  const totalPontos = multas.filter((m: any) => m.status === "Pendente").reduce((acc, m) => acc + (m.pontos || 0), 0);

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Multas e Infrações"
        description="Controle as multas vinculadas a veículos e motoristas."
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder="Buscar multa..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-9 h-9 w-64" />
            </div>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">
              <Plus className="size-4 mr-2" /> Nova Multa
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-400">Total de Multas</p>
            <p className="text-2xl font-bold text-slate-100 mt-1">{multas.length}</p>
          </div>
          <div className="p-2 bg-sky-500/10 rounded-lg"><AlertTriangle className="size-5 text-sky-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-400">Valor Pendente</p>
            <p className="text-2xl font-bold text-rose-400 mt-1">{brl(totalPendente)}</p>
          </div>
          <div className="p-2 bg-rose-500/10 rounded-lg"><DollarSign className="size-5 text-rose-400" /></div>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-widest text-slate-400">Pontos na CNH</p>
            <p className="text-2xl font-bold text-amber-400 mt-1">{totalPontos}</p>
          </div>
          <div className="p-2 bg-amber-500/10 rounded-lg"><Gauge className="size-5 text-amber-400" /></div>
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-500">
              <th className="px-5 py-3 font-medium">Data</th>
              <th className="px-3 py-3 font-medium">Veículo / Motorista</th>
              <th className="px-3 py-3 font-medium">Descrição</th>
              <th className="px-3 py-3 font-medium">AIT</th>
              <th className="px-3 py-3 font-medium">Valor</th>
              <th className="px-3 py-3 font-medium">Pontos</th>
              <th className="px-3 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filtrados.length === 0 ? (
              <tr><td colSpan={7} className="p-8 text-center text-slate-500">Nenhuma multa registrada.</td></tr>
            ) : (
              filtrados.map((m: any) => (
                <tr key={m.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-5 py-3 font-mono text-slate-300">{m.data_infracao ? m.data_infracao.split("-").reverse().join("/") : "—"}</td>
                  <td className="px-3 py-3">
                    <p className="font-mono text-sky-300">{veiculos.find((v: any) => v.id === m.veiculo_id)?.placa || "—"}</p>
                    <p className="text-xs text-slate-400">{motoristas.find((d: any) => d.id === m.motorista_id)?.nome || "—"}</p>
                  </td>
                  <td className="px-3 py-3 text-slate-300">{m.descricao}</td>
                  <td className="px-3 py-3 font-mono text-slate-400">{m.numero_ait || "—"}</td>
                  <td className="px-3 py-3 font-mono text-rose-400">{brl(m.valor)}</td>
                  <td className="px-3 py-3 font-mono text-amber-400">{m.pontos}</td>
                  <td className="px-3 py-3">
                    <Badge tone={m.status === "Pago" ? "ativo" : m.status === "Recurso" ? "warning" : "inativo"}>
                      {m.status}
                    </Badge>
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
              <h2 className="text-lg font-bold text-slate-100">{editando ? "Editar Multa" : "Nova Multa"}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Veículo *</Label>
                <select value={form.veiculo_id} onChange={(e) => setForm((s: any) => ({ ...s, veiculo_id: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  <option value="">Selecione...</option>
                  {veiculos.map((v: any) => <option key={v.id} value={v.id}>{v.placa}</option>)}
                </select>
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Motorista *</Label>
                <select value={form.motorista_id} onChange={(e) => setForm((s: any) => ({ ...s, motorista_id: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  <option value="">Selecione...</option>
                  {motoristas.map((m: any) => <option key={m.id} value={m.id}>{m.nome}</option>)}
                </select>
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Data da Infração *</Label>
                <Input type="date" value={form.data_infracao} onChange={(e) => setForm((s: any) => ({ ...s, data_infracao: e.target.value }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Hora da Infração</Label>
                <Input type="time" value={form.hora_infracao} onChange={(e) => setForm((s: any) => ({ ...s, hora_infracao: e.target.value }))} />
              </div>
              <div className="grid gap-1.5 col-span-2">
                <Label className="text-xs text-slate-400">Local</Label>
                <Input value={form.local} onChange={(e) => setForm((s: any) => ({ ...s, local: e.target.value }))} placeholder="Ex: BR-050 KM 120" />
              </div>
              <div className="grid gap-1.5 col-span-2">
                <Label className="text-xs text-slate-400">Descrição da Infração</Label>
                <Input value={form.descricao} onChange={(e) => setForm((s: any) => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Excesso de velocidade" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Valor (R$)</Label>
                <Input type="number" value={form.valor} onChange={(e) => setForm((s: any) => ({ ...s, valor: e.target.value }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Pontos na CNH</Label>
                <Input type="number" value={form.pontos} onChange={(e) => setForm((s: any) => ({ ...s, pontos: e.target.value }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Órgão Autuador</Label>
                <Input value={form.orgao_autuador} onChange={(e) => setForm((s: any) => ({ ...s, orgao_autuador: e.target.value }))} placeholder="Ex: PRF, DER" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Número do AIT</Label>
                <Input value={form.numero_ait} onChange={(e) => setForm((s: any) => ({ ...s, numero_ait: e.target.value }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Status</Label>
                <select value={form.status} onChange={(e) => setForm((s: any) => ({ ...s, status: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  <option value="Pendente">Pendente</option>
                  <option value="Pago">Pago</option>
                  <option value="Recurso">Recurso</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate(form)} disabled={salvar.isPending || !form.veiculo_id || !form.motorista_id || !form.data_infracao} className="bg-emerald-600 hover:bg-emerald-500 text-white">
                <Check className="size-4 mr-2" /> Salvar Multa
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''

with open(path_multas, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Página Multas.tsx criada.")

# Adicionar rota no App.tsx
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "Multas" not in app_c:
    app_c = app_c.replace(
        'import RelatoriosPneus from "@/pages/RelatoriosPneus";',
        'import RelatoriosPneus from "@/pages/RelatoriosPneus";\nimport Multas from "@/pages/Multas";'
    )
    app_c = app_c.replace(
        '<Route path="/financeiro"',
        '<Route path="/multas" element={<Multas />} />\n              <Route path="/financeiro"'
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_c)
    print("✅ Rota /multas adicionada ao App.tsx.")

# Adicionar no Menu (Sidebar)
sidebar_path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    s_c = f.read()

if "/multas" not in s_c:
    ancora = '{ label: "Central de Alertas", icon: BellRing, path: "/alertas" },'
    novo_link = ancora + '\n      { label: "Multas e Infrações", icon: AlertTriangle, path: "/multas" },'
    s_c = s_c.replace(ancora, novo_link)
    if "AlertTriangle" not in s_c.split("from \"lucide-react\"")[0]:
        s_c = re.sub(r'import\s+\{([^}]+)\}\s+from\s+"lucide-react";', r'import {\1, AlertTriangle } from "lucide-react";', s_c, count=1)
    
    with open(sidebar_path, "w", encoding="utf-8") as f:
        f.write(s_c)
    print("✅ Link 'Multas e Infrações' adicionado ao menu Gestão.")

print("✅ Tudo pronto! Faça o git push.")