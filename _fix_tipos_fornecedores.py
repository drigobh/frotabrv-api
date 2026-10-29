import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_TIPOS_FORNECEDOR_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/models/tipos_fornecedores.py",
        "app/backend/routers/tipos_fornecedores.py",
        "app/backend/server.py",
        "frontend/src/pages/TiposFornecedores.tsx",
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/App.tsx"
    ]
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def criar_backend(raiz):
    # 1. Model
    model_path = os.path.join(raiz, "app", "backend", "models", "tipos_fornecedores.py")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class TipoFornecedorCreate(BaseModel):
    nome: str
    categoria_pai_id: Optional[str] = None

class TipoFornecedor(TipoFornecedorCreate):
    id: str
    created_at: str
''')
    
    # 2. Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "tipos_fornecedores.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.tipos_fornecedores import TipoFornecedorCreate, TipoFornecedor

router = APIRouter(prefix="/tipos-fornecedores", tags=["Tipos de Fornecedores"])

@router.get("", response_model=list[TipoFornecedor])
async def listar(_u: dict = Depends(require("read"))):
    docs = await db.tipos_fornecedores.find({}, {"_id": 0}).sort("nome", 1).to_list(1000)
    return [TipoFornecedor(**d) for d in docs]

@router.post("", response_model=TipoFornecedor, status_code=201)
async def criar(body: TipoFornecedorCreate, user: dict = Depends(require("write"))):
    # Verifica se já existe na mesma categoria
    existente = await db.tipos_fornecedores.find_one({
        "nome": {"$regex": f"^{body.nome}$", "$options": "i"},
        "categoria_pai_id": body.categoria_pai_id
    })
    if existente:
        raise HTTPException(409, "Já existe um tipo com este nome nesta categoria.")
    
    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["created_at"] = now_iso()
    await db.tipos_fornecedores.insert_one(dict(doc))
    return TipoFornecedor(**doc)

@router.put("/{id}", response_model=TipoFornecedor)
async def atualizar(id: str, body: TipoFornecedorCreate, user: dict = Depends(require("write"))):
    await db.tipos_fornecedores.update_one({"id": id}, {"$set": body.model_dump()})
    doc = await db.tipos_fornecedores.find_one({"id": id}, {"_id": 0})
    return TipoFornecedor(**doc)

@router.delete("/{id}")
async def excluir(id: str, user: dict = Depends(require("delete"))):
    # Verifica se tem sub-itens
    sub = await db.tipos_fornecedores.find_one({"categoria_pai_id": id})
    if sub:
        raise HTTPException(400, "Não é possível excluir uma categoria que possui sub-itens.")
    await db.tipos_fornecedores.delete_one({"id": id})
    return {"ok": True}
''')
    print("✅ Backend: Model e Router de Tipos de Fornecedores criados.")

    # 3. Registrar no server.py
    server_path = os.path.join(raiz, "app", "backend", "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        c = f.read()
        
    if 'tipos_fornecedores' not in c:
        c = c.replace(
            'from routers import parametrizacao, auth,',
            'from routers import tipos_fornecedores, parametrizacao, auth,'
        )
        c = c.replace(
            'api_router.include_router(parametrizacao.router)',
            'api_router.include_router(parametrizacao.router)\napi_router.include_router(tipos_fornecedores.router)'
        )
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router registrado no server.py.")

def criar_frontend(raiz):
    # 1. Criar a página
    page_path = os.path.join(raiz, "frontend", "src", "pages", "TiposFornecedores.tsx")
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write('''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FolderTree, Plus, Pencil, Trash2, Tag } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function TiposFornecedores() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  
  const [form, setForm] = useState({ nome: "", categoria_pai_id: "" });

  const q = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });
  const rows = q.data || [];

  const categorias = rows.filter(r => !r.categoria_pai_id).map(r => ({ value: r.id, label: r.nome }));

  const salvar = useMutation({
    mutationFn: () => editingId ? apiPut(`/tipos-fornecedores/${editingId}`, form) : apiPost("/tipos-fornecedores", form),
    onSuccess: () => { toast.success("Tipo salvo"); setOpen(false); qc.invalidateQueries({ queryKey: ["tipos-fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro"),
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/tipos-fornecedores/${id}`),
    onSuccess: () => { toast.success("Tipo excluído"); setExcluirId(null); qc.invalidateQueries({ queryKey: ["tipos-fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro"),
  });

  const abrirNovo = () => { setEditingId(null); setForm({ nome: "", categoria_pai_id: "" }); setOpen(true); };
  const abrirEdicao = (r: any) => { setEditingId(r.id); setForm({ nome: r.nome, categoria_pai_id: r.categoria_pai_id || "" }); setOpen(true); };

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Tipos de Fornecedores"
        description="Classificação para insumos, serviços, tecnologia e terceirização."
        actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Tipo</Button>}
      />

      <div className="glass overflow-hidden rounded-2xl mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Categoria Pai</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Tipo de Fornecedor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={3} className="text-center py-8 text-slate-500">Nenhum tipo cadastrado.</TableCell></TableRow>
            )}
            {rows.filter(r => !r.categoria_pai_id).map(cat => (
              <>
                <TableRow key={cat.id} className="border-slate-800 bg-slate-800/30">
                  <TableCell colSpan={3} className="font-bold text-slate-200 py-2">
                    <div className="flex items-center gap-2"><FolderTree className="size-4 text-sky-400"/> {cat.nome}</div>
                  </TableCell>
                </TableRow>
                {rows.filter(r => r.categoria_pai_id === cat.id).map(sub => (
                  <TableRow key={sub.id} className="border-slate-800/50 hover:bg-slate-800/20">
                    <TableCell className="text-slate-400 pl-10 text-xs">└─ Subcategoria</TableCell>
                    <TableCell className="text-slate-300 font-medium"><Tag className="size-3 inline mr-2 text-slate-500"/>{sub.nome}</TableCell>
                    <TableCell className="text-center">
                      <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(sub)}><Pencil className="size-4 text-sky-400" /></Button>
                      <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(sub.id)}><Trash2 className="size-4 text-red-300" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editingId ? "Editar Tipo" : "Novo Tipo"}</DialogTitle></DialogHeader>
          <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="grid gap-1.5">
              <Label>Categoria Pai (Opcional)</Label>
              <FieldSelect value={form.categoria_pai_id} onChange={(v) => setForm(s => ({ ...s, categoria_pai_id: v }))} options={[{ value: "", label: "Nenhuma (Criar Categoria Principal)" }, ...categorias]} />
            </div>
            <div className="grid gap-1.5">
              <Label>Nome do Tipo *</Label>
              <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: Peças e componentes" required />
            </div>
            <DialogFooter><Button type="submit">Salvar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      
      <Dialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)}>
        <DialogContent>
          <DialogHeader><DialogTitle>Excluir Tipo?</DialogTitle></DialogHeader>
          <p className="text-sm text-slate-400">Tem certeza que deseja excluir este tipo de fornecedor?</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setExcluirId(null)}>Cancelar</Button>
            <Button variant="destructive" onClick={() => excluirId && excluir.mutate(excluirId)}>Excluir</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
''')
    print("✅ Frontend: Página TiposFornecedores.tsx criada.")

    # 2. Adicionar Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c_app = f.read()
    if 'TiposFornecedores' not in c_app:
        c_app = c_app.replace('import Fornecedores from', 'import TiposFornecedores from "@/pages/TiposFornecedores";\nimport Fornecedores from')
        c_app = c_app.replace('<Route path="/fornecedores"', '<Route path="/tipos-fornecedores" element={<TiposFornecedores />} />\n              <Route path="/fornecedores"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c_app)
        print("✅ Frontend: Rota /tipos-fornecedores adicionada no App.tsx.")

    # 3. Adicionar Item no Sidebar
    side_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(side_path, 'r', encoding='utf-8') as f:
        c_side = f.read()
    if '/tipos-fornecedores' not in c_side:
        # Coloca logo após o item de Fornecedores
        if 'label: "Fornecedores"' in c_side:
            c_side = c_side.replace(
                '{ label: "Fornecedores", icon: Truck, path: "/fornecedores" },',
                '{ label: "Fornecedores", icon: Truck, path: "/fornecedores" },\n      { label: "Tipos de Fornecedores", icon: Tag, path: "/tipos-fornecedores" },'
            )
            if 'Tag' not in c_side.split('lucide-react')[0]:
                c_side = c_side.replace('import { ', 'import { Tag, ')
            with open(side_path, 'w', encoding='utf-8') as f:
                f.write(c_side)
            print("✅ Frontend: Item 'Tipos de Fornecedores' adicionado ao Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    criar_backend(raiz)
    criar_frontend(raiz)
    print("\n✅ Estrutura de Tipos de Fornecedores criada com sucesso!")