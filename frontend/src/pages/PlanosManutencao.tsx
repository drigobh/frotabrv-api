import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Wrench, Plus, Pencil, Trash2, Info, User, Gauge, Calendar, HelpCircle, X } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { useVeiculos } from "@/hooks/useCadastros";
import { useMe } from "@/hooks/useSession";

const FAMILIAS = [
  { nome: "Lubrificação e Filtros", itens: "Óleo do motor, filtro de óleo, filtro de combustível/separador sedimentador, filtro de ar do motor." },
  { nome: "Linha Pesada e Transmissão", itens: "Óleo da caixa de câmbio (I-Shift), óleo de diferencial, kit de embreagem, cruzetas e cardan." },
  { nome: "Segurança e Rodagem", itens: "Lonas e pastilhas, tambores/discos, cuícas de freio, alinhamento, balanceamento e rodízio de pneus." },
  { nome: "Sistemas de Emissões", itens: "Filtro dessecador (APU/secador de ar), filtro do sistema de Arla 32 e sensor de NOx." },
  { nome: "Chassi e Suspensão", itens: "Bolsas de ar, amortecedores, molas, engraxamento de quinta roda e buchas de tirante." },
  { nome: "Outros", itens: "Outros serviços não listados nas categorias padrão." }
];

const TIPOS_GATILHO = [
  { value: "km", label: "Por Quilometragem (KM)" },
  { value: "horas", label: "Por Horímetro (Horas)" },
  { value: "dias", label: "Por Tempo (Dias/Meses/Anos)" }
];

const UNIDADES_TEMPO = [
  { value: "dias", label: "Dias" },
  { value: "meses", label: "Meses" },
  { value: "anos", label: "Anos" }
];

