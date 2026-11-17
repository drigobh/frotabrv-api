import { useEffect, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Plus, Search, Wrench } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api";
import { brl } from "@/lib/format";
import { cn } from "@/lib/utils";

const ETAPAS = [
  "Todas", "Aguardando aprovação", "Aguardando peça", "Em execução", "Concluída", "Cancelada", "Outras",
] as const;
type Etapa = typeof ETAPAS[number];

const PROXIMAS: Partial<Record<Etapa, Etapa[]>> = {
  "Aguardando aprovação": ["Em execução", "Cancelada"],
  "Aguardando peça": ["Em execução", "Cancelada"],
  "Em execução": ["Aguardando peça", "Concluída", "Cancelada"],
  Outras: ["Aguardando aprovação"],
};

const CORES: Partial<Record<Etapa, string>> = {
  "Aguardando aprovação": "bg-amber-500/10 text-amber-300",
  "Aguardando peça": "bg-violet-500/10 text-violet-300",
  "Em execução": "bg-sky-500/10 text-sky-300",
  "Concluída": "bg-emerald-500/10 text-emerald-300",
  "Cancelada": "bg-rose-500/10 text-rose-300",
};

type Ordem = {
  id: string;
  etapa: Etapa;
  status?: string;
  versao_dados?: string;
  veiculo_id?: string;
  veiculo_label?: string;
  veiculo_placa?: string;
  tipo?: string;
  data?: string;
  descricao?: string;
  custo?: number;
  valor?: number;
  fornecedor_id?: string;
  fornecedor_nome?: string;
  oficina?: string;
  pecas_utilizadas?: unknown[];
};
type VeiculoIndicador = { veiculo: string; valor: number; quantidade: number };
type Indicadores = {
  valor: number;
  duracao: { dias: number; os_id?: string; veiculo?: string } | null;
  maior_valor: VeiculoIndicador | null;
  maior_quantidade: VeiculoIndicador | null;
};
type Painel = {
  itens: Ordem[];
  contagens: Record<Etapa, number>;
  total: number;
  por_pagina: number;
  indicadores?: Indicadores;
};

function CardsManutencao({ painel, etapa }: { painel?: Painel; etapa: Etapa }) {
  const dados = painel?.indicadores;
  const duracao = dados?.duracao;
  const total = painel?.total;
  const cards = [
    { titulo: "Valor das manutenções", valor: dados ? brl(dados.valor) : "—", detalhe: "" },
    { titulo: "Quantidade de manutenções", valor: total === undefined ? "—" : total.toLocaleString("pt-BR"), detalhe: "" },
    {
      titulo: "Maior tempo de manutenção",
      valor: duracao ? duracao.dias + (duracao.dias === 1 ? " dia" : " dias") : "—",
      detalhe: duracao
        ? [duracao.veiculo, duracao.os_id && "OS " + duracao.os_id.slice(0, 8).toUpperCase()].filter(Boolean).join(" · ")
        : dados && total ? "Sem datas suficientes" : "",
    },
    {
      titulo: "Veículo com maior valor",
      valor: dados?.maior_valor ? brl(dados.maior_valor.valor) : "—",
      detalhe: dados?.maior_valor?.veiculo ?? "",
    },
    {
      titulo: "Veículo com mais manutenções",
      valor: dados?.maior_quantidade ? String(dados.maior_quantidade.quantidade) : "—",
      detalhe: dados?.maior_quantidade?.veiculo ?? "",
    },
  ];

  return (
    <section aria-label={"Indicadores de manutenção · " + etapa} className="mb-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5">
      {cards.map(({ titulo, valor, detalhe }) => (
        <div key={titulo} className="min-w-0 rounded-xl border border-slate-800 bg-slate-900/70 px-4 py-4">
          <h2 className="text-sm font-medium text-slate-300">{titulo}</h2>
          <p className="mt-2 break-words text-xl font-semibold tabular-nums text-slate-100">{valor}</p>
          {detalhe && <p className="mt-1 break-words text-xs text-slate-400">{detalhe}</p>}
        </div>
      ))}
    </section>
  );
}
type Veiculo = { id: string; placa: string; modelo: string; ativo?: boolean };
type Fornecedor = { id: string; nome: string };

