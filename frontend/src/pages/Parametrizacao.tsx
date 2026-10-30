import { useState, useEffect } from "react";
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
  const [seedMod, setSeedMod] = useState(false);
  const [seedTemp, setSeedTemp] = useState(false);

  useEffect(() => {
    if (config) {
      setAtivo(config.meta_abastecimento_ativo);
      setValor(String(config.meta_abastecimento_valor).replace(".", ","));
      setSeedForn(config.mostrar_seed_fornecedores || false);
      setSeedMed(config.mostrar_seed_medidas || false);
      setSeedMarc(config.mostrar_seed_marcas || false);
      setSeedMod(config.mostrar_seed_modelos || false);
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
      mostrar_seed_modelos: seedMod,
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
          
            <TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">Exibir botão "Popular Modelos" (Modelos de Pneus)</TableCell>
              <TableCell>
                <BotaoStatus ativo={seedMod} onClick={() => setSeedMod(!seedMod)} textoAtivo="Visível" textoInativo="Oculto" />
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
