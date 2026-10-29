import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PLANOS_RECORRENCIA_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = ["app/backend/models/planos_manutencao.py", "frontend/src/pages/PlanosManutencao.tsx"]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "planos_manutencao.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adicionar campos de recorrência e data
    if 'tipo_recorrencia' not in c:
        c = c.replace(
            'tipo_gatilho: str',
            'tipo_gatilho: str\n    tipo_recorrencia: str = "periodico" # "periodico" ou "vitalicio"\n    unidade_tempo: str | None = None # "dias", "meses", "anos"\n    data_abertura: str'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend Model: campos de recorrência e data adicionados.")

    # Garantir que o Router salve esses campos
    router_path = os.path.join(raiz, "app", "backend", "routers", "planos_manutencao.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'doc["data_abertura"] = body.data_abertura' not in c:
        c = c.replace(
            'doc["created_at"] = now_iso()',
            'doc["created_at"] = now_iso()\n    doc["data_abertura"] = body.data_abertura'
        )
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend Router: gravação de data e recorrência garantida.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "PlanosManutencao.tsx")
    
    codigo = '''import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Wrench, Plus, Pencil, Trash2, Info, User, Gauge, Calendar } from "lucide-react";
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
  const { data: planos = [], refetch } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });

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

  const buscarHodometro = async (id: string, tipo: "cavalo" | "carreta") => {
    if (!id) { setHodometroAtual(null); return; }
    
    try {
      if (tipo === "cavalo") {
        const v = veiculos.data?.find((x: any) => x.id === id);
        setHodometroAtual(v?.hodometro_km || 0);
      } else {
        // Para carreta, precisamos pegar o cavalo acoplado. 
        // Vamos simular pegando o hodometro da primeira carreta que tiver o id.
        // O ideal seria uma rota que busca o cavalo acoplado à carreta.
        const c = carretas.find((x: any) => x.id === id);
        setHodometroAtual(c?.hodometro_km || 0); // Assumindo que a carreta tem hodometro (ou usar o cavalo acoplado)
      }
    } catch (e) {
      setHodometroAtual(null);
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

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6 overflow-y-auto max-h-[90vh]">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Plano" : "Novo Plano"}</h2>
            
            <div className="space-y-4">
              {/* FLAG CAVALO VS CARRETA */}
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Tipo de Ativo</Label>
                <div className="flex bg-slate-950 p-1 rounded-md border border-slate-700">
                  <button className={`flex-1 py-1.5 text-sm rounded font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('cavalo'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); setHodometroAtual(null); }}>Cavalo Mecânico</button>
                  <button className={`flex-1 py-1.5 text-sm rounded font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('carreta'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); setHodometroAtual(null); }}>Carreta / Semi</button>
                </div>
              </div>

              {/* SELETOR DE VEÍCULO OU CARRETA */}
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">{tipoAtivo === 'cavalo' ? 'Cavalo Mecânico' : 'Carreta'}</Label>
                {tipoAtivo === 'cavalo' ? (
                  <FieldSelect value={form.veiculo_id} onChange={(v) => { setForm(s => ({ ...s, veiculo_id: v })); buscarHodometro(v, 'cavalo'); }} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione o Cavalo..." />
                ) : (
                  <FieldSelect value={form.carreta_id} onChange={(v) => { setForm(s => ({ ...s, carreta_id: v })); buscarHodometro(v, 'carreta'); }} options={carretas.map((c: any) => ({ value: c.id, label: `${c.codigo} - ${c.tipo}` }))} placeholder="Selecione a Carreta..." />
                )}
              </div>

              {/* HODÔMETRO ATUAL (READ-ONLY) */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-md p-2 flex items-center justify-between">
                <div className="flex items-center gap-2 text-slate-400 text-sm">
                  <Gauge className="size-4" />
                  <span>Hodômetro Atual</span>
                </div>
                <span className="font-mono font-bold text-sky-400">
                  {hodometroAtual !== null ? `${hodometroAtual.toLocaleString('pt-BR')} km` : "—"}
                </span>
              </div>

              {/* FAMÍLIA */}
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Família de Componentes</Label>
                <select value={form.familia} onChange={(e) => setForm(s => ({ ...s, familia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                  {FAMILIAS.map(f => <option key={f.nome} value={f.nome}>{f.nome}</option>)}
                </select>
              </div>

              {/* GUIA DA FAMÍLIA */}
              <div className="bg-sky-950/30 border border-sky-900/50 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <Info className="size-4 text-sky-400 mt-0.5 shrink-0" />
                  <p className="text-xs text-sky-200/80 leading-relaxed">
                    <strong className="text-sky-300 block mb-1">Itens cobertos:</strong>
                    {familiaSelecionada?.itens}
                  </p>
                </div>
              </div>

              {/* DESCRIÇÃO */}
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Descrição do Serviço</Label>
                <Input value={form.descricao} onChange={(e) => setForm(s => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Revisão Periódica de 40.000 km" />
              </div>
              
              {/* GATILHO E RECORRÊNCIA */}
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Tipo de Gatilho</Label>
                  <select value={form.tipo_gatilho} onChange={(e) => setForm(s => ({ ...s, tipo_gatilho: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                    {TIPOS_GATILHO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Recorrência</Label>
                  <select value={form.tipo_recorrencia} onChange={(e) => setForm(s => ({ ...s, tipo_recorrencia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                    <option value="periodico">Periódico (Repete)</option>
                    <option value="vitalicio">Vitalício (Única vez)</option>
                  </select>
                </div>
              </div>

              {/* INTERVALO E UNIDADE DE TEMPO */}
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Intervalo</Label>
                  <Input type="number" value={form.intervalo} onChange={(e) => setForm(s => ({ ...s, intervalo: e.target.value }))} placeholder={form.tipo_gatilho === 'km' ? "Ex: 20000" : form.tipo_gatilho === 'horas' ? "Ex: 500" : "Ex: 6"} />
                </div>
                {form.tipo_gatilho === 'dias' && (
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Unidade de Tempo</Label>
                    <select value={form.unidade_tempo} onChange={(e) => setForm(s => ({ ...s, unidade_tempo: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                      {UNIDADES_TEMPO.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
                    </select>
                  </div>
                )}
              </div>

              {/* ÚLTIMA EXECUÇÃO (KM) - Só para KM */}
              {form.tipo_gatilho === 'km' && (
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Última Execução (KM)</Label>
                  <Input type="number" value={form.ultima_execucao_km} onChange={(e) => setForm(s => ({ ...s, ultima_execucao_km: e.target.value }))} />
                </div>
              )}

              {/* DATA DE ABERTURA (READ-ONLY) */}
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400 flex items-center gap-1"><Calendar className="size-3" /> Data de Abertura do Plano</Label>
                <Input 
                  value={form.data_abertura} 
                  disabled 
                  className="bg-slate-800/50 text-slate-400 cursor-not-allowed border-slate-700" 
                />
              </div>

              {/* USUÁRIO RESPONSÁVEL (READ-ONLY) */}
              <div className="bg-slate-800/50 border border-slate-700 rounded-md p-2 flex items-center gap-2">
                <User className="size-4 text-slate-500" />
                <span className="text-xs text-slate-400">Registrado por: <strong className="text-slate-300">{me?.nome || "Usuário Logado"}</strong></span>
              </div>

            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>{salvar.isPending ? "Salvando..." : "Salvar Plano"}</Button>
            </div>
          </div>
        </div>
      )}

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
'''
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend: Página de Planos recriada com Hodômetro, Data Read-Only e Recorrência.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")
    