const campo = "w-full rounded-lg border border-input bg-background px-3 py-2 text-sm";
const codigo = (os: Ordem) => os.id.slice(0, 8).toUpperCase();
const veiculoDa = (os: Ordem) => os.veiculo_label || os.veiculo_placa || "Veículo sem identificação";
const statusDa = (os: Ordem) => os.etapa === "Outras" ? os.status || "Sem status" : os.etapa;
const dataISO = (data?: string) => data?.match(/^\d{4}-\d{2}-\d{2}/)?.[0] || "";
const dataBR = (data?: string) => dataISO(data).split("-").reverse().join("/") || "—";
const hoje = () => new Date().toLocaleDateString("sv-SE");

function FormularioOS({ os, fechar, atualizar }: { os?: Ordem; fechar: () => void; atualizar: () => void }) {
  const veiculos = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<Veiculo[]>("/veiculos") });
  const fornecedores = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<Fornecedor[]>("/fornecedores") });
  const opcoesVeiculos = (veiculos.data ?? []).filter((v) => v.ativo !== false || v.id === os?.veiculo_id);
  const opcoesFornecedores = fornecedores.data ?? [];
  const [status, setStatus] = useState("");
  const salvar = useMutation({
    mutationFn: (form: FormData) => {
      const descricao = String(form.get("descricao") ?? "").trim();
      if (!descricao) throw new Error("Descreva o serviço.");
      const valor = String(form.get("custo") ?? "").trim().replace(",", ".");
      if (valor && (!/^\d+(?:\.\d{1,2})?$/.test(valor) || !Number.isFinite(Number(valor)))) {
        throw new Error("Informe um valor em reais, como 1250,50.");
      }
      const dados = {
        veiculo_id: String(form.get("veiculo") ?? ""),
        tipo: String(form.get("tipo") ?? ""),
        data: String(form.get("data") ?? ""),
        descricao,
        custo: valor ? Number(valor) : 0,
        fornecedor_id: String(form.get("fornecedor") ?? "") || null,
        oficina: String(form.get("oficina") ?? "").trim() || null,
      };
      if (!os) return apiPost("/manutencoes", { ...dados, status: "Aguardando aprovação" });
      const transicao = status ? { status, status_original: os.status ?? null } : {};
      return apiPatch("/manutencoes/" + os.id + "/dados", { ...dados, ...transicao, versao: os.versao_dados ?? null });
    },
    onSuccess: () => {
      atualizar();
      fechar();
      toast.success(os ? "Ordem atualizada." : "Ordem aberta.");
    },
    onError: atualizar,
  });

  function enviar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!salvar.isPending) salvar.mutate(new FormData(event.currentTarget));
  }

  return (
    <Dialog open onOpenChange={(aberto) => { if (!aberto && !salvar.isPending) fechar(); }}>
      <DialogContent className="flex max-h-[90dvh] flex-col overflow-hidden sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>{os ? "Editar OS " + codigo(os) : "Nova ordem de serviço"}</DialogTitle>
          <DialogDescription>{os ? veiculoDa(os) : "A nova OS entra em Aguardando aprovação."}</DialogDescription>
        </DialogHeader>
        <form onSubmit={enviar} className="flex min-h-0 flex-col gap-4">
          <div className="grid min-h-0 gap-3 overflow-y-auto px-0.5 pb-1 sm:grid-cols-2">
            <label className="space-y-1 text-sm sm:col-span-2">
              <span>Veículo</span>
              <select name="veiculo" className={campo} required defaultValue={os?.veiculo_id ?? ""}>
                <option value="" disabled>{veiculos.isPending ? "Carregando veículos…" : "Selecione um veículo"}</option>
                {os?.veiculo_id && !opcoesVeiculos.some((v) => v.id === os.veiculo_id) && <option value={os.veiculo_id}>{veiculoDa(os)}</option>}
                {opcoesVeiculos.map((v) => <option key={v.id} value={v.id}>{v.placa} · {v.modelo}</option>)}
              </select>
            </label>
            <label className="space-y-1 text-sm">
              <span>Tipo de manutenção</span>
              <select name="tipo" className={campo} defaultValue={os?.tipo || "Corretiva"} required>
                {os?.tipo && !["Corretiva", "Preventiva"].includes(os.tipo) && <option>{os.tipo}</option>}
                <option>Corretiva</option><option>Preventiva</option>
              </select>
            </label>
            <label className="space-y-1 text-sm">
              <span>Data de abertura</span>
              <Input name="data" type="date" required defaultValue={dataISO(os?.data) || (os ? "" : hoje())} />
            </label>
            <label className="space-y-1 text-sm sm:col-span-2">
              <span>Descrição do serviço</span>
              <textarea name="descricao" className={campo} rows={3} required maxLength={4000} defaultValue={os?.descricao} />
            </label>
            <label className="space-y-1 text-sm">
              <span>Fornecedor</span>
              <select name="fornecedor" className={campo} defaultValue={os?.fornecedor_id || ""}>
                <option value="">{fornecedores.isPending ? "Carregando fornecedores…" : "Sem fornecedor"}</option>
                {os?.fornecedor_id && !opcoesFornecedores.some((f) => f.id === os.fornecedor_id) && (
                  <option value={os.fornecedor_id}>{os.fornecedor_nome || "Fornecedor vinculado"}</option>
                )}
                {opcoesFornecedores.map((f) => <option key={f.id} value={f.id}>{f.nome}</option>)}
              </select>
            </label>
            <label className="space-y-1 text-sm">
              <span>Oficina</span>
              <Input name="oficina" maxLength={200} defaultValue={os?.oficina ?? ""} />
            </label>
            <label className="space-y-1 text-sm">
              <span>Valor (R$)</span>
              <Input name="custo" inputMode="decimal" placeholder="0,00" defaultValue={os ? String(os.custo ?? os.valor ?? 0).replace(".", ",") : ""} />
            </label>
            {os && (
              <label className="space-y-1 text-sm">
                <span>Status</span>
                <select aria-label="Status" className={campo} value={status} onChange={(event) => setStatus(event.target.value)}>
                  <option value="">{statusDa(os)} (atual)</option>
                  {(PROXIMAS[os.etapa] ?? []).map((etapa) => <option key={etapa}>{etapa}</option>)}
                </select>
              </label>
            )}
            {veiculos.isError && <p role="alert" className="text-sm text-rose-300">Falha ao carregar veículos. <button type="button" className="underline" onClick={() => veiculos.refetch()}>Recarregar</button></p>}
            {fornecedores.isError && <p role="alert" className="text-sm text-rose-300">Falha ao carregar fornecedores. <button type="button" className="underline" onClick={() => fornecedores.refetch()}>Recarregar</button></p>}
          </div>
          {salvar.isError && <p role="alert" className="text-sm text-rose-300">{salvar.error.message}</p>}
          <div className="flex justify-end gap-2 border-t border-border pt-4">
            <Button type="button" variant="outline" disabled={salvar.isPending} onClick={fechar}>Fechar</Button>
            <Button type="submit" disabled={salvar.isPending}>{salvar.isPending ? "Salvando…" : "Salvar OS"}</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function Manutencoes() {
  const qc = useQueryClient();
  const [params, setParams] = useSearchParams();
  const [etapa, setEtapa] = useState<Etapa>("Todas");
  const [entrada, setEntrada] = useState("");
  const [busca, setBusca] = useState("");
  const [pagina, setPagina] = useState(1);
  const [edicao, setEdicao] = useState<Ordem>();
  const [exclusao, setExclusao] = useState<Ordem>();
  const nova = params.get("nova-os") === "1";

  useEffect(() => {
    const timer = setTimeout(() => {
      setBusca(entrada.trim());
      setPagina(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [entrada]);

  const consulta = useQuery({
    queryKey: ["manutencoes-painel", etapa, busca, pagina],
    queryFn: () => {
      const filtros = new URLSearchParams({ etapa, busca, pagina: String(pagina) });
      return apiGet<Painel>("/manutencoes/painel?" + filtros);
    },
  });
  const painel = consulta.data;
  const paginas = Math.max(1, Math.ceil((painel?.total ?? 0) / (painel?.por_pagina ?? 12)));

  useEffect(() => {
    if (painel && pagina > paginas) setPagina(paginas);
  }, [painel, pagina, paginas]);

  function atualizar() {
    void qc.invalidateQueries({ queryKey: ["manutencoes-painel"] });
    void qc.invalidateQueries({ queryKey: ["manutencoes"] });
    void qc.invalidateQueries({ queryKey: ["acoplamentos"] });
  }

  function abrirNova(aberto: boolean) {
    setParams((atuais) => {
      const proximos = new URLSearchParams(atuais);
      if (aberto) proximos.set("nova-os", "1");
      else proximos.delete("nova-os");
      return proximos;
    }, { replace: true });
  }

  const remover = useMutation({
    mutationFn: (id: string) => apiDelete("/manutencoes/" + id),
    onSuccess: () => {
      atualizar();
      setExclusao(undefined);
      toast.success("Ordem excluída.");
    },
  });

  return (
    <section>
      <PageHeader eyebrow="Manutenção" title="Ordens de serviço"
        actions={<Button onClick={() => abrirNova(true)}><Plus className="size-4" /> Nova OS</Button>} />
      <CardsManutencao painel={painel} etapa={etapa} />
      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
        <nav aria-label="Etapas das ordens de serviço" className="flex flex-wrap gap-2 border-b border-slate-800 p-3">
          {ETAPAS.map((nome) => (
            <button type="button" key={nome} aria-pressed={etapa === nome}
              className={cn("rounded-lg px-3 py-2 text-left text-sm transition-colors", etapa === nome
                ? "bg-sky-500/15 text-sky-200 ring-1 ring-sky-500/35"
                : "text-slate-300 hover:bg-slate-800")}
              onClick={() => { setEtapa(nome); setPagina(1); }}>
              {nome} {painel && <span className="ml-1 font-mono text-xs text-slate-400">{painel.contagens[nome]}</span>}
            </button>
          ))}
        </nav>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 px-4 py-3">
          <label className="relative w-full max-w-md">
            <span className="sr-only">Buscar ordens</span>
            <Search aria-hidden="true" className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400" />
            <Input value={entrada} maxLength={120} className="pl-9" placeholder="Buscar por código, placa ou serviço"
              onChange={(event) => setEntrada(event.target.value)} />
          </label>
          {painel && <p className="text-sm text-slate-400" aria-live="polite">{painel.total} {painel.total === 1 ? "ordem" : "ordens"}</p>}
        </div>
        {consulta.isPending ? <p role="status" className="p-8 text-center text-slate-400">Carregando ordens…</p> : consulta.isError ? (
          <div role="alert" className="flex flex-wrap items-center gap-3 p-5 text-rose-300">
            {consulta.error.message}<Button variant="outline" onClick={() => consulta.refetch()}>Tentar novamente</Button>
          </div>
        ) : !painel?.itens.length ? (
          <div className="grid justify-items-center gap-2 p-10 text-sm text-slate-400">
            <Wrench className="size-5" aria-hidden="true" /><p>Nenhuma ordem encontrada nesta etapa.</p>
          </div>
        ) : (
          <>
            <div className="hidden grid-cols-[minmax(0,2fr)_minmax(0,1.35fr)_minmax(0,1fr)_8rem_auto] gap-4 border-b border-slate-800 px-4 py-3 text-xs text-slate-400 lg:grid" aria-hidden="true">
              <span>Ordem e veículo</span><span>Fornecedor</span><span>Status</span><span>Valor</span><span>Ações</span>
            </div>
            <ul className="divide-y divide-slate-800">
              {painel.itens.map((os) => (
                <li key={os.id} className="grid min-w-0 gap-3 px-4 py-4 text-sm lg:grid-cols-[minmax(0,2fr)_minmax(0,1.35fr)_minmax(0,1fr)_8rem_auto] lg:items-center lg:gap-4">
                  <div className="min-w-0">
                    <div className="flex flex-wrap gap-x-2 text-xs text-slate-400">
                      <span className="font-mono">{codigo(os)}</span><span>{dataBR(os.data)}</span>
                    </div>
                    <button type="button" onClick={() => setEdicao(os)} className="mt-1 block max-w-full truncate text-left font-semibold text-slate-100 hover:text-sky-300" title={os.descricao}>
                      {os.descricao || "Serviço sem descrição"}
                    </button>
                    <p className="truncate text-slate-400" title={veiculoDa(os)}>{veiculoDa(os)}</p>
                  </div>
                  <p className="truncate text-slate-300" title={os.fornecedor_nome || os.oficina}>{os.fornecedor_nome || os.oficina || "—"}</p>
                  <span className={cn("w-fit rounded-md px-2 py-1 text-xs font-medium", CORES[os.etapa] || "bg-slate-800 text-slate-300")}>{statusDa(os)}</span>
                  <p className="font-mono text-slate-100">{brl(os.custo ?? os.valor ?? 0)}</p>
                  <div className="flex flex-wrap gap-2">
                    <Button size="sm" variant="outline" onClick={() => setEdicao(os)} aria-label={"Editar OS " + codigo(os)}>Editar</Button>
                    <Button size="sm" variant="ghost" className="text-rose-300" aria-label={"Excluir OS " + codigo(os)}
                      onClick={() => { remover.reset(); setExclusao(os); }}>Excluir</Button>
                  </div>
                </li>
              ))}
            </ul>
          </>
        )}
        {painel && painel.total > 0 && (
          <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 px-4 py-3">
            <span className="text-sm text-slate-400">Página {pagina} de {paginas}</span>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={pagina <= 1} onClick={() => setPagina((n) => n - 1)}><ChevronLeft className="size-4" /> Anterior</Button>
              <Button variant="outline" size="sm" disabled={pagina >= paginas} onClick={() => setPagina((n) => n + 1)}>Próxima <ChevronRight className="size-4" /></Button>
            </div>
          </footer>
        )}
      </div>
      {(nova || edicao) && (
        <FormularioOS key={edicao?.id ?? "nova"} os={edicao} atualizar={atualizar} fechar={() => {
          setEdicao(undefined);
          if (nova) abrirNova(false);
        }} />
      )}
      {exclusao && (
        <Dialog open onOpenChange={(aberto) => { if (!aberto && !remover.isPending) setExclusao(undefined); }}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Excluir OS {codigo(exclusao)}?</DialogTitle>
              <DialogDescription>
                {exclusao.descricao || veiculoDa(exclusao)}. A exclusão é definitiva.
                {exclusao.pecas_utilizadas?.length ? " As peças vinculadas serão devolvidas ao estoque." : ""}
              </DialogDescription>
            </DialogHeader>
            {remover.isError && <p role="alert" className="text-sm text-rose-300">{remover.error.message}</p>}
            <div className="flex justify-end gap-2">
              <Button variant="outline" disabled={remover.isPending} onClick={() => setExclusao(undefined)}>Voltar</Button>
              <Button variant="destructive" disabled={remover.isPending} onClick={() => remover.mutate(exclusao.id)}>
                {remover.isPending ? "Excluindo…" : "Excluir definitivamente"}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </section>
  );
}