export default function PlanosManutencao() {
  const qc = useQueryClient();
  const { data: me } = useMe();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  
  const veiculos = useVeiculos();
  const { data: carretas = [] } = useQuery({ queryKey: ["carretas"], queryFn: () => apiGet<any[]>("/carretas") });
  const { data: planos = [] } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });

  const [tipoAtivo, setTipoAtivo] = useState<"cavalo" | "carreta">("cavalo");
  const [hodometroAtual, setHodometroAtual] = useState<number | null>(null);
  
  const [form, setForm] = useState({
    veiculo_id: "", carreta_id: "", familia: FAMILIAS[0].nome, descricao: "", 
    tipo_gatilho: "km", tipo_recorrencia: "periodico", unidade_tempo: "dias",
    intervalo: "", ultima_execucao_km: "", data_abertura: new Date().toISOString().split('T')[0]
  });

  const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        ...form,
        veiculo_id: tipoAtivo === "cavalo" ? form.veiculo_id : null,
        carreta_id: tipoAtivo === "carreta" ? form.carreta_id : null,
        intervalo: Number(form.intervalo),
        ultima_execucao_km: form.ultima_execucao_km ? Number(form.ultima_execucao_km) : null
      };
      return editingId ? apiPut(`/planos-manutencao/${editingId}`, payload) : apiPost("/planos-manutencao", payload);
    },
    onSuccess: () => { toast.success("Plano salvo!"); setOpen(false); qc.invalidateQueries({ queryKey: ["planos-manutencao"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/planos-manutencao/${id}`),
    onSuccess: () => { toast.success("Plano excluído."); setExcluirId(null); qc.invalidateQueries({ queryKey: ["planos-manutencao"] }); }
  });

  const buscarHodometro = (id: string, tipo: "cavalo" | "carreta") => {
    if (!id) { setHodometroAtual(null); return; }
    if (tipo === "cavalo") {
      const v = veiculos.data?.find((x: any) => x.id === id);
      setHodometroAtual(v?.hodometro_km || 0);
    } else {
      const c = carretas.find((x: any) => x.id === id);
      setHodometroAtual(c?.hodometro_km || 0);
    }
  };

  const abrirNovo = () => {
    setEditingId(null);
    setTipoAtivo("cavalo");
    setHodometroAtual(null);
    setForm({ 
      veiculo_id: "", carreta_id: "", familia: FAMILIAS[0].nome, descricao: "", 
      tipo_gatilho: "km", tipo_recorrencia: "periodico", unidade_tempo: "dias",
      intervalo: "", ultima_execucao_km: "", data_abertura: new Date().toISOString().split('T')[0] 
    });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setTipoAtivo(r.carreta_id ? "carreta" : "cavalo");
    setHodometroAtual(null);
    setForm({ ...r, intervalo: String(r.intervalo), ultima_execucao_km: String(r.ultima_execucao_km || "") });
    setOpen(true);
  };

  const familiaSelecionada = FAMILIAS.find(f => f.nome === form.familia);

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Cadastro de Planos Preventivos"
        description="Defina os gatilhos e intervalos por família de componentes."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Plano</Button>}
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Ativo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Família</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Descrição</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Gatilho</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Recorrência</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {planos.map((p: any) => (
              <TableRow key={p.id} className="border-slate-800 hover:bg-slate-800/30">
                <TableCell className="text-slate-200 font-medium">{p.veiculo_label}</TableCell>
                <TableCell className="text-slate-400">{p.familia}</TableCell>
                <TableCell className="text-slate-400">{p.descricao}</TableCell>
                <TableCell className="text-xs text-slate-400">
                  A cada {p.intervalo} {p.tipo_gatilho === 'km' ? 'km' : p.tipo_gatilho === 'horas' ? 'horas' : p.unidade_tempo}
                </TableCell>
                <TableCell className="text-xs text-slate-400">
                  {p.tipo_recorrencia === 'vitalicio' ? 'Vitalício' : 'Periódico'}
                </TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(p)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(p.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* MODAL EXPANDIDO */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-5xl flex flex-col max-h-[90vh]">
            
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900 rounded-t-2xl">
              <h2 className="text-lg font-bold text-slate-100">{editingId ? "Editar Plano" : "Novo Plano"}</h2>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white"><X className="size-5" /></button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex flex-col lg:flex-row gap-8">
                
                {/* COLUNA ESQUERDA */}
                <div className="w-full lg:w-[300px] shrink-0 flex flex-col gap-4 border-r border-slate-800 pr-6">
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase mb-2"><Gauge className="size-4" /> Hodômetro Atual</div>
                    <p className="text-3xl font-bold text-sky-400 font-mono">{hodometroAtual !== null ? `${hodometroAtual.toLocaleString('pt-BR')} km` : "—"}</p>
                  </div>

                  <div className="bg-sky-950/30 border border-sky-900/50 rounded-xl p-4">
                    <div className="flex items-start gap-2">
                      <Info className="size-4 text-sky-400 mt-0.5 shrink-0" />
                      <div>
                        <strong className="text-sky-300 text-xs uppercase block mb-1">Itens cobertos:</strong>
                        <p className="text-xs text-sky-200/80 leading-relaxed">{familiaSelecionada?.itens}</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-3 flex items-center gap-2 mt-auto">
                    <User className="size-4 text-slate-500" />
                    <span className="text-xs text-slate-400">Registrado por: <strong className="text-slate-300">{me?.nome || "Usuário"}</strong></span>
                  </div>
                </div>

                {/* COLUNA DIREITA */}
                <div className="flex-1 flex flex-col gap-4">
                  <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-700">
                    <button className={`flex-1 py-2 text-sm rounded-md font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('cavalo'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); setHodometroAtual(null); }}>Cavalo Mecânico</button>
                    <button className={`flex-1 py-2 text-sm rounded-md font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('carreta'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); setHodometroAtual(null); }}>Carreta / Semi</button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">{tipoAtivo === 'cavalo' ? 'Cavalo Mecânico' : 'Carreta'}</Label>
                      {tipoAtivo === 'cavalo' ? (
                        <FieldSelect value={form.veiculo_id} onChange={(v) => { setForm(s => ({ ...s, veiculo_id: v })); buscarHodometro(v, 'cavalo'); }} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione..." />
                      ) : (
                        <FieldSelect value={form.carreta_id} onChange={(v) => { setForm(s => ({ ...s, carreta_id: v })); buscarHodometro(v, 'carreta'); }} options={carretas.map((c: any) => ({ value: c.id, label: `${c.codigo} - ${c.tipo}` }))} placeholder="Selecione..." />
                      )}
                    </div>
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Família de Componentes</Label>
                      <select value={form.familia} onChange={(e) => setForm(s => ({ ...s, familia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                        {FAMILIAS.map(f => <option key={f.nome} value={f.nome}>{f.nome}</option>)}
                      </select>
                    </div>
                  </div>

                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Descrição do Serviço</Label>
                    <Input value={form.descricao} onChange={(e) => setForm(s => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Revisão Periódica de 40.000 km" className="h-9" />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1">Tipo de Gatilho <HelpCircle className="size-3 text-slate-500" /></Label>
                      <select value={form.tipo_gatilho} onChange={(e) => setForm(s => ({ ...s, tipo_gatilho: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                        {TIPOS_GATILHO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                      </select>
                    </div>
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1">Recorrência <HelpCircle className="size-3 text-slate-500" /></Label>
                      <select value={form.tipo_recorrencia} onChange={(e) => setForm(s => ({ ...s, tipo_recorrencia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                        <option value="periodico">Periódico (Repete)</option>
                        <option value="vitalicio">Vitalício (Única vez)</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1">Intervalo <HelpCircle className="size-3 text-slate-500" /></Label>
                      <Input type="number" value={form.intervalo} onChange={(e) => setForm(s => ({ ...s, intervalo: e.target.value }))} placeholder={form.tipo_gatilho === 'km' ? "Ex: 20000" : "Ex: 180"} className="h-9" />
                    </div>
                    {form.tipo_gatilho === 'dias' && (
                      <div className="grid gap-1.5">
                        <Label className="text-xs text-slate-400 flex items-center gap-1">Unidade de Tempo <HelpCircle className="size-3 text-slate-500" /></Label>
                        <select value={form.unidade_tempo} onChange={(e) => setForm(s => ({ ...s, unidade_tempo: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                          {UNIDADES_TEMPO.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
                        </select>
                      </div>
                    )}
                  </div>

                  {form.tipo_gatilho === 'km' && (
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Última Execução (KM)</Label>
                      <Input type="number" value={form.ultima_execucao_km} onChange={(e) => setForm(s => ({ ...s, ultima_execucao_km: e.target.value }))} className="h-9" />
                    </div>
                  )}

                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400 flex items-center gap-1"><Calendar className="size-3" /> Data de Abertura do Plano</Label>
                    <Input value={form.data_abertura ? form.data_abertura.split("-").reverse().join("/") : ""} disabled className="bg-slate-800/50 text-slate-400 cursor-not-allowed border-slate-700 h-9" />
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900 rounded-b-2xl">
              <Button variant="outline" onClick={() => setOpen(false)} className="h-9">Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="h-9 bg-sky-600 hover:bg-sky-500">{salvar.isPending ? "Salvando..." : "Salvar Plano"}</Button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE EXCLUSÃO */}
      {excluirId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-sm p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-2">Excluir Plano?</h2>
            <p className="text-sm text-slate-400 mb-6">Tem certeza que deseja remover este plano preventivo?</p>
            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
              <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
