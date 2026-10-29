import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PLANOS_REFINADO_{agora}.zip")
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

    # Adicionar campos carreta_id e created_by
    if 'carreta_id' not in c:
        c = c.replace(
            'veiculo_id: str',
            'veiculo_id: str | None = None\n    carreta_id: str | None = None'
        )
        c = c.replace(
            'veiculo_label: str',
            'veiculo_label: str\n    created_by: str'
        )
        # Ajustar o Create também
        c = c.replace(
            'class PlanoManutencaoCreate(BaseModel):\n    veiculo_id: str',
            'class PlanoManutencaoCreate(BaseModel):\n    veiculo_id: str | None = None\n    carreta_id: str | None = None'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend Model: campos 'carreta_id' e 'created_by' adicionados.")

    # Atualizar o Router para salvar o created_by e o carreta_id
    router_path = os.path.join(raiz, "app", "backend", "routers", "planos_manutencao.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()

    # No POST
    if 'doc["created_by"] = user["nome"]' not in c:
        c = c.replace(
            'doc["created_at"] = now_iso()',
            'doc["created_at"] = now_iso()\n    doc["created_by"] = user["nome"]'
        )
        # Ajustar a busca de veículo (pode ser carreta)
        c = c.replace(
            'veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})',
            '''veiculo = None
    if body.veiculo_id:
        veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    elif body.carreta_id:
        veiculo = await db.carretas.find_one({"id": body.carreta_id}, {"_id": 0})'''
        )
        # Ajustar o label
        c = c.replace(
            'doc["veiculo_label"] = f"{veiculo[\'placa\']} - {veiculo.get(\'modelo\', \'\')}"',
            'doc["veiculo_label"] = f"{veiculo.get(\'placa\', veiculo.get(\'codigo\', \'\'))} - {veiculo.get(\'modelo\', \'\')}"'
        )
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend Router: gravação de 'created_by' e suporte a carretas.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "PlanosManutencao.tsx")
    
    codigo = '''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Wrench, Plus, Pencil, Trash2, Truck, Info, User } from "lucide-react";
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
  { value: "dias", label: "Por Tempo (Dias)" }
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
  
  const [form, setForm] = useState({
    veiculo_id: "", carreta_id: "", familia: FAMILIAS[0].nome, descricao: "", tipo_gatilho: "km", intervalo: "", ultima_execucao_km: "", ultima_execucao_data: ""
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

  const abrirNovo = () => {
    setEditingId(null);
    setTipoAtivo("cavalo");
    setForm({ veiculo_id: "", carreta_id: "", familia: FAMILIAS[0].nome, descricao: "", tipo_gatilho: "km", intervalo: "", ultima_execucao_km: "", ultima_execucao_data: "" });
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
              <TableHead className="text-xs uppercase text-slate-500">Veículo / Carreta</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Família</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Descrição</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Gatilho</TableHead>
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
                  A cada {p.intervalo} {p.tipo_gatilho === 'km' ? 'km' : p.tipo_gatilho === 'horas' ? 'horas' : 'dias'}
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
                  <button 
                    className={`flex-1 py-1.5 text-sm rounded font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => { setTipoAtivo('cavalo'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); }}
                  >
                    Cavalo Mecânico
                  </button>
                  <button 
                    className={`flex-1 py-1.5 text-sm rounded font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => { setTipoAtivo('carreta'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); }}
                  >
                    Carreta / Semi
                  </button>
                </div>
              </div>

              {/* SELETOR DE VEÍCULO OU CARRETA */}
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">{tipoAtivo === 'cavalo' ? 'Cavalo Mecânico' : 'Carreta'}</Label>
                {tipoAtivo === 'cavalo' ? (
                  <FieldSelect value={form.veiculo_id} onChange={(v) => setForm(s => ({ ...s, veiculo_id: v }))} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione o Cavalo..." />
                ) : (
                  <FieldSelect value={form.carreta_id} onChange={(v) => setForm(s => ({ ...s, carreta_id: v }))} options={carretas.map((c: any) => ({ value: c.id, label: `${c.codigo} - ${c.tipo}` }))} placeholder="Selecione a Carreta..." />
                )}
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
              
              {/* GATILHO E INTERVALO */}
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Tipo de Gatilho</Label>
                  <select value={form.tipo_gatilho} onChange={(e) => setForm(s => ({ ...s, tipo_gatilho: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                    {TIPOS_GATILHO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Intervalo</Label>
                  <Input type="number" value={form.intervalo} onChange={(e) => setForm(s => ({ ...s, intervalo: e.target.value }))} placeholder={form.tipo_gatilho === 'km' ? "Ex: 20000" : "Ex: 180"} />
                </div>
              </div>

              {form.tipo_gatilho === 'km' && (
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Última Execução (KM)</Label>
                  <Input type="number" value={form.ultima_execucao_km} onChange={(e) => setForm(s => ({ ...s, ultima_execucao_km: e.target.value }))} />
                </div>
              )}

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
    print("✅ Frontend: Página de Planos recriada com flag, guia e auditoria.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")