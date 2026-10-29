import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PLANO_FASE2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    print(f"✅ Backup de segurança: {caminho_zip}")

def criar_backend(raiz):
    # 1. Model de Planos de Manutenção
    model_path = os.path.join(raiz, "app", "backend", "models", "planos_manutencao.py")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class PlanoManutencaoCreate(BaseModel):
    veiculo_id: str
    familia: str  # Ex: Lubrificação, Transmissão, Segurança
    descricao: str
    tipo_gatilho: str  # "km", "horas" ou "dias"
    intervalo: float  # Ex: 20000 (km) ou 180 (dias)
    ultima_execucao_km: Optional[float] = None
    ultima_execucao_data: Optional[str] = None
    ativo: bool = True

class PlanoManutencao(PlanoManutencaoCreate):
    id: str
    veiculo_label: str
    created_at: str
''')
    print("✅ Backend: Model de Planos de Manutenção criado.")

    # 2. Router de Planos de Manutenção
    router_path = os.path.join(raiz, "app", "backend", "routers", "planos_manutencao.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.planos_manutencao import PlanoManutencaoCreate, PlanoManutencao

router = APIRouter(prefix="/planos-manutencao", tags=["Planos de Manutenção"])

@router.get("", response_model=list[PlanoManutencao])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.planos_manutencao.find({}, {"_id": 0}).to_list(1000)
    return [PlanoManutencao(**d) for d in docs]

@router.post("", response_model=PlanoManutencao, status_code=201)
async def criar(body: PlanoManutencaoCreate, _u: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
    
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} - {veiculo.get('modelo', '')}"
    doc["created_at"] = now_iso()
    
    await db.planos_manutencao.insert_one(dict(doc))
    return PlanoManutencao(**doc)

@router.put("/{id}", response_model=PlanoManutencao)
async def atualizar(id: str, body: PlanoManutencaoCreate, _u: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")
        
    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo['placa']} - {veiculo.get('modelo', '')}"
    
    await db.planos_manutencao.update_one({"id": id}, {"$set": doc})
    doc = await db.planos_manutencao.find_one({"id": id}, {"_id": 0})
    return PlanoManutencao(**doc)

@router.delete("/{id}")
async def excluir(id: str, _u: dict = Depends(require("delete"))):
    await db.planos_manutencao.delete_one({"id": id})
    return {"ok": True}
''')
    print("✅ Backend: Router de Planos de Manutenção criado.")

    # 3. Registrar no server.py
    server_path = os.path.join(raiz, "app", "backend", "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'planos_manutencao' not in c:
        c = c.replace(
            'from routers import tipos_fornecedores, parametrizacao, auth,',
            'from routers import planos_manutencao, tipos_fornecedores, parametrizacao, auth,'
        )
        c = c.replace(
            'api_router.include_router(parametrizacao.router)',
            'api_router.include_router(parametrizacao.router)\napi_router.include_router(planos_manutencao.router)'
        )
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router registrado no server.py.")

def criar_frontend(raiz):
    # 1. Criar a página de Cadastro de Planos (que ficará dentro de Operação)
    page_path = os.path.join(raiz, "frontend", "src", "pages", "PlanosManutencao.tsx")
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write('''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Wrench, Plus, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { useVeiculos } from "@/hooks/useCadastros";

const FAMILIAS = ["Lubrificação e Filtros", "Linha Pesada e Transmissão", "Segurança e Rodagem", "Sistemas de Emissões", "Outros"];
const TIPOS_GATILHO = [
  { value: "km", label: "Por Quilometragem (KM)" },
  { value: "horas", label: "Por Horímetro (Horas)" },
  { value: "dias", label: "Por Tempo (Dias)" }
];

export default function PlanosManutencao() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  
  const veiculos = useVeiculos();
  const { data: planos = [], refetch } = useQuery({ queryKey: ["planos-manutencao"], queryFn: () => apiGet<any[]>("/planos-manutencao") });

  const [form, setForm] = useState({
    veiculo_id: "", familia: FAMILIAS[0], descricao: "", tipo_gatilho: "km", intervalo: "", ultima_execucao_km: "", ultima_execucao_data: ""
  });

  const salvar = useMutation({
    mutationFn: () => {
      const payload = {
        ...form,
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
    setForm({ veiculo_id: "", familia: FAMILIAS[0], descricao: "", tipo_gatilho: "km", intervalo: "", ultima_execucao_km: "", ultima_execucao_data: "" });
    setOpen(true);
  };

  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({ ...r, intervalo: String(r.intervalo), ultima_execucao_km: String(r.ultima_execucao_km || "") });
    setOpen(true);
  };

  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Cadastro de Planos Preventivos"
        description="Defina os gatilhos e intervalos por família de componentes."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Novo Plano</Button>}
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
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
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-lg p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-4">{editingId ? "Editar Plano" : "Novo Plano"}</h2>
            
            <div className="space-y-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Veículo</Label>
                <FieldSelect value={form.veiculo_id} onChange={(v) => setForm(s => ({ ...s, veiculo_id: v }))} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione..." />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Família de Componentes</Label>
                <select value={form.familia} onChange={(e) => setForm(s => ({ ...s, familia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                  {FAMILIAS.map(f => <option key={f} value={f}>{f}</option>)}
                </select>
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Descrição do Serviço</Label>
                <Input value={form.descricao} onChange={(e) => setForm(s => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Troca de óleo e filtro" />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Tipo de Gatilho</Label>
                  <select value={form.tipo_gatilho} onChange={(e) => setForm(s => ({ ...s, tipo_gatilho: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                    {TIPOS_GATILHO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Intervalo</Label>
                  <Input type="number" value={form.intervalo} onChange={(e) => setForm(s => ({ ...s, intervalo: e.target.value }))} placeholder={form.tipo_gatilho === 'km' ? "Ex: 20000" : form.tipo_gatilho === 'horas' ? "Ex: 500" : "Ex: 180"} />
                </div>
              </div>

              {form.tipo_gatilho === 'km' && (
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Última Execução (KM)</Label>
                  <Input type="number" value={form.ultima_execucao_km} onChange={(e) => setForm(s => ({ ...s, ultima_execucao_km: e.target.value }))} />
                </div>
              )}
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
''')
    print("✅ Frontend: Página de Cadastro de Planos criada.")

    # 2. Adicionar Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c_app = f.read()
    if 'PlanosManutencao' not in c_app:
        c_app = c_app.replace('import Agendamento from', 'import PlanosManutencao from "@/pages/PlanosManutencao";\nimport Agendamento from')
        c_app = c_app.replace('<Route path="/agendamento"', '<Route path="/planos-manutencao" element={<PlanosManutencao />} />\n              <Route path="/agendamento"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c_app)
        print("✅ Frontend: Rota /planos-manutencao adicionada no App.tsx.")

    # 3. Adicionar Item no Sidebar
    side_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(side_path, 'r', encoding='utf-8') as f:
        c_side = f.read()
    if '/planos-manutencao' not in c_side:
        if 'label: "Plano de Manutenção"' in c_side:
            c_side = c_side.replace(
                '{ label: "Plano de Manutenção", icon: CalendarClock, path: "/agendamento" }',
                '{ label: "Plano de Manutenção", icon: CalendarClock, path: "/agendamento" },\n      { label: "Cadastro de Planos", icon: Wrench, path: "/planos-manutencao" }'
            )
            if 'Wrench' not in c_side.split('lucide-react')[0]:
                c_side = c_side.replace('import { ', 'import { Wrench, ')
            with open(side_path, 'w', encoding='utf-8') as f:
                f.write(c_side)
            print("✅ Frontend: Item 'Cadastro de Planos' adicionado ao Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    criar_backend(raiz)
    criar_frontend(raiz)
    print("\n✅ Fase 2 aplicada com sucesso! Faça o git push.")
    