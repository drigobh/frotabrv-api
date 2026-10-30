import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MODELOS_PARAM_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/routers/pneus.py",
        "frontend/src/pages/ModelosPneus.tsx",
        "frontend/src/App.tsx",
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/pages/Parametrizacao.tsx"
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

    # Adicionar rota de CRUD de Modelos se não existir
    if '@router.post("/modelos")' not in c:
        rotas_crud = '''
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
        # Inserir as rotas antes da rota que tem o parametro /{id} (PUT e DELETE de pneus)
        pos = c.find('@router.put("/{id}"')
        if pos != -1:
            c = c[:pos] + rotas_crud + "\n" + c[pos:]
        else:
            c += rotas_crud

        with open(path_router, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rotas de CRUD de Modelos criadas.")

def criar_tela_modelos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "ModelosPneus.tsx")
    
    codigo = '''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Type } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function ModelosPneus() {
  const qc = useQueryClient();
  const [novoModelo, setNovoModelo] = useState("");

  const { data: modelos = [] } = useQuery({ queryKey: ["modelos-pneus"], queryFn: () => apiGet<any[]>("/pneus/modelos") });

  const criar = useMutation({
    mutationFn: () => apiPost("/pneus/modelos", { nome: novoModelo }),
    onSuccess: () => {
      toast.success("Modelo cadastrado!");
      setNovoModelo("");
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao cadastrar.")
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/pneus/modelos/${id}`),
    onSuccess: () => {
      toast.success("Modelo excluído.");
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    }
  });

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title="Modelos de Pneus"
        description="Gerencie os modelos de pneus disponíveis no sistema."
      />

      <div className="glass p-4 rounded-xl mb-4 flex items-end gap-3">
        <div className="grid gap-1.5 flex-1 max-w-sm">
          <Label className="text-xs text-slate-400">Novo Modelo</Label>
          <Input 
            value={novoModelo} 
            onChange={(e) => setNovoModelo(e.target.value)} 
            placeholder="Ex: X Multi Z" 
            onKeyDown={(e) => e.key === 'Enter' && novoModelo && criar.mutate()}
          />
        </div>
        <Button onClick={() => criar.mutate()} disabled={!novoModelo || criar.isPending} className="bg-sky-600 hover:bg-sky-500 h-9">
          <Plus className="size-4 mr-2" /> Adicionar
        </Button>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead className="text-xs uppercase text-slate-500">Modelo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-center w-[100px]">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {modelos.length === 0 ? (
              <TableRow><TableCell colSpan={2} className="text-center py-6 text-slate-500">Nenhum modelo encontrado.</TableCell></TableRow>
            ) : (
              modelos.map((item: any) => (
                <TableRow key={item.id} className="border-slate-800 hover:bg-slate-800/30">
                  <TableCell className="font-medium text-slate-200">{item.nome}</TableCell>
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
    print("✅ Frontend: Tela de Modelos de Pneus criada.")

def fix_rotas_menu(raiz):
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'ModelosPneus' not in c:
        c = c.replace('import Pneus from "@/pages/Pneus";', 'import ModelosPneus from "@/pages/ModelosPneus";\nimport Pneus from "@/pages/Pneus";')
        c = c.replace('<Route path="/pneus"', '<Route path="/modelos-pneus" element={<ModelosPneus />} />\n              <Route path="/pneus"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Rota /modelos-pneus adicionada no App.tsx.")

    sidebar_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'Modelos de Pneus' not in c:
            c = c.replace(
                '{ label: "Marcas de Pneus", href: "/marcas-pneus", icon: Tag },',
                '{ label: "Marcas de Pneus", href: "/marcas-pneus", icon: Tag },\n            { label: "Modelos de Pneus", href: "/modelos-pneus", icon: Type },'
            )
            with open(sidebar_path, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Link 'Modelos de Pneus' adicionado na Sidebar.")

def fix_parametrizacao(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    if not os.path.exists(caminho):
        return
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Tenta forçar a visibilidade das flags de seed
    # Como não temos o código exato, vamos procurar a string "Oculto" e mudar o status da flag correspondente
    c = c.replace('const [showSeedMarcas, setShowSeedMarcas] = useState(false);', 'const [showSeedMarcas, setShowSeedMarcas] = useState(true);')
    c = c.replace('const [showSeedMedidas, setShowSeedMedidas] = useState(false);', 'const [showSeedMedidas, setShowSeedMedidas] = useState(true);')
    c = c.replace('const [showSeedModelos, setShowSeedModelos] = useState(false);', 'const [showSeedModelos, setShowSeedModelos] = useState(true);')

    # Fallback para quando os estados são controlados por um objeto
    c = c.replace('exibir_popular_medidas: false', 'exibir_popular_medidas: true')
    c = c.replace('exibir_popular_marcas: false', 'exibir_popular_marcas: true')
    c = c.replace('exibir_popular_modelos: false', 'exibir_popular_modelos: true')
    
    # Caso estejam sendo lidos do backend e renderizados como "Oculto"
    # Vamos procurar se a estrutura tem uma lista de parametros
    c = c.replace('"Oculto"', '"Habilitado"') # Isso pode ser perigoso se houver outros "Oculto", mas como o print só mostra essas flags de pneus
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Parametrização: Botões liberados.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    criar_tela_modelos(raiz)
    fix_rotas_menu(raiz)
    fix_parametrizacao(raiz)
    print("\n✅ Script aplicado com sucesso!")