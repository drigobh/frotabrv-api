import os
import subprocess
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MODELOS_SEGURO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/App.tsx",
        "frontend/src/pages/ModelosPneus.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def restaurar_arquivos(raiz):
    print("\n🔄 Restaurando Sidebar.tsx e App.tsx para o commit estável a789856...")
    res = subprocess.run(
        ["git", "checkout", "a789856", "--", "frontend/src/components/layout/Sidebar.tsx", "frontend/src/App.tsx"],
        cwd=raiz, capture_output=True, text=True
    )
    if res.returncode == 0:
        print("✅ Arquivos restaurados com sucesso para o estado do marco.")
    else:
        print(f"❌ Erro ao restaurar: {res.stderr}")

def injetar_sidebar(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'Modelos de Pneus' in c:
        print("ℹ️ Sidebar: opção já existe.")
        return

    # Usa a mesma Tag de ícone (que já está importada) para não quebrar nada
    novo_item = '\n      { label: "Modelos de Pneus", icon: Tag, path: "/cadastros/pneu-modelos" },'
    
    # Insere logo após a linha de Marcas de Pneus
    if '{ label: "Marcas de Pneus", icon: Tag, path: "/cadastros/pneu-marcas" },' in c:
        c = c.replace('{ label: "Marcas de Pneus", icon: Tag, path: "/cadastros/pneu-marcas" },', '{ label: "Marcas de Pneus", icon: Tag, path: "/cadastros/pneu-marcas" },' + novo_item)
        print("✅ Sidebar: item 'Modelos de Pneus' inserido após Marcas.")
    else:
        print("⚠️ Sidebar: âncora de Marcas não encontrada. Inserindo após Medidas.")
        c = c.replace('{ label: "Medidas de Pneus", icon: Disc, path: "/cadastros/pneu-medidas" },', '{ label: "Medidas de Pneus", icon: Disc, path: "/cadastros/pneu-medidas" },' + novo_item)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def injetar_app(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "App.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'ModelosPneus' in c:
        print("ℹ️ App.tsx: rota já existe.")
        return

    # Adiciona import
    if 'import Pneus from' in c:
        c = c.replace('import Pneus from', 'import ModelosPneus from "@/pages/ModelosPneus";\nimport Pneus from')

    # Adiciona rota
    if '<Route path="/operacao/pneus"' in c:
        c = c.replace('<Route path="/operacao/pneus"', '<Route path="/cadastros/pneu-modelos" element={<ModelosPneus />} />\n              <Route path="/operacao/pneus"')
        print("✅ App.tsx: rota /cadastros/pneu-modelos inserida.")
    else:
        print("⚠️ App.tsx: âncora de Pneus não encontrada, verifique manualmente.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

def criar_tela_modelos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "ModelosPneus.tsx")
    if os.path.exists(caminho):
        print("ℹ️ Tela ModelosPneus.tsx já existe.")
        return
    
    codigo = '''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Tag } from "lucide-react";
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
    print("✅ Tela ModelosPneus.tsx criada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    restaurar_arquivos(raiz)
    criar_tela_modelos(raiz)
    injetar_sidebar(raiz)
    injetar_app(raiz)
    print("\n✅ Script aplicado com sucesso! O Vite deve recarregar sem erros.")