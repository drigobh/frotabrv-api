import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_EMPRESA_CONTATOS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/models/fornecedores.py",
        "app/backend/models/empresa.py",
        "app/backend/routers/empresa.py",
        "app/backend/server.py",
        "frontend/src/pages/Fornecedores.tsx",
        "frontend/src/pages/Empresa.tsx",
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/App.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

# ==========================================
# PARTE 1: BACKEND - FORNECEDORES (Contato e Whatsapp)
# ==========================================
def fix_backend_fornecedores(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    if not os.path.exists(caminho): return
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona os campos se não existirem
    if 'contato:' not in c:
        c = c.replace(
            'telefone: str | None = None',
            'telefone: str | None = None\n    contato: str | None = None\n    whatsapp: str | None = None'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend Fornecedores: campos 'contato' e 'whatsapp' adicionados.")

# ==========================================
# PARTE 2: BACKEND - EMPRESA
# ==========================================
def criar_backend_empresa(raiz):
    # 1. Model
    model_path = os.path.join(raiz, "app", "backend", "models", "empresa.py")
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class EmpresaBase(BaseModel):
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: str
    ie: Optional[str] = None
    im: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    site: Optional[str] = None
    tipo_unidade: str = "Matriz"  # Matriz ou Filial
    logo_base64: Optional[str] = None

class Empresa(EmpresaBase):
    id: str
    created_at: str
    updated_at: str
''')

    # 2. Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "empresa.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''import uuid
from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.empresa import EmpresaBase, Empresa

router = APIRouter(prefix="/empresa", tags=["Empresa"])

@router.get("", response_model=Empresa)
async def obter(_u: dict = Depends(require("read"))):
    doc = await db.empresa.find_one({"id": "empresa_atual"}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Empresa não cadastrada")
    return Empresa(**doc)

@router.put("", response_model=Empresa)
async def atualizar(body: EmpresaBase, user: dict = Depends(require("write"))):
    doc = body.model_dump()
    doc["id"] = "empresa_atual"
    doc["updated_at"] = now_iso()
    
    existente = await db.empresa.find_one({"id": "empresa_atual"})
    if not existente:
        doc["created_at"] = doc["updated_at"]
    else:
        doc["created_at"] = existente.get("created_at", doc["updated_at"])

    await db.empresa.update_one(
        {"id": "empresa_atual"},
        {"$set": doc},
        upsert=True
    )
    return Empresa(**doc)
''')
    print("✅ Backend Empresa: Model e Router criados.")

    # 3. Registrar no server.py
    server_path = os.path.join(raiz, "app", "backend", "server.py")
    with open(server_path, 'r', encoding='utf-8') as f:
        c = f.read()
        
    if 'empresa' not in c:
        c = c.replace(
            'from routers import',
            'from routers import empresa,\nfrom routers import'
        )
        c = c.replace(
            'api_router.include_router(parametrizacao.router)',
            'api_router.include_router(parametrizacao.router)\napi_router.include_router(empresa.router)'
        )
        with open(server_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router da Empresa registrado no server.py.")

# ==========================================
# PARTE 3: FRONTEND - FORNECEDORES
# ==========================================
def fix_frontend_fornecedores(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar contato e whatsapp no estado do form
    if 'contato:' not in c:
        c = c.replace(
            'telefone: "", email: "",',
            'telefone: "", contato: "", whatsapp: "", email: "",'
        )
        c = c.replace(
            'telefone: r.telefone || "",',
            'telefone: r.telefone || "", contato: r.contato || "", whatsapp: r.whatsapp || "",'
        )

    # 2. Adicionar os campos no modal (abaixo do Email)
    if 'WhatsApp' not in c:
        alvo = '<div className="grid gap-1"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9" /></div>'
        novo_campo = '''<div className="grid gap-1"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9" /></div>
            
            <div className="grid gap-1">
              <Label className="text-xs">Contato</Label>
              <Input value={form.contato} onChange={(e) => setForm(s => ({ ...s, contato: e.target.value }))} placeholder="Nome do contato" className="h-9" />
            </div>
            <div className="grid gap-1">
              <Label className="text-xs flex items-center gap-1">
                <MessageCircle className="size-3 text-emerald-500" /> WhatsApp
              </Label>
              <Input value={form.whatsapp} onChange={(e) => setForm(s => ({ ...s, whatsapp: e.target.value }))} placeholder="(00) 00000-0000" className="h-9" />
            </div>'''
        c = c.replace(alvo, novo_campo)
        
        # Importar ícone MessageCircle
        if 'MessageCircle' not in c.split('lucide-react')[0]:
            c = c.replace('import { Building2,', 'import { MessageCircle, Building2,')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend Fornecedores: campos Contato e WhatsApp adicionados.")

# ==========================================
# PARTE 4: FRONTEND - EMPRESA E MENUS
# ==========================================
def criar_frontend_empresa(raiz):
    # 1. Criar a Página
    page_path = os.path.join(raiz, "frontend", "src", "pages", "Empresa.tsx")
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write('''import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Building, Upload, MapPin, Phone, Mail, Globe, FileText } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FieldSelect } from "@/components/common/FieldSelect";

export default function Empresa() {
  const qc = useQueryClient();
  const { data: empresa, isLoading } = useQuery({
    queryKey: ["empresa"],
    queryFn: async () => {
      try { return await apiGet<any>("/empresa"); }
      catch { return null; }
    }
  });

  const [form, setForm] = useState<any>({
    razao_social: "", nome_fantasia: "", cnpj: "", ie: "", im: "",
    endereco: "", bairro: "", cidade: "", estado: "", cep: "",
    telefone: "", email: "", site: "", tipo_unidade: "Matriz", logo_base64: ""
  });

  useEffect(() => {
    if (empresa) setForm((s: any) => ({ ...s, ...empresa }));
  }, [empresa]);

  const salvar = useMutation({
    mutationFn: () => apiPut("/empresa", form),
    onSuccess: () => { toast.success("Dados da empresa salvos!"); qc.invalidateQueries({ queryKey: ["empresa"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar"),
  });

  const handleLogo = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => setForm((s: any) => ({ ...s, logo_base64: reader.result as string }));
      reader.readAsDataURL(file);
    }
  };

  if (isLoading) return <div className="p-8 text-center text-slate-400">Carregando...</div>;

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Dados da Empresa"
        description="Cadastro da matriz e filiais, logomarca e identificação."
        actions={<Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="bg-sky-600 hover:bg-sky-500"><FileText className="size-4 mr-2" /> {salvar.isPending ? "Salvando..." : "Salvar Dados"}</Button>}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
        {/* COLUNA ESQUERDA: Logomarca e Tipo */}
        <div className="space-y-4">
          <div className="glass rounded-2xl p-6 flex flex-col items-center justify-center text-center">
            <div className="size-32 rounded-2xl border-2 border-dashed border-slate-700 bg-slate-900/50 flex items-center justify-center mb-4 overflow-hidden relative">
              {form.logo_base64 ? (
                <img src={form.logo_base64} alt="Logo" className="w-full h-full object-contain" />
              ) : (
                <Building className="size-12 text-slate-600" />
              )}
            </div>
            <Label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2">
              <Upload className="size-4" /> Alterar Logomarca
              <input type="file" accept="image/*" className="hidden" onChange={handleLogo} />
            </Label>
            <p className="text-[10px] text-slate-500 mt-2">PNG ou JPG, máx 2MB.</p>
          </div>

          <div className="glass rounded-2xl p-4">
            <Label className="text-xs mb-2 block">Tipo de Unidade</Label>
            <FieldSelect value={form.tipo_unidade} onChange={(v) => setForm((s: any) => ({ ...s, tipo_unidade: v }))} options={[{ value: "Matriz", label: "Matriz" }, { value: "Filial", label: "Filial" }]} />
          </div>
        </div>

        {/* COLUNA DIREITA: Formulário */}
        <div className="md:col-span-2 glass rounded-2xl p-6 space-y-4">
          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2 flex items-center gap-2"><Building className="size-4 text-sky-400" /> Dados Cadastrais</h3>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Razão Social *</Label><Input value={form.razao_social} onChange={e => setForm((s: any) => ({ ...s, razao_social: e.target.value }))} className="h-9" required /></div>
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Nome Fantasia</Label><Input value={form.nome_fantasia} onChange={e => setForm((s: any) => ({ ...s, nome_fantasia: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">CNPJ *</Label><Input value={form.cnpj} onChange={e => setForm((s: any) => ({ ...s, cnpj: e.target.value }))} className="h-9" required /></div>
            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1.5"><Label className="text-xs">I.E.</Label><Input value={form.ie} onChange={e => setForm((s: any) => ({ ...s, ie: e.target.value }))} className="h-9" /></div>
              <div className="grid gap-1.5"><Label className="text-xs">I.M.</Label><Input value={form.im} onChange={e => setForm((s: any) => ({ ...s, im: e.target.value }))} className="h-9" /></div>
            </div>
          </div>

          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2 flex items-center gap-2 mt-6"><MapPin className="size-4 text-sky-400" /> Endereço</h3>
          
          <div className="grid grid-cols-4 gap-3">
            <div className="col-span-3 grid gap-1.5"><Label className="text-xs">Endereço</Label><Input value={form.endereco} onChange={e => setForm((s: any) => ({ ...s, endereco: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">CEP</Label><Input value={form.cep} onChange={e => setForm((s: any) => ({ ...s, cep: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">Bairro</Label><Input value={form.bairro} onChange={e => setForm((s: any) => ({ ...s, bairro: e.target.value }))} className="h-9" /></div>
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Cidade</Label><Input value={form.cidade} onChange={e => setForm((s: any) => ({ ...s, cidade: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">UF</Label><Input value={form.estado} onChange={e => setForm((s: any) => ({ ...s, estado: e.target.value }))} maxLength={2} className="h-9 uppercase" /></div>
          </div>

          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-2 flex items-center gap-2 mt-6"><Phone className="size-4 text-sky-400" /> Contato</h3>
          
          <div className="grid grid-cols-2 gap-3">
            <div className="grid gap-1.5"><Label className="text-xs">Telefone</Label><Input value={form.telefone} onChange={e => setForm((s: any) => ({ ...s, telefone: e.target.value }))} className="h-9" /></div>
            <div className="grid gap-1.5"><Label className="text-xs">E-mail</Label><Input type="email" value={form.email} onChange={e => setForm((s: any) => ({ ...s, email: e.target.value }))} className="h-9" /></div>
            <div className="col-span-2 grid gap-1.5"><Label className="text-xs">Site</Label><Input value={form.site} onChange={e => setForm((s: any) => ({ ...s, site: e.target.value }))} placeholder="https://" className="h-9" /></div>
          </div>
        </div>
      </div>
    </div>
  );
}
''')
    print("✅ Frontend Empresa: Página criada.")

    # 2. Adicionar Rota no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c_app = f.read()
    if 'Empresa' not in c_app:
        c_app = c_app.replace('import Parametrizacao from', 'import Empresa from "@/pages/Empresa";\nimport Parametrizacao from')
        c_app = c_app.replace('<Route path="/admin/parametrizacao"', '<Route path="/admin/empresa" element={<Empresa />} />\n              <Route path="/admin/parametrizacao"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c_app)
        print("✅ Frontend: Rota /admin/empresa adicionada no App.tsx.")

    # 3. Adicionar Item no Sidebar
    side_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(side_path, 'r', encoding='utf-8') as f:
        c_side = f.read()
    if '/admin/empresa' not in c_side:
        if 'label: "Parametrização"' in c_side:
            c_side = c_side.replace(
                '{ label: "Parametrização", icon: Settings, path: "/admin/parametrizacao" }',
                '{ label: "Empresa", icon: Building, path: "/admin/empresa" },\n      { label: "Parametrização", icon: Settings, path: "/admin/parametrizacao" }'
            )
            if 'Building' not in c_side.split('lucide-react')[0]:
                c_side = c_side.replace('import { ', 'import { Building, ')
            with open(side_path, 'w', encoding='utf-8') as f:
                f.write(c_side)
            print("✅ Frontend: Item 'Empresa' adicionado ao Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend_fornecedores(raiz)
    criar_backend_empresa(raiz)
    fix_frontend_fornecedores(raiz)
    criar_frontend_empresa(raiz)
    print("\n✅ Todos os scripts aplicados com sucesso! Faça o git push.")