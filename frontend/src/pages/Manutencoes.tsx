import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Plus } from "lucide-react";
import { toast } from "sonner";
import { useSearchParams } from "react-router-dom";
import { apiGet, apiPatch, apiPost } from "@/lib/api";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { brl } from "@/lib/format";
import { cn } from "@/lib/utils";

const COLUNAS = [
  { id: "Aguardando aprovação", label: "Aguardando Aprovação", color: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/30" },
  { id: "Aguardando peça", label: "Aguardando Peça", color: "text-sky-500", bg: "bg-sky-500/10", border: "border-sky-500/30" },
  { id: "Em execução", label: "Em Execução", color: "text-blue-500", bg: "bg-blue-500/10", border: "border-blue-500/30" },
  { id: "Concluída", label: "Concluída", color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30" },
  { id: "Cancelada", label: "Cancelada", color: "text-rose-300", bg: "bg-rose-500/5", border: "border-rose-500/25" },
];

type Ordem = {
  id: string;
  descricao?: string;
  veiculo_label?: string;
  veiculo_placa?: string;
  tipo?: string;
  status?: string;
  data?: string;
  oficina?: string;
  fornecedor_nome?: string;
  custo?: number;
  valor?: number;
};

const ACOES: Record<string, { nome: string; destino: string }[]> = {
  "Aguardando aprovação": [
    { nome: "Aprovar", destino: "Em execução" },
    { nome: "Cancelar OS", destino: "Cancelada" },
  ],
  "Em execução": [
    { nome: "Aguardar peça", destino: "Aguardando peça" },
    { nome: "Concluir", destino: "Concluída" },
    { nome: "Cancelar OS", destino: "Cancelada" },
  ],
  "Aguardando peça": [
    { nome: "Retomar", destino: "Em execução" },
    { nome: "Cancelar OS", destino: "Cancelada" },
  ],
};

const campo = "w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm";
const normalizar = (valor: string) => valor.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
const veiculoDa = (os: Ordem) => os.veiculo_label || os.veiculo_placa || "Veículo sem identificação";
const numeroDa = (os: Ordem) => os.id.slice(0, 6).toUpperCase();
function dataDa(os: Ordem) {
  const partes = os.data?.match(/^(\d{4})-(\d{2})-(\d{2})/);
  return partes ? `${partes[3]}/${partes[2]}/${partes[1]}` : "—";
}

export default function Manutencoes() {
  const qc = useQueryClient();
  const consulta = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<Ordem[]>("/manutencoes") });
  const manutencoes = consulta.data ?? [];
  const [busca, setBusca] = useState("");
  const [filtro, setFiltro] = useState("");
  const [modo, setModo] = useState<"quadro" | "lista">("quadro");

  const [params, setParams] = useSearchParams();
  const novaOS = params.get("nova-os") === "1";
  const veiculos = useQuery({
    queryKey: ["veiculos"],
    queryFn: () => apiGet<{ id: string; placa: string; modelo: string; ativo?: boolean }[]>("/veiculos"),
    enabled: novaOS,
  });
  const veiculosAtivos = (veiculos.data ?? []).filter((veiculo) => veiculo.ativo !== false);

  function abrirFormulario(open: boolean) {
    criarOS.reset();
    setParams((atuais) => {
      const proximos = new URLSearchParams(atuais);
      if (open) proximos.set("nova-os", "1");
      else proximos.delete("nova-os");
      return proximos;
    }, { replace: true });
  }

  const criarOS = useMutation({
    mutationFn: (dados: { veiculo_id: string; tipo: string; data: string; descricao: string; status: string }) =>
      apiPost("/manutencoes", dados),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["manutencoes"] });
      qc.invalidateQueries({ queryKey: ["acoplamentos"] });
      abrirFormulario(false);
      toast.success("Ordem de serviço aberta.");
    },
  });

  const alterarStatus = useMutation({
    mutationFn: ({ id, novo_status }: { id: string, novo_status: string }) => {
      return apiPatch(`/manutencoes/${id}/status`, { status: novo_status });
    },
    onSuccess: () => {
      toast.success("Status atualizado com sucesso!");
      qc.invalidateQueries({ queryKey: ["manutencoes"] });
      qc.invalidateQueries({ queryKey: ["acoplamentos"] });
    },
    onError: (erro: Error) => {
      qc.invalidateQueries({ queryKey: ["manutencoes"] });
      toast.error(erro.message || "Erro ao atualizar.");
    }
  });

  const termo = normalizar(busca);
  const statusDa = (os: Ordem) => os.status?.trim() || "Sem status";
  const etapas = [
    ...COLUNAS,
    ...Array.from(new Set(manutencoes.map(statusDa)))
      .filter((status) => !COLUNAS.some((etapa) => etapa.id === status))
      .map((status) => ({ id: status, label: status, color: "text-slate-300", bg: "bg-slate-900/60", border: "border-slate-800" })),
  ];
  const filtradas = manutencoes.filter((os) => {
    const texto = [os.id, os.descricao, veiculoDa(os), os.veiculo_placa, os.tipo, os.oficina].join(" ");
    return (!filtro || statusDa(os) === filtro) && normalizar(texto).includes(termo);
  });

  function renderAcoes(os: Ordem) {
    const acoes = ACOES[os.status ?? ""] ?? [];
    if (!acoes.length) return null;
    return (
      <div className="flex flex-wrap gap-1.5">
        {acoes.map(({ nome, destino }) => (
          <Button key={nome} size="sm" variant="outline"
            className={destino === "Cancelada" ? "text-rose-300" : undefined}
            disabled={alterarStatus.isPending}
            aria-label={`${nome} · OS ${numeroDa(os)}`}
            onClick={() => {
              if (destino === "Cancelada" && !window.confirm(`Cancelar a OS ${numeroDa(os)}?`)) return;
              alterarStatus.mutate({ id: os.id, novo_status: destino });
            }}>
            {nome}
          </Button>
        ))}
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Gestão de Manutenção"
        description="Aprove ordens de serviço, acompanhe peças e libere veículos."
        actions={
          <Button className="bg-sky-600 hover:bg-sky-500 h-9" onClick={() => abrirFormulario(true)}>
            <Plus className="size-4 mr-2" /> Nova OS
          </Button>
        }
      />

      <Dialog open={novaOS} onOpenChange={(open) => {
        if (!criarOS.isPending) abrirFormulario(open);
      }}>
        <DialogContent className="max-h-[90dvh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Nova ordem de serviço</DialogTitle>
            <DialogDescription>A ordem será aberta como Aguardando aprovação.</DialogDescription>
          </DialogHeader>
          <form className="space-y-4" onSubmit={(event) => {
            event.preventDefault();
            if (criarOS.isPending) return;
            const dados = new FormData(event.currentTarget);
            const descricao = String(dados.get("descricao") ?? "").trim();
            if (!descricao) {
              toast.error("Informe a descrição do serviço.");
              return;
            }
            criarOS.mutate({
              veiculo_id: String(dados.get("veiculo_id") ?? ""),
              tipo: String(dados.get("tipo") ?? ""),
              data: String(dados.get("data") ?? ""),
              descricao,
              status: "Aguardando aprovação",
            });
          }}>
            <label className="block space-y-1">
              <span>Veículo</span>
              <select name="veiculo_id" required defaultValue="" className="w-full rounded-lg border bg-background px-2 py-2">
                <option value="" disabled>Selecione o veículo</option>
                {veiculosAtivos.map(({ id, placa, modelo }) => (
                  <option key={id} value={id}>{placa} · {modelo}</option>
                ))}
              </select>
            </label>
            {veiculos.isError && <p role="alert">Falha ao carregar veículos.</p>}
            {veiculos.isPending && <p role="status">Carregando veículos…</p>}
            {veiculos.isSuccess && veiculosAtivos.length === 0 && <p role="status">Nenhum veículo ativo disponível.</p>}
            <label className="block space-y-1">
              <span>Tipo de manutenção</span>
              <select name="tipo" required defaultValue="Corretiva" className="w-full rounded-lg border bg-background px-2 py-2">
                <option>Corretiva</option>
                <option>Preventiva</option>
              </select>
            </label>
            <label className="block space-y-1">
              <span>Data de abertura</span>
              <Input name="data" type="date" required defaultValue={new Date().toLocaleDateString("sv-SE")} />
            </label>
            <label className="block space-y-1">
              <span>Descrição do serviço</span>
              <textarea name="descricao" required rows={3} className="w-full rounded-lg border bg-background px-2 py-2" />
            </label>
            {criarOS.isError && <p role="alert" className="text-rose-400">{criarOS.error.message}</p>}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" disabled={criarOS.isPending} onClick={() => abrirFormulario(false)}>Cancelar</Button>
              <Button type="submit" disabled={criarOS.isPending || !veiculos.isSuccess || !veiculosAtivos.length}>
                {criarOS.isPending ? "Salvando…" : "Abrir OS"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <section aria-label="Ordens de serviço" className="space-y-4">
        <div className="grid gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-3 sm:grid-cols-[1fr_minmax(12rem,auto)_auto] sm:items-end">
          <label className="block space-y-1">
            <span className="text-xs text-slate-400">Buscar OS</span>
            <Input placeholder="Código, placa, veículo ou descrição" value={busca} onChange={(event) => setBusca(event.target.value)} />
          </label>
          <label className="block space-y-1">
            <span className="text-xs text-slate-400">Status</span>
            <select className={campo} value={filtro} onChange={(event) => setFiltro(event.target.value)}>
              <option value="">Todos os status</option>
              {etapas.map(({ id, label }) => <option key={id} value={id}>{label}</option>)}
            </select>
          </label>
          <div className="flex gap-1" role="group" aria-label="Visualização">
            <Button variant={modo === "quadro" ? "secondary" : "ghost"} aria-pressed={modo === "quadro"} onClick={() => setModo("quadro")}>Quadro</Button>
            <Button variant={modo === "lista" ? "secondary" : "ghost"} aria-pressed={modo === "lista"} onClick={() => setModo("lista")}>Lista</Button>
          </div>
        </div>

        {consulta.isPending ? <p role="status">Carregando ordens de serviço…</p> : consulta.isError ? (
          <div role="alert" className="flex flex-wrap items-center gap-3 text-rose-300">
            Falha ao carregar ordens de serviço.
            <Button variant="outline" onClick={() => consulta.refetch()}>Tentar novamente</Button>
          </div>
        ) : filtradas.length === 0 ? (
          <p className="rounded-xl border border-dashed border-slate-700 p-6 text-center text-sm text-slate-400">Nenhuma ordem encontrada.</p>
        ) : modo === "lista" ? (
          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/60">
            <table className="w-full min-w-[54rem] text-left text-sm">
              <thead className="bg-slate-900 text-xs text-slate-400">
                <tr>{["OS / Serviço", "Veículo", "Abertura", "Status", "Custo", "Ações"].map((titulo) => <th key={titulo} scope="col" className="px-4 py-3">{titulo}</th>)}</tr>
              </thead>
              <tbody>
                {filtradas.map((os) => (
                  <tr key={os.id} className="border-t border-slate-800">
                    <th scope="row" className="max-w-72 break-words px-4 py-3 font-medium">
                      <span className="block font-mono text-xs text-slate-400">{numeroDa(os)}</span>
                      {os.descricao || "Manutenção"}
                    </th>
                    <td className="px-4 py-3">{veiculoDa(os)}</td>
                    <td className="whitespace-nowrap px-4 py-3">{dataDa(os)}</td>
                    <td className="px-4 py-3">{statusDa(os)}</td>
                    <td className="whitespace-nowrap px-4 py-3">{brl(os.custo ?? os.valor ?? 0)}</td>
                    <td className="px-4 py-3">{renderAcoes(os)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="grid items-start gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            {etapas.filter((etapa) => !filtro || etapa.id === filtro).map((etapa) => {
              const ordens = filtradas.filter((os) => statusDa(os) === etapa.id);
              return (
                <section key={etapa.id} className={cn("min-w-0 space-y-3 rounded-xl border p-3", etapa.border, etapa.bg)}>
                  <h2 className={cn("flex justify-between gap-2 text-sm font-semibold", etapa.color)}>
                    {etapa.label} <span className="font-mono text-slate-400">{ordens.length}</span>
                  </h2>
                  {ordens.length === 0 && <p className="py-3 text-sm text-slate-400">Nenhuma OS nesta etapa.</p>}
                  {ordens.map((os) => (
                    <article key={os.id} className="space-y-2 rounded-lg border border-slate-800 bg-slate-900 p-3">
                      <div className="flex justify-between gap-2 text-xs text-slate-400">
                        <span className="font-mono">{numeroDa(os)}</span><time>{dataDa(os)}</time>
                      </div>
                      <h3 className="break-words text-sm font-semibold">{os.descricao || "Manutenção"}</h3>
                      <p className="break-words text-sm text-slate-300">{veiculoDa(os)}</p>
                      {(os.tipo || os.oficina || os.fornecedor_nome) && (
                        <p className="break-words text-xs text-slate-400">{[os.tipo, os.oficina || os.fornecedor_nome].filter(Boolean).join(" · ")}</p>
                      )}
                      <div className="space-y-2 border-t border-slate-800 pt-2">
                        <p className="font-mono text-sm">{brl(os.custo ?? os.valor ?? 0)}</p>
                        {renderAcoes(os)}
                      </div>
                    </article>
                  ))}
                </section>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
