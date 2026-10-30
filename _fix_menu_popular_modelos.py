import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MENU_POPULAR_MODELOS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/pages/ModelosPneus.tsx",
        "frontend/src/App.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_sidebar(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    
    # Lendo o arquivo atual para pegar a estrutura original
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que o ícone Type está importado do lucide-react
    if 'Type' not in c.split('from "lucide-react"')[0]:
        c = c.replace('import {', 'import { Type,', 1)

    # 2. Inserir o link "Modelos de Pneus" se não existir
    if 'Modelos de Pneus' not in c:
        # Procura a linha exata de "Marcas de Pneus" para colar embaixo
        import re
        padrao = re.compile(r'(\{[^{}]*label:\s*["\']Marcas de Pneus["\'][^{}]*\})')
        match = padrao.search(c)
        
        if match:
            novo_item = '\n      { label: "Modelos de Pneus", icon: Type, path: "/cadastros/pneu-modelos" },'
            c = c[:match.end()] + novo_item + c[match.end():]
            print("✅ Sidebar: Link de Modelos inserido após Marcas.")
        else:
            print("⚠️ Sidebar: Não achei 'Marcas de Pneus'. Verifique manualmente.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_tela_modelos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "ModelosPneus.tsx")
    
    codigo = '''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Tag, RefreshCw } from "lucide-react";
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

  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });
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

  const popular = useMutation({
    mutationFn: () => apiPost("/pneus/seed", {}),
    onSuccess: () => {
      toast.success("Modelos populados com sucesso!");
      qc.invalidateQueries({ queryKey: ["modelos-pneus"] });
    }
  });

  return (
    <div>
      <PageHeader 
        eyebrow="Cadastros" 
        title="Modelos de Pneus" 
        description="Gerencie os modelos de pneus disponíveis no sistema." 
        actions={
          config?.mostrar_seed_modelos && (
            <Button onClick={() => popular.mutate()} disabled={popular.isPending} variant="outline" className="border-sky-500/40 text-sky-400 hover:bg-sky-500/10 h-9">
              <RefreshCw className={`size-4 mr-2 ${popular.isPending ? 'animate-spin' : ''}`} /> 
              Popular Modelos
            </Button>
          )
        }
      />

      <div className="glass p-4 rounded-xl mb-4 flex items-end gap-3">
        <div className="grid gap-1.5 flex-1 max-w-sm">
          <Label className="text-xs text-slate-400">Novo Modelo</Label>
          <Input value={novoModelo} onChange={(e) => setNovoModelo(e.target.value)} placeholder="Ex: X Multi Z" onKeyDown={(e) => e.key === 'Enter' && novoModelo && criar.mutate()} />
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
    print("✅ Frontend: Tela de Modelos atualizada com o botão 'Popular Modelos'.")

def garantir_rota_app(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'ModelosPneus' not in c:
        c = c.replace('import Pneus from', 'import ModelosPneus from "@/pages/ModelosPneus";\nimport Pneus from')
        c = c.replace('<Route path="/pneus"', '<Route path="/cadastros/pneu-modelos" element={<ModelosPneus />} />\n              <Route path="/pneus"')
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ App.tsx: Rota /cadastros/pneu-modelos garantida.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_sidebar(raiz)
    fix_tela_modelos(raiz)
    garantir_rota_app(raiz)
    print("\n✅ Script aplicado com sucesso!")
    