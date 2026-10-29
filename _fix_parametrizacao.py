import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PARAMETRIZACAO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ["app", "frontend"]:
            caminho_pasta = os.path.join(raiz, pasta)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ['node_modules', '__pycache__', 'backups', 'dist', 'build', '.git']]
                for file in files:
                    c = os.path.join(root, file)
                    r = os.path.relpath(c, os.getcwd())
                    try: zipf.write(c, r)
                    except: pass
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Criar o modelo
    models_dir = os.path.join(raiz, "app", "backend", "models")
    os.makedirs(models_dir, exist_ok=True)
    caminho_model = os.path.join(models_dir, "parametrizacao.py")
    with open(caminho_model, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class ParametrizacaoBase(BaseModel):
    meta_abastecimento_ativo: bool = False
    meta_abastecimento_valor: float = 2.5

class Parametrizacao(ParametrizacaoBase):
    id: str
    updated_at: str
''')
    print("✅ Modelo criado: models/parametrizacao.py")

    # 2. Criar o router
    routers_dir = os.path.join(raiz, "app", "backend", "routers")
    os.makedirs(routers_dir, exist_ok=True)
    caminho_router = os.path.join(routers_dir, "parametrizacao.py")
    with open(caminho_router, 'w', encoding='utf-8') as f:
        f.write('''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.parametrizacao import ParametrizacaoBase, Parametrizacao

router = APIRouter(prefix="/parametrizacao", tags=["parametrizacao"])

@router.get("/meta", response_model=ParametrizacaoBase)
async def obter_meta(_u: dict = Depends(require("read"))):
    config = await db.parametrizacoes.find_one({"id": "meta_abastecimento"}, {"_id": 0})
    if not config:
        return ParametrizacaoBase(meta_abastecimento_ativo=False, meta_abastecimento_valor=2.5)
    return ParametrizacaoBase(
        meta_abastecimento_ativo=config.get("meta_abastecimento_ativo", False),
        meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5)
    )

@router.put("/meta", response_model=ParametrizacaoBase)
async def atualizar_meta(body: ParametrizacaoBase, _u: dict = Depends(require("write"))):
    await db.parametrizacoes.update_one(
        {"id": "meta_abastecimento"},
        {"$set": {
            "id": "meta_abastecimento",
            "meta_abastecimento_ativo": body.meta_abastecimento_ativo,
            "meta_abastecimento_valor": body.meta_abastecimento_valor,
            "updated_at": now_iso()
        }},
        upsert=True
    )
    return body
