import { useState, useEffect } from "react";
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
    queryFn: () => apiGet<any>("/parametrizacao/meta"),
  });

  const [ativo, setAtivo] = useState(false);
  const [valor, setValor] = useState("2,5");
  const [mostrarSeedFornecedores, setMostrarSeedFornecedores] = useState(false);
  const [mostrarSeedMedidas, setMostrarSeedMedidas] = useState(false);
  const [mostrarSeedMarcas, setMostrarSeedMarcas] = useState(false);

  useEffect(() => {
    if (config) {
      setAtivo(config.meta_abastecimento_ativo);
      setValor(String(config.meta_abastecimento_valor).replace(".", ","));
      setMostrarSeedFornecedores(config.mostrar_seed_fornecedores || false);
      setMostrarSeedMedidas(config.mostrar_seed_medidas || false);
      setMostrarSeedMarcas(config.mostrar_seed_marcas || false);
    }
  }, [config]);

  const salvar = useMutation({
    mutationFn: () => apiPut("/parametrizacao/meta", {
      meta_abastecimento_ativo: ativo,
      meta_abastecimento_valor: Number(String(valor).replace(",", ".")),
      mostrar_seed_fornecedores: mostrarSeedFornecedores,
      mostrar_seed_medidas: mostrarSeedMedidas,
      mostrar_seed_marcas: mostrarSeedMarcas,
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
            {/* Meta de Abastecimento */}
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Parametrização de Meta de Abastecimento</TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setAtivo(!ativo)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    ativo ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
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
            </TableRow>

            {/* Botão Popular Lista Base (Fornecedores) */}
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Lista Base" na tela de Tipos de Fornecedores</TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeedFornecedores(!mostrarSeedFornecedores)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeedFornecedores ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {mostrarSeedFornecedores ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeedFornecedores ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
            </TableRow>

            {/* Botão Popular Medidas */}
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Medidas" na tela de Medidas de Pneus</TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeedMedidas(!mostrarSeedMedidas)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeedMedidas ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {mostrarSeedMedidas ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeedMedidas ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
            </TableRow>

            {/* Botão Popular Marcas */}
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Marcas" na tela de Marcas de Pneus</TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeedMarcas(!mostrarSeedMarcas)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeedMarcas ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                  }`}
                >
                  {mostrarSeedMarcas ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeedMarcas ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
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
