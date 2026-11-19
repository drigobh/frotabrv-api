import { useEffect, useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Download, Plus, Search, Wrench } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { toast } from "sonner";
import { useAcoesApi } from "@/hooks/useSession";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { apiDelete, apiGet, apiGetBlob, apiPatch, apiPost } from "@/lib/api";
import { brl } from "@/lib/format";
import { cn } from "@/lib/utils";

const ETAPAS = [
  "Todas", "Aguardando aprovação", "Aguardando peça", "Em execução", "Concluída", "Cancelada", "Outras",
] as const;
type Etapa = typeof ETAPAS[number];

const ORDENACOES = {
  recentes: "Mais recentes",
  antigas: "Mais antigas",
  maior_valor: "Maior valor",
  menor_valor: "Menor valor",
} as const;
type OrdemPainel = keyof typeof ORDENACOES;

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
  plano_manutencao_id?: string;
  km_manutencao?: number;
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
  pecas_utilizadas?: { peca_id: string; quantidade: number | string }[];
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

type PlanoPreventivoOS = {
  id: string; veiculo_id?: string; ativo?: boolean; tipo_gatilho: string;
  familia: string; descricao: string;
};

function FormularioOS({ os, fechar, atualizar }: { os?: Ordem; fechar: () => void; atualizar: () => void }) {
  const veiculos = useQuery({ queryKey: ["veiculos"], queryFn: () => apiGet<Veiculo[]>("/veiculos") });
  const fornecedores = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<Fornecedor[]>("/fornecedores") });
  const [mostrarPecas, setMostrarPecas] = useState(false);
  const [pecaId, setPecaId] = useState("");
  const [itens, setItens] = useState<{ peca_id: string; quantidade: string }[]>([]);
  const pecas = useQuery({
    queryKey: ["pecas"],
    queryFn: () => apiGet<{ id: string; nome: string; quantidade_estoque: number }[]>("/pecas"),
    enabled: mostrarPecas || Boolean(os?.pecas_utilizadas?.length),
  });
  const opcoesPecas = (pecas.data ?? []).filter((peca) =>
    peca.quantidade_estoque > 0 && !itens.some((item) => item.peca_id === peca.id)
  );
  const opcoesVeiculos = (veiculos.data ?? []).filter((v) => v.ativo !== false || v.id === os?.veiculo_id);
  const opcoesFornecedores = fornecedores.data ?? [];
  const [status, setStatus] = useState("");
  const [veiculoId, setVeiculoId] = useState(os?.veiculo_id ?? "");
  const [tipo, setTipo] = useState(os?.tipo || "Corretiva");
  const [planoId, setPlanoId] = useState(os?.plano_manutencao_id ?? "");
  const vinculoFechado = os?.etapa === "Concluída";
  const planos = useQuery({
    queryKey: ["planos-manutencao"],
    queryFn: () => apiGet<PlanoPreventivoOS[]>("/planos-manutencao"),
    enabled: tipo === "Preventiva" && Boolean(veiculoId),
  });
  const elegiveis = (planos.data ?? []).filter((p) =>
    p.veiculo_id === veiculoId && p.ativo !== false && ["km", "dias"].includes(p.tipo_gatilho)
  );
  const plano = elegiveis.find((p) => p.id === planoId);
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
      const vinculo = vinculoFechado ? {} : {
        plano_manutencao_id: planoId || null,
        ...(form.has("km_execucao") && {
          km_manutencao: form.get("km_execucao") === "" ? null : Number(form.get("km_execucao")),
        }),
      };
      if (!os) {
        const pecas_utilizadas = itens.map(({ peca_id, quantidade }) => {
          const unidades = Number(quantidade);
          if (!Number.isSafeInteger(unidades) || unidades < 1) {
            throw new Error("Informe uma quantidade inteira e positiva para cada peça.");
          }
          const peca = pecas.data?.find((item) => item.id === peca_id);
          if (!peca || unidades > peca.quantidade_estoque) {
            throw new Error(`Confira o saldo disponível para ${peca?.nome ?? "a peça selecionada"}.`);
          }
          return { peca_id, quantidade: unidades };
        });
        return apiPost("/manutencoes", { ...dados, ...vinculo, status: "Aguardando aprovação", pecas_utilizadas });
      }
      const transicao = status ? { status, status_original: os.status ?? null } : {};
      return apiPatch("/manutencoes/" + os.id + "/dados", { ...dados, ...vinculo, ...transicao, versao: os.versao_dados ?? null });
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
              <select name="veiculo" className={campo} required value={veiculoId} onChange={(e) => { setVeiculoId(e.target.value); if (!vinculoFechado) setPlanoId(""); }}>
                <option value="" disabled>{veiculos.isPending ? "Carregando veículos…" : "Selecione um veículo"}</option>
                {os?.veiculo_id && !opcoesVeiculos.some((v) => v.id === os.veiculo_id) && <option value={os.veiculo_id}>{veiculoDa(os)}</option>}
                {opcoesVeiculos.map((v) => <option key={v.id} value={v.id}>{v.placa} · {v.modelo}</option>)}
              </select>
            </label>
            <label className="space-y-1 text-sm">
              <span>Tipo de manutenção</span>
              <select name="tipo" className={campo} value={tipo} onChange={(e) => { setTipo(e.target.value); if (!vinculoFechado) setPlanoId(""); }} required>
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
            {(tipo === "Preventiva" || planoId) && (
              <label className="space-y-1 text-sm sm:col-span-2">
                <span>Plano preventivo</span>
                <select className={campo} disabled={vinculoFechado || !veiculoId}
                  value={planoId} onChange={(e) => setPlanoId(e.target.value)}>
                  <option value="">{planos.isFetching ? "Carregando planos…" : "Sem plano vinculado"}</option>
                  {planoId && !plano && <option value={planoId}>Plano vinculado · {planoId.slice(0, 8)}</option>}
                  {elegiveis.map((p) => <option key={p.id} value={p.id}>{p.familia} · {p.descricao}</option>)}
                </select>
              </label>
            )}
            {plano?.tipo_gatilho === "km" && (
              <label key={plano.id} className="space-y-1 text-sm">
                <span>Hodômetro da execução (km)</span>
                <Input name="km_execucao" type="number" min={0} step="any" disabled={vinculoFechado}
                  required={status === "Concluída"} defaultValue={os?.km_manutencao ?? ""} />
              </label>
            )}
            {!os && (
              <details className="rounded-lg border border-border p-3 sm:col-span-2"
                onToggle={(event) => setMostrarPecas(event.currentTarget.open)}>
                <summary className="cursor-pointer text-sm font-medium">Peças do estoque{itens.length ? ` (${itens.length})` : ""}</summary>
                <p className="mt-2 text-sm text-slate-400">O saldo é baixado ao salvar a OS.</p>
                <div className="mt-3 flex flex-wrap items-end gap-2">
                  <label className="min-w-0 flex-1 space-y-1 text-sm">
                    <span>Peça</span>
                    <select className={campo} value={pecaId} onChange={(event) => setPecaId(event.target.value)}>
                      <option value="">{pecas.isPending ? "Carregando…" : "Selecione uma peça"}</option>
                      {opcoesPecas.map((peca) => <option key={peca.id} value={peca.id}>{peca.nome} · saldo {peca.quantidade_estoque}</option>)}
                    </select>
                  </label>
                  <Button type="button" variant="outline" disabled={!opcoesPecas.some((peca) => peca.id === pecaId)}
                    onClick={() => { setItens([...itens, { peca_id: pecaId, quantidade: "1" }]); setPecaId(""); }}>
                    Adicionar peça
                  </Button>
                </div>
                {pecas.isError ? <p role="alert" className="mt-2 text-sm text-rose-300">
                  Falha ao carregar o estoque. <button type="button" className="underline" onClick={() => pecas.refetch()}>Tentar novamente</button>
                </p> : pecas.isSuccess && !opcoesPecas.length && !itens.length && (
                  <p className="mt-2 text-sm text-slate-400">Nenhuma peça com saldo disponível.</p>
                )}
                <ul className="mt-2 divide-y divide-border">
                  {itens.map((item) => {
                    const peca = pecas.data?.find((p) => p.id === item.peca_id);
                    const nome = peca?.nome ?? item.peca_id;
                    return (
                      <li key={item.peca_id} className="flex flex-wrap items-end gap-2 py-2">
                        <span className="min-w-0 flex-1 self-center break-words text-sm">{nome}</span>
                        <label className="w-24 space-y-1 text-sm">
                          <span>Quantidade</span>
                          <Input type="number" inputMode="numeric" value={item.quantidade}
                            aria-label={`Quantidade de ${nome}`}
                            onChange={(event) => setItens(itens.map((p) => p.peca_id === item.peca_id ? { ...p, quantidade: event.target.value } : p))} />
                        </label>
                        <Button type="button" variant="ghost" aria-label={`Remover ${nome}`}
                          onClick={() => setItens(itens.filter((p) => p.peca_id !== item.peca_id))}>Remover</Button>
                      </li>
                    );
                  })}
                </ul>
              </details>
            )}
            {Boolean(os?.pecas_utilizadas?.length) && (
              <div className="space-y-1 rounded-lg border border-border p-3 text-sm sm:col-span-2">
                <p className="font-medium">Peças vinculadas</p>
                <ul className="space-y-1 text-slate-400">
                  {os?.pecas_utilizadas?.map((item, indice) => (
                    <li key={indice}>{pecas.data?.find((peca) => peca.id === item.peca_id)?.nome ?? item.peca_id} · {item.quantidade} un.</li>
                  ))}
                </ul>
              </div>
            )}
            {tipo === "Preventiva" && planos.isError && <p role="alert" className="text-sm text-rose-300">
              Falha ao carregar planos. <button type="button" className="underline" onClick={() => planos.refetch()}>Recarregar</button>
            </p>}
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

