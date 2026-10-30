import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MODELOS_ESTAVEL_{agora}.zip")
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
    path = os.path.join(raiz, "app", "backend", "routers", "pneus.py")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    if '@router.post("/modelos")' not in c:
        rotas = '''
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
        # Insere antes do PUT /{id}
        c = c.replace('@router.put("/{id}", response_model=Pneu)', rotas + '@router.put("/{id}", response_model=Pneu)')
        
        # Adiciona a carga inicial de modelos no seed existente
        if 'modelos = ["X Multi Z"' not in c:
            c = c.replace(
                'medidas = ["295/80 R22.5", "275/80 R22.5", "11R22.5", "12R22.5"]',
                'medidas = ["295/80 R22.5", "275/80 R22.5", "11R22.5", "12R22.5"]\n    modelos = ["X Multi Z", "X Line Energy", "R268", "M840", "G580"]\n    for m in modelos:\n        if not await db.modelos_pneus.find_one({"nome": m}):\n            await db.modelos_pneus.insert_one({"id": str(uuid.uuid4()), "nome": m})'
            )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: CRUD de Modelos e Seed adicionados.")

def criar_tela_modelos(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "ModelosPneus.tsx")
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
      <PageHeader eyebrow="Cadastros" title="Modelos de Pneus" description="Gerencie os modelos de pneus disponíveis no sistema." />

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
    with open(path, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Frontend: Tela de Modelos de Pneus criada.")

def fix_rotas_menu(raiz):
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(app_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'ModelosPneus' not in c:
        c = c.replace('import Pneus from "@/pages/Pneus";', 'import ModelosPneus from "@/pages/ModelosPneus";\nimport Pneus from "@/pages/Pneus";')
        c = c.replace('<Route path="/pneus"', '<Route path="/cadastros/pneu-modelos" element={<ModelosPneus />} />\n              <Route path="/pneus"')
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ App.tsx: Rota /cadastros/pneu-modelos adicionada.")

    sidebar_path = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(sidebar_path):
        with open(sidebar_path, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'Modelos de Pneus' not in c:
            c = c.replace(
                '{ label: "Marcas de Pneus", icon: Tag, path: "/cadastros/pneu-marcas" },',
                '{ label: "Marcas de Pneus", icon: Tag, path: "/cadastros/pneu-marcas" },\n      { label: "Modelos de Pneus", icon: Type, path: "/cadastros/pneu-modelos" },'
            )
            # Garante que o ícone Type está importado
            if ', Type' not in c.split('from "lucide-react"')[0] and 'Type,' not in c.split('from "lucide-react"')[0]:
                c = c.replace('import {', 'import { Type,', 1)
            
            with open(sidebar_path, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Sidebar.tsx: Link e Ícone de Modelos adicionados.")

def fix_parametrizacao(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adicionar estado
    if 'seedMod' not in c:
        c = c.replace('const [seedMarc, setSeedMarc] = useState(false);', 'const [seedMarc, setSeedMarc] = useState(false);\n  const [seedMod, setSeedMod] = useState(false);')
        
        # Adicionar no useEffect
        c = c.replace('setSeedMarc(config.mostrar_seed_marcas || false);', 'setSeedMarc(config.mostrar_seed_marcas || false);\n      setSeedMod(config.mostrar_seed_modelos || false);')
        
        # Adicionar no Salvar
        c = c.replace('mostrar_seed_marcas: seedMarc,', 'mostrar_seed_marcas: seedMarc,\n      mostrar_seed_modelos: seedMod,')
        
        # Adicionar na Tabela
        tabela_mod = '''
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Modelos" (Modelos de Pneus)</TableCell>
              <TableCell>
                <BotaoStatus ativo={seedMod} onClick={() => setSeedMod(!seedMod)} textoAtivo="Visível" textoInativo="Oculto" />
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Setup inicial.</TableCell>
            </TableRow>
'''
        c = c.replace('</TableBody>', tabela_mod + '          </TableBody>')

        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Parametrização: Botão de Modelos adicionado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    criar_tela_modelos(raiz)
    fix_rotas_menu(raiz)
    fix_parametrizacao(raiz)
    print("\n✅ Script aplicado com sucesso! O Vite deve atualizar na hora.")