''')
    print("✅ Router criado: routers/parametrizacao.py")

    # 3. Registrar o router no server.py (procura por "include_router")
    server_paths = [
        os.path.join(raiz, "app", "backend", "server.py"),
        os.path.join(raiz, "app", "backend", "main.py"),
        os.path.join(raiz, "app", "backend", "app.py"),
        os.path.join(raiz, "app", "main.py"),
    ]
    server_encontrado = False
    for sp in server_paths:
        if os.path.exists(sp):
            with open(sp, 'r', encoding='utf-8') as f:
                c = f.read()
            if 'parametrizacao' not in c:
                # Encontra a linha com 'include_router' e insere antes
                # Tenta importar o router e incluir
                if 'from routers' in c:
                    c = c.replace('from routers import', 'from routers import parametrizacao,')
                    # Encontra a última inclusão de router para adicionar depois
                    matches = list(re.finditer(r'app\.include_router\([^)]+\)', c))
                    if matches:
                        ultimo = matches[-1]
                        c = c[:ultimo.end()] + '\napp.include_router(parametrizacao.router)' + c[ultimo.end():]
                with open(sp, 'w', encoding='utf-8') as f:
                    f.write(c)
                print(f"✅ Router registrado em {sp}")
                server_encontrado = True
                break
    if not server_encontrado:
        print("⚠️ Não foi possível registrar o router automaticamente. Verifique manualmente o server.py.")

def fix_frontend(raiz):
    # 1. Criar a página Parametrizacao.tsx
    pages_dir = os.path.join(raiz, "frontend", "src", "pages")
    os.makedirs(pages_dir, exist_ok=True)
    caminho_page = os.path.join(pages_dir, "Parametrizacao.tsx")
    with open(caminho_page, 'w', encoding='utf-8') as f:
        f.write('''import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Settings, Target, CheckCircle2, XCircle } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function Parametrizacao() {
  const qc = useQueryClient();
  const { data: config, isLoading } = useQuery({
    queryKey: ["parametrizacao-meta"],
    queryFn: () => apiGet<{ meta_abastecimento_ativo: boolean; meta_abastecimento_valor: number }>("/parametrizacao/meta"),
  });

  const [ativo, setAtivo] = useState(false);
  const [valor, setValor] = useState("2,5");

  useEffect(() => {
    if (config) {
      setAtivo(config.meta_abastecimento_ativo);
      setValor(String(config.meta_abastecimento_valor).replace(".", ","));
    }
  }, [config]);

  const salvar = useMutation({
    mutationFn: () => apiPut("/parametrizacao/meta", {
      meta_abastecimento_ativo: ativo,
      meta_abastecimento_valor: Number(String(valor).replace(",", ".")),
    }),
    onSuccess: () => {
      toast.success("Parametrização salva com sucesso!");
      qc.invalidateQueries({ queryKey: ["parametrizacao-meta"] });
      qc.invalidateQueries({ queryKey: ["abastecimentos"] });
    },
    onError: () => toast.error("Erro ao salvar parametrização."),
  });

  return (
    <div>
      <PageHeader eyebrow="Administração" title="Parametrização" description="Configure os parâmetros globais do sistema." />

      <div className="glass rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-sky-500/10">
            <Target className="size-5 text-sky-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">Meta de Abastecimento</h3>
            <p className="text-sm text-slate-400">Define o valor mínimo de KM/L para o termômetro de abastecimento.</p>
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Parâmetro</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Meta (KM/L)</TableHead>
              <TableHead className="text-xs uppercase text-slate-500 text-right">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">
                Parametrização de Meta de Abastecimento
              </TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setAtivo(!ativo)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    ativo
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  }`}
                >
                  {ativo ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {ativo ? "Habilitado" : "Desabilitado"}
                </button>
              </TableCell>
              <TableCell>
                <Input
                  value={valor}
                  onChange={(e) => setValor(e.target.value)}
                  disabled={!ativo}
                  placeholder="Ex: 2,5"
                  className="w-24 h-8 text-center disabled:opacity-50"
                />
              </TableCell>
              <TableCell className="text-right">
                <Button onClick={() => salvar.mutate()} disabled={salvar.isPending}>
                  {salvar.isPending ? "Salvando..." : "Salvar"}
                </Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
''')
    print("✅ Página criada: pages/Parametrizacao.tsx")

    # 2. Adicionar rota no App.tsx
    app_tsx = os.path.join(raiz, "frontend", "src", "App.tsx")
    if os.path.exists(app_tsx):
        with open(app_tsx, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'Parametrizacao' not in c:
            # Import
            c = c.replace(
                'import Base from',
                'import Parametrizacao from "@/pages/Parametrizacao";\nimport Base from'
            )
            # Route (insere antes da rota de /admin/base)
            c = c.replace(
                '<Route path="/admin/base"',
                '<Route path="/admin/parametrizacao" element={<Parametrizacao />} />\n              <Route path="/admin/base"'
            )
            with open(app_tsx, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Rota adicionada no App.tsx")

    # 3. Adicionar item no Sidebar
    sidebar_tsx = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(sidebar_tsx):
        with open(sidebar_tsx, 'r', encoding='utf-8') as f:
            c = f.read()
        if '/admin/parametrizacao' not in c:
            # Encontra o item 'Base (Limpeza)' e insere antes dele
            padrao_base = re.compile(r'(\s*\{\s*label:\s*"[^"]*Base[^"]*"[^}]*\}[,]?)')
            match = padrao_base.search(c)
            if match:
                novo_item = '{ label: "Parametrização", icon: Settings, path: "/admin/parametrizacao" },'
                c = c[:match.start()] + '\n      ' + novo_item + c[match.start():]
                # Garantir import do Settings
                if 'Settings' not in c.split('lucide-react')[0]:
                    c = c.replace('import { ', 'import { Settings, ')
                with open(sidebar_tsx, 'w', encoding='utf-8') as f:
                    f.write(c)
                print("✅ Item adicionado ao Sidebar")
            else:
                print("⚠️ Item 'Base' não encontrado no Sidebar para servir de âncora.")

    # 4. Integrar com o Termômetro no Abastecimentos.tsx
    abast_tsx = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(abast_tsx):
        with open(abast_tsx, 'r', encoding='utf-8') as f:
            c = f.read()
        
        # Busca a config da meta de abastecimento
        if 'parametrizacao-meta' not in c:
            # Adicionar useQuery para buscar a meta
            c = c.replace(
                'const { data: fornecedores = [], refetch: refetchFornecedores } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });',
                '''const { data: fornecedores = [], refetch: refetchFornecedores } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });
  const { data: metaConfig } = useQuery({
    queryKey: ["parametrizacao-meta"],
    queryFn: () => apiGet<{ meta_abastecimento_ativo: boolean; meta_abastecimento_valor: number }>("/parametrizacao/meta"),
  });
  const metaValor = metaConfig?.meta_abastecimento_ativo ? metaConfig.meta_abastecimento_valor : 2.5;'''
            )
            print("✅ Query da meta adicionada ao Abastecimentos.tsx")

        # Substituir todos os "2.5" fixos do termômetro pela meta dinâmica
        c = c.replace(
            'const valorMeta = 2.5;',  # Caso exista
            'const valorMeta = metaValor;'
        )
        # Substituir os usos do 2.5 no Termômetro (bom/ruim)
        c = c.replace(
            'r.media >= 2.5 ? \'bg-emerald-500\' : \'bg-red-500\'',
            'r.media >= metaValor ? \'bg-emerald-500\' : \'bg-red-500\''
        )
        c = c.replace(
            'r.media >= 2.5 ?',
            'r.media >= metaValor ?'
        )
        # Atualizar legendas do termômetro (se existirem como texto fixo)
        c = c.replace(
            'Bom (&ge; 2.5)',
            'Bom (&ge; {metaValor.toFixed(1)})'
        )
        c = c.replace(
            'Ruim (&lt; 2.5)',
            'Ruim (&lt; {metaValor.toFixed(1)})'
        )
        # Corrige os textos que estavam como strings literais
        c = c.replace(
            'Bom (\u2265 2.5)',
            'Bom (\u2265 {metaValor.toFixed(1)})'
        )
        c = c.replace(
            'Ruim (< 2.5)',
            'Ruim (< {metaValor.toFixed(1)})'
        )

        with open(abast_tsx, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Integração com o Termômetro realizada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Parametrização criada com sucesso!")