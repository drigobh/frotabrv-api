import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Disc, Upload, Search } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { useVeiculos } from "@/hooks/useCadastros";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ChassiMapa } from "@/components/ChassiMapa";
import { brl } from "@/lib/format";

const STATUS_PNEU = ["Estoque", "Aplicado", "Recapagem", "Conserto", "Sucateado"];
const TIPOS_PNEU = ["Direcional", "Tração", "Misto"];

export default function Pneus() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [filtro, setFiltro] = useState("");
  const [tipoAtivo, setTipoAtivo] = useState<"cavalo" | "carreta">("cavalo");
  const [veiculoMapa, setVeiculoMapa] = useState<string>("");

  const { data: pneus = [] } = useQuery({ queryKey: ["pneus"], queryFn: () => apiGet<any[]>("/pneus") });
  const veiculos = useVeiculos();
  const { data: carretas = [] } = useQuery({ queryKey: ["carretas"], queryFn: () => apiGet<any[]>("/carretas") });

  const [form, setForm] = useState({
    numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: "", veiculo_id: "", carreta_id: "", posicao: "", sulco_atual: "", pressao_atual: ""
  });

  const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        ...form,
        custo_aquisicao: Number(String(form.custo_aquisicao).replace(",", ".")) || 0,
        sulco_atual: form.sulco_atual ? Number(form.sulco_atual) : null,
        pressao_atual: form.pressao_atual ? Number(form.pressao_atual) : null
      };
      return editingId ? apiPut(`/pneus/${editingId}`, payload) : apiPost("/pneus", payload);
    },
    onSuccess: () => {
      toast.success(editingId ? "Pneu atualizado!" : "Pneu cadastrado!");
      setOpen(false); setEditingId(null);
      qc.invalidateQueries({ queryKey: ["pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneus/${id}`),
    onSuccess: () => { toast.success("Pneu excluído."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["pneus"] }); }
  });

  const abrirNovo = () => {
    setEditingId(null);
    setForm({ numero_fogo: "", marca: "", modelo: "", medida: "", dot: "", tipo: "Tração", status: "Estoque", custo_aquisicao: "", observacoes: "", foto_url: "", veiculo_id: "", carreta_id: "", posicao: "", sulco_atual: "", pressao_atual: "" });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({ ...r, custo_aquisicao: String(r.custo_aquisicao || ""), sulco_atual: String(r.sulco_atual || ""), pressao_atual: String(r.pressao_atual || "") });
    setOpen(true);
  };

  const pneusFiltrados = pneus.filter((p: any) => {
    if (!filtro) return true;
    return p.numero_fogo.toLowerCase().includes(filtro.toLowerCase()) || p.marca.toLowerCase().includes(filtro.toLowerCase());
  });

  const statusColor = (status: string) => {
    if (status === "Estoque") return "bg-sky-500/20 text-sky-400";
    if (status === "Aplicado") return "bg-emerald-500/20 text-emerald-400";
    if (status === "Recapagem") return "bg-amber-500/20 text-amber-400";
    if (status === "Sucateado") return "bg-rose-500/20 text-rose-400";
    return "bg-slate-800 text-slate-400";
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Controle de Pneus"
        description="Gestão de pneus por número de fogo, marca, DOT e status."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Pneu</Button>}
      />

      <div className="mb-4 flex gap-2">
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
          <Input placeholder="Buscar por número de fogo ou marca..." value={filtro} onChange={(e) => setFiltro(e.target.value)} className="pl-9 h-9" />
        </div>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Nº Fogo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Marca / Modelo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Medida</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">DOT</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Custo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {pneusFiltrados.length === 0 ? (
              <TableRow><TableCell colSpan={8} className="text-center py-8 text-slate-500">Nenhum pneu cadastrado.</TableCell></TableRow>
            ) : (
              pneusFiltrados.map((p: any) => (
                <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="font-bold text-slate-100">{p.numero_fogo}</TableCell>
                  <TableCell className="text-slate-300">{p.marca} {p.modelo && `/ ${p.modelo}`}</TableCell>
                  <TableCell className="text-slate-400 font-mono">{p.medida}</TableCell>
                  <TableCell className="text-slate-400">{p.dot || "—"}</TableCell>
                  <TableCell className="text-slate-400">{p.tipo}</TableCell>
                  <TableCell><span className={`px-2 py-0.5 rounded text-[10px] font-bold ${statusColor(p.status)}`}>{p.status}</span></TableCell>
                  <TableCell className="text-amber-400 font-mono">{brl(p.custo_aquisicao)}</TableCell>
                  <TableCell className="text-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(p)}><Pencil className="size-4 text-sky-400" /></Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(p.id)}><Trash2 className="size-4 text-red-300" /></Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Pneu" : "Novo Pneu"}</h2>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Número de Fogo *</Label>
                <Input value={form.numero_fogo} onChange={(e) => setForm(s => ({ ...s, numero_fogo: e.target.value }))} placeholder="Ex: FOG-10492" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Marca *</Label>
                <Input value={form.marca} onChange={(e) => setForm(s => ({ ...s, marca: e.target.value }))} placeholder="Ex: Michelin" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Modelo</Label>
                <Input value={form.modelo} onChange={(e) => setForm(s => ({ ...s, modelo: e.target.value }))} placeholder="Ex: X Multi Z" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Medida *</Label>
                <Input value={form.medida} onChange={(e) => setForm(s => ({ ...s, medida: e.target.value }))} placeholder="Ex: 295/80 R22.5" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">DOT (Semana/Ano)</Label>
                <Input value={form.dot} onChange={(e) => setForm(s => ({ ...s, dot: e.target.value }))} placeholder="Ex: 4523" maxLength={4} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Tipo</Label>
                <FieldSelect value={form.tipo} onChange={(v) => setForm(s => ({ ...s, tipo: v }))} options={TIPOS_PNEU.map(t => ({ value: t, label: t }))} />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Status</Label>
                <FieldSelect value={form.status} onChange={(v) => setForm(s => ({ ...s, status: v }))} options={STATUS_PNEU.map(s => ({ value: s, label: s }))} />
              </div>
              <div className="grid gap-1.5">
                <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">Tipo de Ativo</Label>
                <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-700">
                  <button 
                    className={`flex-1 py-1.5 text-sm rounded-md font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => { setTipoAtivo('cavalo'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); }}
                  >
                    Cavalo Mecânico
                  </button>
                  <button 
                    className={`flex-1 py-1.5 text-sm rounded-md font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => { setTipoAtivo('carreta'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); }}
                  >
                    Carreta / Semi
                  </button>
                </div>
              </div>

              <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">{tipoAtivo === 'cavalo' ? 'Veículo' : 'Carreta'}</Label>
                {tipoAtivo === 'cavalo' ? (
                  <FieldSelect value={form.veiculo_id} onChange={(v) => setForm(s => ({ ...s, veiculo_id: v }))} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione..." />
                ) : (
                  <FieldSelect value={form.carreta_id} onChange={(v) => setForm(s => ({ ...s, carreta_id: v }))} options={carretas.map((c: any) => ({ value: c.id, label: `${c.codigo} - ${c.tipo}` }))} placeholder="Selecione..." />
                )}
              </div>

              <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">Posição no Eixo</Label>
                <Input value={form.posicao} onChange={(e) => setForm(s => ({ ...s, posicao: e.target.value }))} placeholder="Ex: 2-DE (Eixo 2, Direito Externo)" />
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Sulco Atual (mm)</Label>
                <Input type="number" step="0.1" value={form.sulco_atual} onChange={(e) => setForm(s => ({ ...s, sulco_atual: e.target.value }))} placeholder="Ex: 5.5" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Pressão Atual (psi)</Label>
                <Input type="number" value={form.pressao_atual} onChange={(e) => setForm(s => ({ ...s, pressao_atual: e.target.value }))} placeholder="Ex: 120" />
              </div>
            </div>
            
            <div className="col-span-2 grid gap-1.5">
              <Label className="text-xs text-slate-400">Custo de Aquisição (R$)</Label>
                <Input value={form.custo_aquisicao} onChange={(e) => setForm(s => ({ ...s, custo_aquisicao: e.target.value }))} placeholder="0,00" />
              </div>
              <div className="col-span-2 grid gap-1.5">
                <Label className="text-xs text-slate-400">Observações</Label>
                <Input value={form.observacoes} onChange={(e) => setForm(s => ({ ...s, observacoes: e.target.value }))} placeholder="Ex: Comprado na loja X" />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar"}</Button>
            </div>
          </div>
        </div>
      )}

      {excluirId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Pneu?</h2>
            <p className="text-sm text-slate-400 mb-6">Tem certeza que deseja remover este pneu?</p>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
              <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
            </div>
          </div>
        </div>
      )}
    
      {/* Mapa de Chassi */}
      <div className="mt-8">
        <div className="flex items-center gap-4 mb-4">
          <h3 className="text-lg font-bold text-slate-100">Chassi do Veículo</h3>
          <select 
            value={veiculoMapa} 
            onChange={(e) => setVeiculoMapa(e.target.value)}
            className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3 ml-auto"
          >
            <option value="">Selecione o Veículo para o Mapa</option>
            <optgroup label="Cavalos Mecânicos">
              {(veiculos.data ?? []).map((v: any) => (
                <option key={v.id} value={v.id}>{v.placa} - {v.modelo}</option>
              ))}
            </optgroup>
            <optgroup label="Carretas">
              {carretas.map((c: any) => (
                <option key={c.id} value={c.id}>{c.codigo} - {c.tipo}</option>
              ))}
            </optgroup>
          </select>
        </div>
        <div className="grid grid-cols-1 gap-4">
          {veiculoMapa ? (
            <>
              <ChassiMapa 
                pneus={pneus} 
                veiculoId={veiculoMapa} 
                configuracao="6x2" 
                tipo="cavalo" 
              />
              <ChassiMapa 
                pneus={pneus} 
                veiculoId={veiculoMapa} 
                configuracao="3 eixos" 
                tipo="carreta" 
              />
            </>
          ) : (
            <div className="glass p-6 rounded-2xl text-center text-slate-500">
              <p className="text-sm">Selecione um veículo acima para visualizar o chassi.</p>
            </div>
          )}
        </div>
      </div>
</div>
  );
}
