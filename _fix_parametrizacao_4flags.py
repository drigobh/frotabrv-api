import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PARAM_4FLAGS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = [
        "app/backend/models/parametrizacao.py",
        "app/backend/routers/parametrizacao.py",
        "frontend/src/pages/Parametrizacao.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Model
    model_path = os.path.join(raiz, "app", "backend", "models", "parametrizacao.py")
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write('''from pydantic import BaseModel
from typing import Optional

class ParametrizacaoBase(BaseModel):
    meta_abastecimento_ativo: bool = False
    meta_abastecimento_valor: float = 2.5
    mostrar_seed_fornecedores: bool = False
    mostrar_seed_medidas: bool = False
    mostrar_seed_marcas: bool = False
    mostrar_seed_templates: bool = False

class Parametrizacao(ParametrizacaoBase):
    id: str
    updated_at: str
''')
    print("✅ Model Parametrização: 4 flags garantidas.")

    # 2. Router
    router_path = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    with open(router_path, 'w', encoding='utf-8') as f:
        f.write('''from fastapi import APIRouter, Depends, HTTPException
from lib.db import db
from lib.security import require
from lib.dates import now_iso
from models.parametrizacao import ParametrizacaoBase

router = APIRouter(prefix="/parametrizacao", tags=["parametrizacao"])

@router.get("/meta", response_model=ParametrizacaoBase)
async def obter_meta(_u: dict = Depends(require("read"))):
    config = await db.parametrizacoes.find_one({"id": "meta_abastecimento"}, {"_id": 0})
    if not config:
        return ParametrizacaoBase()
    return ParametrizacaoBase(
        meta_abastecimento_ativo=config.get("meta_abastecimento_ativo", False),
        meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5),
        mostrar_seed_fornecedores=config.get("mostrar_seed_fornecedores", False),
        mostrar_seed_medidas=config.get("mostrar_seed_medidas", False),
        mostrar_seed_marcas=config.get("mostrar_seed_marcas", False),
        mostrar_seed_templates=config.get("mostrar_seed_templates", False)
    )

@router.put("/meta", response_model=ParametrizacaoBase)
async def atualizar_meta(body: ParametrizacaoBase, _u: dict = Depends(require("write"))):
    await db.parametrizacoes.update_one(
        {"id": "meta_abastecimento"},
        {"$set": {
            "id": "meta_abastecimento",
            "meta_abastecimento_ativo": body.meta_abastecimento_ativo,
            "meta_abastecimento_valor": body.meta_abastecimento_valor,
            "mostrar_seed_fornecedores": body.mostrar_seed_fornecedores,
            "mostrar_seed_medidas": body.mostrar_seed_medidas,
            "mostrar_seed_marcas": body.mostrar_seed_marcas,
            "mostrar_seed_templates": body.mostrar_seed_templates,
            "updated_at": now_iso()
        }},
        upsert=True
    )
    return body
''')
    print("✅ Router Parametrização: 4 flags garantidas.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    codigo = '''import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Target, CheckCircle2, XCircle } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function Parametrizacao() {
  const qc = useQueryClient();
  const { data: config, isLoading } = useQuery({
    queryKey: ["parametrizacao-meta"],
    queryFn: () => apiGet<any>("/parametrizacao/meta"),
  });

  const [ativo, setAtivo] = useState(false);
  const [valor, setValor] = useState("2,5");
  const [seedForn, setSeedForn] = useState(false);
  const [seedMed, setSeedMed] = useState(false);
  const [seedMarc, setSeedMarc] = useState(false);
  const [seedTemp, setSeedTemp] = useState(false);

  useEffect(() => {
    if (config) {
      setAtivo(config.meta_abastecimento_ativo);
      setValor(String(config.meta_abastecimento_valor).replace(".", ","));
      setSeedForn(config.mostrar_seed_fornecedores || false);
      setSeedMed(config.mostrar_seed_medidas || false);
      setSeedMarc(config.mostrar_seed_marcas || false);
      setSeedTemp(config.mostrar_seed_templates || false);
    }
  }, [config]);

  const salvar = useMutation({
    mutationFn: () => apiPut("/parametrizacao/meta", {
      meta_abastecimento_ativo: ativo,
      meta_abastecimento_valor: Number(String(valor).replace(",", ".")),
      mostrar_seed_fornecedores: seedForn,
      mostrar_seed_medidas: seedMed,
      mostrar_seed_marcas: seedMarc,
      mostrar_seed_templates: seedTemp,
    }),
    onSuccess: () => {
      toast.success("Parametrização salva com sucesso!");
      qc.invalidateQueries({ queryKey: ["parametrizacao-meta"] });
    },
    onError: () => toast.error("Erro ao salvar parametrização."),
  });

  const BotaoStatus = ({ ativo, onClick, textoAtivo, textoInativo }: any) => (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
        ativo ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
      }`}
    >
      {ativo ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
      {ativo ? textoAtivo : textoInativo}
    </button>
  );

  return (
    <div>
      <PageHeader eyebrow="Administração" title="Parametrização" description="Configure os parâmetros globais do sistema." />

      <div className="glass rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-sky-500/10">
            <Target className="size-5 text-sky-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">Configurações Globais</h3>
            <p className="text-sm text-slate-400">Metas e visibilidade de botões de setup.</p>
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Parâmetro</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Ação</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Parametrização de Meta de Abastecimento</TableCell>
              <TableCell>
                <BotaoStatus ativo={ativo} onClick={() => setAtivo(!ativo)} textoAtivo="Habilitado" textoInativo="Desabilitado" />
              </TableCell>
              <TableCell>
                <Input value={valor} onChange={(e) => setValor(e.target.value)} disabled={!ativo} placeholder="Ex: 2,5" className="w-24 h-8 text-center disabled:opacity-50" />
              </TableCell>
            </TableRow>

            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Lista Base" (Tipos de Fornecedores)</TableCell>
              <TableCell>
                <BotaoStatus ativo={seedForn} onClick={() => setSeedForn(!seedForn)} textoAtivo="Visível" textoInativo="Oculto" />
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Setup inicial.</TableCell>
            </TableRow>

            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Medidas" (Medidas de Pneus)</TableCell>
              <TableCell>
                <BotaoStatus ativo={seedMed} onClick={() => setSeedMed(!seedMed)} textoAtivo="Visível" textoInativo="Oculto" />
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Setup inicial.</TableCell>
            </TableRow>

            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Marcas" (Marcas de Pneus)</TableCell>
              <TableCell>
                <BotaoStatus ativo={seedMarc} onClick={() => setSeedMarc(!seedMarc)} textoAtivo="Visível" textoInativo="Oculto" />
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Setup inicial.</TableCell>
            </TableRow>

            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Templates" (Templates de Chassi)</TableCell>
              <TableCell>
                <BotaoStatus ativo={seedTemp} onClick={() => setSeedTemp(!seedTemp)} textoAtivo="Visível" textoInativo="Oculto" />
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Setup inicial.</TableCell>
            </TableRow>
          </TableBody>
        </Table>

        <div className="flex justify-end mt-6">
          <Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="bg-sky-600 hover:bg-sky-500">
            {salvar.isPending ? "Salvando..." : "Salvar Parametrizações"}
          </Button>
        </div>
      </div>
    </div>
  );
}
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo)
    print("✅ Parametrizacao.tsx reescrita com as 4 flags independentes.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")