type EventoOS = {
  id: string;
  acao: "abertura" | "alteracao";
  data: string;
  autor: string;
  alteracoes: { campo: "status" | "valor" | "fornecedor"; antes: string | number | null; depois: string | number | null }[];
};
type HistoricoOS = { eventos: EventoOS[]; anterior_ao_historico: boolean };

const ROTULOS_HISTORICO = { status: "Status", valor: "Valor", fornecedor: "Fornecedor" } as const;

function exibirAlteracao(campo: keyof typeof ROTULOS_HISTORICO, valor: string | number | null) {
  if (valor === null || valor === "") return "—";
  const numero = Number(valor);
  return campo === "valor" && Number.isFinite(numero) ? brl(numero) : String(valor);
}

function DialogoHistorico({ os, fechar }: { os: Ordem; fechar: () => void }) {
  const consulta = useQuery({
    queryKey: ["manutencoes-historico", os.id],
    queryFn: () => apiGet<HistoricoOS>("/manutencoes/" + encodeURIComponent(os.id) + "/historico"),
  });
  const dataHora = new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short", timeStyle: "short", timeZone: "America/Sao_Paulo",
  });

  return (
    <Dialog open onOpenChange={(aberto) => { if (!aberto) fechar(); }}>
      <DialogContent className="max-h-[85dvh] overflow-y-auto sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>Histórico da OS {codigo(os)}</DialogTitle>
          <DialogDescription>{os.descricao || veiculoDa(os)}</DialogDescription>
        </DialogHeader>
        {consulta.isPending ? <p role="status">Carregando histórico…</p> : consulta.isError ? (
          <div role="alert" className="flex flex-wrap items-center gap-3">
            <span>{consulta.error.message}</span>
            <Button size="sm" variant="outline" onClick={() => consulta.refetch()}>Tentar novamente</Button>
          </div>
        ) : (
          <>
            {consulta.data.anterior_ao_historico && (
              <p className="text-sm text-slate-400">Alterações anteriores à ativação do histórico não foram registradas.</p>
            )}
            {consulta.data.eventos.length === 0 ? <p className="text-sm text-slate-400">Nenhum evento registrado.</p> : (
              <ol className="space-y-3">
                {consulta.data.eventos.map((evento) => {
                  const data = new Date(evento.data);
                  return (
                    <li key={evento.id} className="rounded-lg border border-slate-800 p-4">
                      <div className="flex flex-wrap justify-between gap-2">
                        <span className="font-medium">{evento.acao === "abertura" ? "OS aberta" : "OS alterada"}</span>
                        <span className="text-sm text-slate-400">{Number.isNaN(data.getTime()) ? evento.data : dataHora.format(data)}</span>
                      </div>
                      <p className="mt-1 break-words text-sm text-slate-400">{evento.autor}</p>
                      {evento.alteracoes.length > 0 && (
                        <dl className="mt-3 space-y-2 border-t border-slate-800 pt-3 text-sm">
                          {evento.alteracoes.map(({ campo, antes, depois }) => (
                            <div key={campo}>
                              <dt className="font-medium">{ROTULOS_HISTORICO[campo]}</dt>
                              <dd className="break-words text-slate-300">
                                {evento.acao !== "abertura" && <>{exibirAlteracao(campo, antes)} → </>}
                                {exibirAlteracao(campo, depois)}
                              </dd>
                            </div>
                          ))}
                        </dl>
                      )}
                    </li>
                  );
                })}
              </ol>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}


export default function Manutencoes() {
  const { podeLer, podeEscrever, podeExcluir } = useAcoesApi();
  const qc = useQueryClient();
  const [params, setParams] = useSearchParams();
  const [etapa, setEtapa] = useState<Etapa>("Todas");
  const [entrada, setEntrada] = useState("");
  const [busca, setBusca] = useState("");
  const [pagina, setPagina] = useState(1);
  const [ordem, setOrdem] = useState<OrdemPainel>("recentes");
  const [de, setDe] = useState("");
  const [ate, setAte] = useState("");
  const periodoInvalido = Boolean(de && ate && de > ate);

  function aplicarPeriodo(inicio: string, fim: string) {
    setDe(inicio);
    setAte(fim);
    setPagina(1);
  }

  function selecionarMes(deslocamento: number) {
    const [ano, mes] = new Date().toLocaleDateString("sv-SE", { timeZone: "America/Sao_Paulo" }).split("-").map(Number);
    const indiceMes = mes - 1 + deslocamento;
    const inicio = new Date(Date.UTC(ano, indiceMes, 1)).toISOString().slice(0, 10);
    const fim = new Date(Date.UTC(ano, indiceMes + 1, 0)).toISOString().slice(0, 10);
    aplicarPeriodo(inicio, fim);
  }
  const [edicao, setEdicao] = useState<Ordem>();
  const [historico, setHistorico] = useState<Ordem>();
  const [exclusao, setExclusao] = useState<Ordem>();
  const nova = params.get("nova-os") === "1";

  useEffect(() => {
    const timer = setTimeout(() => {
      setBusca(entrada.trim());
      setPagina(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [entrada]);

  function filtrosPainel() {
    const filtros = new URLSearchParams({ etapa, busca, ordem });
    if (de) filtros.set("de", de);
    if (ate) filtros.set("ate", ate);
    return filtros;
  }

  const exportacao = useMutation({
    mutationFn: (filtros: URLSearchParams) => apiGetBlob("/manutencoes/painel/exportar?" + filtros),
    onSuccess: (arquivo) => {
      const url = URL.createObjectURL(arquivo);
      const link = document.createElement("a");
      link.href = url;
      link.download = "ordens-de-servico.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    },
    onError: (erro: Error) => toast.error(erro.message || "Falha ao exportar ordens de serviço."),
  });

  const consulta = useQuery({
    queryKey: ["manutencoes-painel", etapa, busca, pagina, de, ate, ordem],
    enabled: !periodoInvalido,
    queryFn: () => {
      const filtros = filtrosPainel();
      filtros.set("pagina", String(pagina));
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
    void qc.invalidateQueries({ queryKey: ["manutencoes-historico"] });
    void qc.invalidateQueries({ queryKey: ["planos-manutencao"] });
    void qc.invalidateQueries({ queryKey: ["manutencoes"] });
    void qc.invalidateQueries({ queryKey: ["acoplamentos"] });
    void qc.invalidateQueries({ queryKey: ["pecas"] });
    void qc.invalidateQueries({ queryKey: ["movimentacoes"] });
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
        actions={<>
          <Button variant="outline" disabled={!podeLer || !painel?.total || periodoInvalido || entrada.trim() !== busca || exportacao.isPending}
            onClick={() => exportacao.mutate(filtrosPainel())}>
            <Download className="size-4" /> {exportacao.isPending ? "Exportando…" : "Exportar CSV"}
          </Button>
          {podeEscrever && <Button onClick={() => abrirNova(true)}><Plus className="size-4" /> Nova OS</Button>}
        </>} />
      <fieldset className="mb-5 rounded-xl border border-slate-800 bg-slate-900/60 px-4 pb-4">
        <legend className="px-2 text-sm font-medium text-slate-200">Período de abertura da OS</legend>
        <div className="flex flex-wrap items-end gap-3">
          <label className="space-y-1 text-sm text-slate-300">
            <span>De</span>
            <Input type="date" value={de} aria-invalid={periodoInvalido}
              onChange={(event) => aplicarPeriodo(event.target.value, ate)} />
          </label>
          <label className="space-y-1 text-sm text-slate-300">
            <span>Até</span>
            <Input type="date" value={ate} aria-invalid={periodoInvalido}
              onChange={(event) => aplicarPeriodo(de, event.target.value)} />
          </label>
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="outline" onClick={() => selecionarMes(0)}>Este mês</Button>
            <Button type="button" variant="outline" onClick={() => selecionarMes(-1)}>Mês anterior</Button>
            <Button type="button" variant="ghost" disabled={!de && !ate} onClick={() => aplicarPeriodo("", "")}>Limpar período</Button>
          </div>
        </div>
        {periodoInvalido && <p role="alert" className="mt-2 text-sm text-rose-300">A data final deve ser igual ou posterior à inicial.</p>}
      </fieldset>
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
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <span className="whitespace-nowrap">Ordenar por</span>
            <select value={ordem} className={campo} onChange={(event) => {
              setOrdem(event.target.value as OrdemPainel);
              setPagina(1);
            }}>
              {Object.entries(ORDENACOES).map(([valor, rotulo]) => <option key={valor} value={valor}>{rotulo}</option>)}
            </select>
          </label>
          {painel && <p className="text-sm text-slate-400" aria-live="polite">{painel.total} {painel.total === 1 ? "ordem" : "ordens"}</p>}
        </div>
        {periodoInvalido ? null : consulta.isPending ? <p role="status" className="p-8 text-center text-slate-400">Carregando ordens…</p> : consulta.isError ? (
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
                    {podeEscrever ? <button type="button" onClick={() => setEdicao(os)} className="mt-1 block max-w-full truncate text-left font-semibold text-slate-100 hover:text-sky-300" title={os.descricao}>
                      {os.descricao || "Serviço sem descrição"}
                    </button> : <p className="mt-1 truncate font-semibold text-slate-100" title={os.descricao}>{os.descricao || "Serviço sem descrição"}</p>}
                    <p className="truncate text-slate-400" title={veiculoDa(os)}>{veiculoDa(os)}</p>
                  </div>
                  <p className="truncate text-slate-300" title={os.fornecedor_nome || os.oficina}>{os.fornecedor_nome || os.oficina || "—"}</p>
                  <span className={cn("w-fit rounded-md px-2 py-1 text-xs font-medium", CORES[os.etapa] || "bg-slate-800 text-slate-300")}>{statusDa(os)}</span>
                  <p className="font-mono text-slate-100">{brl(os.custo ?? os.valor ?? 0)}</p>
                  <div className="flex flex-wrap gap-2">
                    <Button size="sm" variant="ghost" onClick={() => setHistorico(os)} aria-label={"Histórico da OS " + codigo(os)}>Histórico</Button>
                    {podeEscrever && <Button size="sm" variant="outline" onClick={() => setEdicao(os)} aria-label={"Editar OS " + codigo(os)}>Editar</Button>}
                    {podeExcluir && <Button size="sm" variant="ghost" className="text-rose-300" aria-label={"Excluir OS " + codigo(os)}
                      onClick={() => { remover.reset(); setExclusao(os); }}>Excluir</Button>}
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
      {podeEscrever && (nova || edicao) && (
        <FormularioOS key={edicao?.id ?? "nova"} os={edicao} atualizar={atualizar} fechar={() => {
          setEdicao(undefined);
          if (nova) abrirNova(false);
        }} />
      )}
      {historico && <DialogoHistorico os={historico} fechar={() => setHistorico(undefined)} />}
      {podeExcluir && exclusao && (
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
