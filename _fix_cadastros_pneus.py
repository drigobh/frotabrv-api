import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CADASTROS_PNEUS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/pneus.py",
        "frontend/src/pages/CadastrosPneus.tsx",
        "frontend/src/App.tsx",
        "frontend/src/components/layout/Sidebar.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    path_router = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(path_router, 'r', encoding='utf-8') as f:
        c = f.read()

    if "@router.post('/marcas')" not in c:
        rotas_crud = '''
# ==========================================
# CRUD DE MARCAS
# ==========================================
@router.post("/marcas")
async def criar_marca(body: dict, _u: dict = Depends(require("write"))):
    if not await db.marcas_pneus.find_one({"nome": body.get("nome")}):
        await db.marcas_pneus.insert_one({"id": str(uuid.uuid4()), "nome": body.get("nome")})
    return {"ok": True}

@router.delete("/marcas/{id}")
async def excluir_marca(id: str, _u: dict = Depends(require("delete"))):
    await db.marcas_pneus.delete_one({"id": id})
    return {"ok": True}

# ==========================================
# CRUD DE MEDIDAS
# ==========================================
@router.post("/medidas")
async def criar_medida(body: dict, _u: dict = Depends(require("write"))):
    if not await db.medidas_pneus.find_one({"medida": body.get("medida")}):
        await db.medidas_pneus.insert_one({"id": str(uuid.uuid4()), "medida": body.get("medida")})
    return {"ok": True}

@router.delete("/medidas/{id}")
async def excluir_medida(id: str, _u: dict = Depends(require("delete"))):
    await db.medidas_pneus.delete_one({"id": id})
    return {"ok": True}

# ==========================================
# CRUD DE MODELOS
# ==========================================
@router.post("/modelos")
async def criar_modelo(body: dict, _u: dict = Depends(require("write"))):
    if not await db.modelos_pneus.find_one({"nome": body.get("nome")}):
        await db.modelos_pneus.insert_one({"id": str(uuid.uuid4()), "nome": body.get("nome")})
    return {"ok": True}

@router.delete("/modelos/{id}")
async def excluir_modelo(id: str, _u: dict = Depends(require("delete"))):
    await db.modelos_pneus.delete_one({"id": id})
    return {"ok": True}
'''
        # Inserir as rotas antes da rota que tem o parametro /{id}
        pos = c.find('# --- ROTAS COM PARÂMETRO POR ÚLTIMO ---')
        if pos != -1:
            c = c[:pos] + rotas_crud + "\n" + c[pos:]
        else:
            c += rotas_crud

        with open(path_router, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rotas de CRUD de Marcas, Medidas e Modelos criadas.")

def criar_tela_cadastros(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "CadastrosPneus.tsx")
    
    codigo = '''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Disc, Ruler, Type } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function CadastrosPneus() {
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<"marcas" | "medidas" | "modelos">("marcas");
  const [novoValor, setNovoValor] = useState("");

  const { data: marcas = [] } = useQuery({ queryKey: ["marcas-pneus"], queryFn: () => apiGet<any[]>("/pneus/marcas") });
  const { data: medidas = [] } = useQuery({ queryKey: ["medidas-pneus"], queryFn: () => apiGet<any[]>("/pneus/medidas") });
  const { data: modelos = [] } = useQuery({ queryKey: ["modelos-pneus"], queryFn: () => apiGet<any[]>("/pneus/modelos") });

  const criar = useMutation({
    mutationFn: () => {
      const rota = abaAtiva === 'marcas' ? '/pneus/marcas' : abaAtiva === 'medidas' ? '/pneus/medidas' : '/pneus/modelos';
      const body = abaAtiva === 'medidas' ? { medida: novoValor } : { nome: novoValor };
      return apiPost(rota, body);
    },
    onSuccess: () => {
      toast.success("Cadastro realizado!");
      setNovoValor("");
      qc.invalidateQueries({ queryKey: ["marcas-pneus"] });
      qc.invalidateQueries({ queryKey: ["medidas-pneus"] });
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao cadastrar.")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => {
      const rota = abaAtiva === 'marcas' ? '/pneus/marcas' : abaAtiva === 'medidas' ? '/pneus/medidas' : '/pneus/modelos';
      return apiDelete(`${rota}/${id}`);
    },
    onSuccess: () => {
      toast.success("Cadastro excluído.");
      qc.invalidateQueries({ queryKey: ["marcas-pneus"] });
      qc.invalidateQueries({ queryKey: ["medidas-pneus"] });
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    }
  });

  const listaAtual = abaAtiva === 'marcas' ? marcas : abaAtiva === 'medidas' ? medidas : modelos;

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Tabelas de Pneus"
        description="Gerencie as marcas, medidas e modelos disponíveis no sistema."
      />

      <div className="flex gap-2 mb-4 border-b border-slate-800 pb-2">
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'marcas' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => { setAbaAtiva('marcas'); setNovoValor(''); }}
        >
          <Disc className="size-4 inline mr-2" /> Marcas
        </button>
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'medidas' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => { setAbaAtiva('medidas'); setNovoValor(''); }}
        >
          <Ruler className="size-4 inline mr-2" /> Medidas
        </button>
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${abaAtiva === 'modelos' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
          onClick={() => { setAbaAtiva('modelos'); setNovoValor(''); }}
        >
          <Type className="size-4 inline mr-2" /> Modelos
        </button>
      </div>

      <div className="glass p-4 rounded-xl mb-4 flex items-end gap-3">
        <div className="grid gap-1.5 flex-1 max-w-sm">
          <Label className="text-xs text-slate-400">
            Novo {abaAtiva === 'marcas' ? 'Marca' : abaAtiva === 'medidas' ? 'Medida' : 'Modelo'}
          </Label>
          <Input 
            value={novoValor} 
            onChange={(e) => setNovoValor(e.target.value)} 
            placeholder={abaAtiva === 'medidas' ? "Ex: 295/80 R22.5" : "Ex: Michelin"} 
            onKeyDown={(e) => e.key === 'Enter' && novoValor && criar.mutate()}
          />
        </div>
        <Button onClick={() => criar.mutate()} disabled={!novoValor || criar.isPending} className="bg-sky-600 hover:bg-sky-500 h-9">
          <Plus className="size-4 mr-2" /> Adicionar
        </Button>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Nome / Valor</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center w-[100px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {listaAtual.length === 0 ? (
              <TableRow><TableCell colSpan={2} className="text-center py-6 text-slate-500">Nenhum registro encontrado.</TableCell></TableRow>
            ) : (
              listaAtual.map((item: any) => (
                <TableRow key={item.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="font-medium text-slate-200">
                    {abaAtiva === 'medidas' ? item.medida : item.nome}
                  </TableCell>
                  <TableCell className="text-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => excluir.mutate(item.id)}>
                      <Trash2 className="size-4 text-red-300" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend: Tela de Cadastros de Pneus criada.")

def fix_rotas_menu(raiz):
    # 1. Adicionar no App.tsx
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'CadastrosPneus' not in c:
        c = c.replace('import Pneus from "@/pages/Pneus";', 'import CadastrosPneus from "@/pages/CadastrosPneus";\nimport Pneus from "@/pages/Pneus";')
        c = c.replace('<Route path="/pneus"', '<Route path="/cadastros-pneus" element={<CadastrosPneus />} />\n              <Route path="/pneus"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Rota /cadastros-pneus adicionada no App.tsx.")

    # 2. Adicionar no Sidebar
    sidebar_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'Tabelas de Pneus' not in c:
            # Tenta inserir perto do link de Pneus
            c = c.replace(
                '{ label: "Pneus", href: "/pneus", icon: Disc },',
                '{ label: "Pneus", href: "/pneus", icon: Disc },\n            { label: "Tabelas de Pneus", href: "/cadastros-pneus", icon: Ruler },'
            )
            # Se não achar o Pneus, tenta perto de Veiculos
            if 'Tabelas de Pneus' not in c:
                c = c.replace(
                    '{ label: "Veículos", href: "/veiculos", icon: Truck },',
                    '{ label: "Veículos", href: "/veiculos", icon: Truck },\n            { label: "Tabelas de Pneus", href: "/cadastros-pneus", icon: Ruler },'
                )
            with open(sidebar_path, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Link 'Tabelas de Pneus' adicionado na Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    criar_tela_cadastros(raiz)
    fix_rotas_menu(raiz)
    print("\n✅ Script aplicado com sucesso! Reinicie o Vite e faça o git push.")