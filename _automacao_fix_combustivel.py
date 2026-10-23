import os

def criar_backend(raiz):
    # 1. Modelo
    model_path = os.path.join(raiz, "app", "backend", "models", "combustiveis.py")
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel, Field
from typing import Optional

class CombustivelCreate(BaseModel):
    nome: str = Field(min_length=2)
    is_arla: bool = False
    ativo: bool = True

class Combustivel(CombustivelCreate):
    id: str
''')

    # 2. Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "combustiveis.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.combustiveis import Combustivel, CombustivelCreate
import uuid

router = APIRouter(prefix="/combustiveis", tags=["combustiveis"])

@router.get("", response_model=list[Combustivel])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.combustiveis.find({}, {"_id": 0}).sort("nome", 1).to_list(1000)
    return docs

@router.post("", response_model=Combustivel, status_code=201)
async def criar(body: CombustivelCreate, _u: dict = Depends(require("write"))):
    if await db.combustiveis.find_one({"nome": body.nome}):
        raise HTTPException(409, "Combustível já cadastrado")
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.combustiveis.insert_one(doc)
    return doc
''')

    # 3. Registrar no server.py
    server_path = os.path.join(raiz, "app", "backend", "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "combustiveis" not in content:
        content = content.replace("from routers import auth", "from routers import auth, combustiveis")
        content = content.replace("api_router.include_router(auth.router)", "api_router.include_router(auth.router)\napi_router.include_router(combustiveis.router)")
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(content)
    print("✅ Backend de Combustíveis criado.")

def criar_frontend(raiz):
    # 1. Página de Combustíveis
    page_path = os.path.join(raiz, "frontend", "src", "pages", "Combustiveis.tsx")
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write('''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Fuel, Plus, Check, X } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function Combustiveis() {
  const qc = useQueryClient();
  const [nome, setNome] = useState("");
  const [isArla, setIsArla] = useState(false);

  const q = useQuery({ queryKey: ["combustiveis"], queryFn: () => apiGet<any[]>("/combustiveis") });
  const rows = q.data ?? [];

  const criar = useMutation({
    mutationFn: () => apiPost("/combustiveis", { nome, is_arla: isArla, ativo: true }),
    onSuccess: () => { toast.success("Cadastrado"); setNome(""); setIsArla(false); qc.invalidateQueries({ queryKey: ["combustiveis"] }); },
    onError: (e: any) => toast.error(e.message),
  });

  return (
    <div>
      <PageHeader eyebrow="Cadastros" title="Tipos de Combustível" description="Gerencie os combustíveis. Arla não entra no cálculo de média." />
      <div className="mb-6 flex items-end gap-3 glass p-4 rounded-xl">
        <div className="grid gap-1.5 flex-1">
          <Label>Nome do Combustível</Label>
          <Input value={nome} onChange={(e) => setNome(e.target.value)} placeholder="Ex: Diesel S-10" />
        </div>
        <div className="flex items-center gap-2 mb-2">
          <input type="checkbox" checked={isArla} onChange={(e) => setIsArla(e.target.checked)} className="size-4" />
          <Label>É Arla? (Não calcula média)</Label>
        </div>
        <Button onClick={() => criar.mutate()} disabled={!nome}><Plus className="size-4 mr-2" /> Adicionar</Button>
      </div>
      <div className="glass rounded-2xl overflow-hidden">
        <Table>
          <TableHeader><TableRow><TableHead>Nome</TableHead><TableHead>É Arla?</TableHead></TableRow></TableHeader>
          <TableBody>
            {rows.map(r => (
              <TableRow key={r.id}>
                <TableCell>{r.nome}</TableCell>
                <TableCell>{r.is_arla ? "Sim" : "Não"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
''')
    # Fix missing imports in the generated file (Label)
    with open(page_path, 'r', encoding='utf-8') as f:
        c = f.read()
        c = c.replace('import { Input } from "@/components/ui/input";', 'import { Input } from "@/components/ui/input";\nimport { Label } from "@/components/ui/label";')
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(c)

    # 2. Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        app_content = f.read()
    if "Combustiveis" not in app_content:
        app_content = app_content.replace("import Carretas from", "import Combustiveis from '@/pages/Combustiveis';\nimport Carretas from")
        app_content = app_content.replace('<Route path="cadastros/motoristas"', '<Route path="cadastros/combustiveis" element={<Combustiveis />} />\n          <Route path="cadastros/motoristas"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_content)

    # 3. Link no Sidebar.tsx
    sidebar_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(sidebar_path, 'r', encoding='utf-8') as f:
        sidebar_content = f.read()
    if "combustiveis" not in sidebar_content:
        sidebar_content = sidebar_content.replace('{ label: "Motoristas", icon: Users, path: "/cadastros/motoristas" },', '{ label: "Motoristas", icon: Users, path: "/cadastros/motoristas" },\n        { label: "Combustíveis", icon: Fuel, path: "/cadastros/combustiveis" },')
        with open(sidebar_path, 'w', encoding='utf-8') as f:
            f.write(sidebar_content)

def patch_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar hook de combustíveis
    if "useCombustiveis" not in c:
        c = c.replace('import { useMotoristas, useVeiculos } from "@/hooks/useCadastros";', 'import { useMotoristas, useVeiculos } from "@/hooks/useCadastros";\nimport { useQuery as useQueryComb } from "@tanstack/react-query";')

    # 2. Adicionar campo no form
    if 'name="combustivel_id"' not in c and 'Combustível *' not in c:
        c = c.replace(
            '<div className="col-span-2 grid gap-1.5"><Label>Motorista</Label>',
            '''<div className="col-span-2 grid gap-1.5">
              <Label>Combustível *</Label>
              <FieldSelect value={form.combustivel_id || ""} onChange={(v) => setForm(s => ({ ...s, combustivel_id: v }))} options={combOpts} placeholder="Selecione o combustível" testId="form-combustivel" />
            </div>
            <div className="col-span-2 grid gap-1.5"><Label>Motorista</Label>'''
        )

    # 3. Adicionar ao estado inicial
    if "combustivel_id" not in c:
        c = c.replace('numero_nf: "", chave_nfe: "", hora: "", cnpj: "", fornecedor: "", origem: "excel", produto: "DIESEL"', 'numero_nf: "", chave_nfe: "", hora: "", cnpj: "", fornecedor: "", origem: "excel", produto: "DIESEL", combustivel_id: ""')

    # 4. Adicionar ao payload de salvamento
    if "combustivel_id: form.combustivel_id" not in c:
        c = c.replace('const payload = { ...form, motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id', 'const payload = { ...form, combustivel_id: form.combustivel_id, motorista_id: form.motorista_id === NENHUM ? null : form.motorista_id')

    # 5. Atualizar a lógica do useMemo (filtrar Arla)
    # A lógica antiga tentava adivinhar pelo nome "ARLA". Agora vamos usar o ID.
    # Mas como o ID precisa ser buscado, faremos isso no frontend.
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

    # Adicionar o hook e as opções no inicio do componente
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if "const combQ = useQueryComb" not in c:
        c = c.replace('const motoristas = useMotoristas();', '''const motoristas = useMotoristas();
  const combQ = useQueryComb({ queryKey: ["combustiveis"], queryFn: () => apiGet<any[]>("/combustiveis") });
  const combOpts = (combQ.data ?? []).filter(c => c.ativo).map(c => ({ value: c.id, label: c.nome }));''')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Formulário de Abastecimento atualizado com Combustível.")

if __name__ == "__main__":
    raiz = os.getcwd()
    criar_backend(raiz)
    criar_frontend(raiz)
    patch_abastecimentos(raiz)