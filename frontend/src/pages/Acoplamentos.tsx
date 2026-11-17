import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link2, Plus, Pencil, Trash2, History, Clock, User, Truck } from "lucide-react";
import { toast } from "sonner";
import { ApiError, apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { FieldSelect } from "@/components/common/FieldSelect";
import { useMotoristas, useVeiculos, useCarretas } from "@/hooks/useCadastros";

type Campo = "veiculo_id" | "carreta_id" | "motorista_id";
type Conflito = {
  funcao: string; item: string; conjunto_id: string | null;
  veiculo: string | null; carreta: string | null; motorista: string | null;
  inicio_conjunto: string | null; vinculado_em: string | null;
};

const SEM_VINCULO = "__sem_vinculo__";
const HISTORICO_GERAL = "geral";

function formatarData(valor: string | null) {
  if (!valor) return "Não registrado";
  const data = new Date(valor);
  if (Number.isNaN(data.getTime())) return "Não registrado";
  return /^\d{4}-\d{2}-\d{2}$/.test(valor)
    ? data.toLocaleDateString("pt-BR", { timeZone: "UTC" })
    : data.toLocaleString("pt-BR");
}

export default function Acoplamentos() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [historicoId, setHistoricoId] = useState<string | null>(null);
  const { data: authUser } = useQuery({ queryKey: ["me"], queryFn: () => apiGet<any>("/auth/me") });
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const carretas = useCarretas();
  const q = useQuery({ queryKey: ["acoplamentos"], queryFn: () => apiGet<any[]>("/acoplamentos") });
  const histQuery = useQuery({ queryKey: ["acoplamento-historico", historicoId], queryFn: () => apiGet<any[]>(historicoId === HISTORICO_GERAL ? "/acoplamentos/historico" : `/acoplamentos/${historicoId}/historico`), enabled: !!historicoId });
  const rows = q.data ?? [];
  const [form, setForm] = useState({ veiculo_id: "", carreta_id: "", motorista_id: "", data_inicio: "", data_fim: "" });

  const atualizarDisponibilidade = async () => {
    await Promise.all(
      [["acoplamentos"], ["acoplamento-historico"], ["veiculos"], ["carretas"], ["motoristas"]]
        .map((queryKey) => qc.invalidateQueries({ queryKey })),
    );
  };

  const opcoesLivres = <T extends { id: string; ativo: boolean; acoplado?: boolean }>(
    itens: T[], campo: Campo, nome: (item: T) => string,
  ) => {
    const doConjuntoAtual = rows.find((row) => row.id === editingId)?.[campo];
    const ocupados = new Set(rows.filter((row) => row.id !== editingId).map((row) => row[campo]));
    return itens
      .filter((item) => item.ativo && !ocupados.has(item.id) && (!item.acoplado || item.id === doConjuntoAtual))
      .map((item) => ({ value: item.id, label: nome(item) }));
  };

  const salvar = useMutation({
    mutationFn: () => {
      const dados = { ...form, carreta_id: form.carreta_id || null, motorista_id: form.motorista_id || null };
      return editingId ? apiPut(`/acoplamentos/${editingId}`, dados) : apiPost("/acoplamentos", dados);
    },
    onSuccess: () => { toast.success("Salvo"); setOpen(false); setEditingId(null); void atualizarDisponibilidade(); },
    onError: () => { void atualizarDisponibilidade(); },
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/acoplamentos/${id}`),
    onSuccess: () => { toast.success("Desacoplado"); setExcluirId(null); void atualizarDisponibilidade(); },
    onError: (erro) => toast.error(erro.message),
  });

  const prepararFormulario = () => {
    salvar.reset();
    void atualizarDisponibilidade();
    setOpen(true);
  };
  const abrirNovo = () => {
    setEditingId(null);
    setForm({ veiculo_id: "", carreta_id: "", motorista_id: "", data_inicio: new Date().toISOString().split("T")[0], data_fim: "" });
    prepararFormulario();
  };
  const abrirEdicao = (r: any) => {
    setEditingId(r.id);
    setForm({ veiculo_id: r.veiculo_id, carreta_id: r.carreta_id || "", motorista_id: r.motorista_id || "", data_inicio: r.data_inicio || "", data_fim: r.data_fim || "" });
    prepararFormulario();
  };
  const alterarItem = (campo: Campo, valor: string) => {
    if (salvar.isError) salvar.reset();
    setForm((atual) => ({ ...atual, [campo]: valor === SEM_VINCULO ? "" : valor }));
  };
  const detalhe = salvar.error instanceof ApiError ? salvar.error.body?.detail : null;
  const conflitos: Conflito[] = detalhe?.codigo === "ITENS_EM_USO" && Array.isArray(detalhe.conflitos)
    ? detalhe.conflitos
    : [];
  const falhaDisponibilidade = [q, veiculos, carretas, motoristas].some((consulta) => consulta.isError);
  const carregandoDisponibilidade = [q, veiculos, carretas, motoristas].some((consulta) => consulta.isPending);
  const podeSalvar = !!form.veiculo_id && !salvar.isPending && !falhaDisponibilidade && !carregandoDisponibilidade;
  const cavalosLivres = opcoesLivres(veiculos.data ?? [], "veiculo_id", (v) => v.placa);
  const carretasLivres = opcoesLivres(carretas.data ?? [], "carreta_id", (c) => c.codigo);
  const motoristasLivres = opcoesLivres(motoristas.data ?? [], "motorista_id", (m) => m.nome);

  return (
    <div>
      <PageHeader eyebrow="Operação" title="Acoplamentos" description="Vincule motoristas aos veículos." actions={<div className="flex flex-wrap gap-2"><Button variant="outline" onClick={() => setHistoricoId(HISTORICO_GERAL)}><History className="size-4" /> Histórico geral</Button><Button onClick={abrirNovo}><Plus className="size-4 mr-2" /> Novo</Button></div>} />
      <div className="glass overflow-hidden rounded-2xl">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800">
              <TableHead>Veículo</TableHead><TableHead className="text-slate-400 font-semibold">Carreta</TableHead>
                      <TableHead>Motorista</TableHead><TableHead>Início</TableHead>
                      <TableHead>Usuário</TableHead><TableHead>Fim</TableHead><TableHead className="text-center">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((r: any) => (
              <TableRow key={r.id}>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {r.manutencao && (
                      <div title={`Em manutenção desde ${new Date(r.manutencao.data).toLocaleDateString("pt-BR")} por ${r.manutencao.usuario}`}>
                        <Truck className="size-4 text-red-500 animate-pulse drop-shadow-[0_0_5px_rgba(239,68,68,0.8)]" />
                      </div>
                    )}
                    <span>{r.veiculo_label}</span>
                  </div>
                </TableCell>
                <TableCell>{r.carreta_label || "—"}</TableCell>
                <TableCell>{r.motorista_label}</TableCell>
                <TableCell>{r.data_inicio ? new Date(r.data_inicio).toLocaleDateString("pt-BR", {timeZone: "UTC"}) : "—"}</TableCell>
                <TableCell className="text-xs text-slate-400">{r.updated_by || r.created_by || "—"}</TableCell>
                <TableCell>{r.data_fim || "—"}</TableCell>
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => setHistoricoId(r.id)} title="Histórico"><History className="size-4 text-amber-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Acoplamento</DialogTitle></DialogHeader>
          <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); if (podeSalvar) salvar.mutate(); }}>
            <FieldSelect value={form.veiculo_id} onChange={(v) => alterarItem("veiculo_id", v)} options={cavalosLivres}
              placeholder={cavalosLivres.length ? "Cavalo / veículo livre" : "Nenhum disponível"} />
            <FieldSelect value={form.carreta_id || SEM_VINCULO} onChange={(v) => alterarItem("carreta_id", v)} options={[{ value: SEM_VINCULO, label: "Sem carreta" }, ...carretasLivres]}
              placeholder={carretasLivres.length ? "Carreta livre" : "Nenhum disponível"} />
            <FieldSelect value={form.motorista_id || SEM_VINCULO} onChange={(v) => alterarItem("motorista_id", v)} options={[{ value: SEM_VINCULO, label: "Sem motorista" }, ...motoristasLivres]}
              placeholder={motoristasLivres.length ? "Motorista livre" : "Nenhum disponível"} />
            <div className="flex items-center gap-2 p-2 rounded-md bg-slate-800/50 border border-slate-700/50 text-sm text-slate-300">
              <User className="size-4 text-sky-400" />
              <span>Usuário Logado: <strong>{authUser?.nome || "Carregando..."}</strong></span>
            </div>
            <div className="grid grid-cols-2 gap-3">
            <Input type="date" value={form.data_inicio} onChange={(e) => setForm(s => ({ ...s, data_inicio: e.target.value }))} />
            </div>
            {carregandoDisponibilidade && <p className="text-sm text-slate-400">Carregando disponibilidade…</p>}
            {falhaDisponibilidade && (
              <p role="alert" className="text-sm text-rose-200">
                Não foi possível confirmar a disponibilidade. <button type="button" className="underline" onClick={() => void atualizarDisponibilidade()}>Tentar novamente</button>
              </p>
            )}
            {!falhaDisponibilidade && !carregandoDisponibilidade && !cavalosLivres.length && (
              <p className="text-sm text-slate-400">Nenhum cavalo ou veículo ativo está livre para acoplar.</p>
            )}
            {salvar.error && (
              <div role="alert" className="max-h-56 space-y-2 overflow-y-auto rounded-lg border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-200">
                <p className="font-semibold">{conflitos.length ? "Itens já em uso" : salvar.error.message}</p>
                {conflitos.map((conflito) => (
                  <div key={`${conflito.funcao}-${conflito.conjunto_id}`} className="border-t border-rose-500/20 pt-2">
                    <p className="font-medium">{conflito.funcao}: {conflito.item}</p>
                    <p>Motivo: vínculo em um acoplamento ativo.</p>
                    <p>Conjunto: {[conflito.veiculo, conflito.carreta, conflito.motorista].filter(Boolean).join(" · ") || conflito.conjunto_id || "Não identificado"}</p>
                    <p>Início informado do conjunto: {formatarData(conflito.inicio_conjunto)}</p>
                    {conflito.vinculado_em && <p>Vínculo registrado em: {formatarData(conflito.vinculado_em)}</p>}
                  </div>
                ))}
                {conflitos.length > 0 && <p>Selecione um item livre ou encerre o conjunto atual antes de reutilizá-lo.</p>}
              </div>
            )}
            <DialogFooter><Button type="submit" disabled={!podeSalvar}>{salvar.isPending ? "Salvando…" : "Salvar"}</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <ConfirmDialog open={excluirId !== null} onOpenChange={(o) => !o && setExcluirId(null)} title="Desacoplar conjunto?" onConfirm={() => excluirId && excluir.mutate(excluirId)} confirmLabel="Desacoplar" destructive pending={excluir.isPending} testId="excluir" />

      {/* Modal de Histórico */}
      <Dialog open={!!historicoId} onOpenChange={(o) => !o && setHistoricoId(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>{historicoId === HISTORICO_GERAL ? "Histórico geral de acoplamentos" : "Histórico de movimentações"}</DialogTitle></DialogHeader>
          <div className="max-h-[60vh] overflow-y-auto space-y-4 pr-2 mt-2">
            {histQuery.isLoading ? (
              <p className="text-sm text-slate-400 text-center py-4">Carregando histórico...</p>
            ) : histQuery.isError ? (
              <p role="alert" className="text-sm text-rose-300">Não foi possível carregar o histórico. <button type="button" className="underline" onClick={() => void histQuery.refetch()}>Tentar novamente</button></p>
            ) : histQuery.data?.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-4">Nenhuma movimentação registrada.</p>
            ) : (
              histQuery.data?.map((h: any) => (
                <div key={h.id} className="flex gap-3 text-sm">
                  <div className="mt-0.5"><Clock className="size-4 text-amber-400" /></div>
                  <div>
                    <p className="font-semibold text-slate-200">{h.evento}</p>
                    <p className="text-slate-400 text-xs">{h.descricao}</p>
                    <p className="text-slate-400 text-xs mt-1">{[h.conjunto, h.usuario, formatarData(h.created_at)].filter(Boolean).join(" · ")}</p>
                  </div>
                </div>
              ))
            )}
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setHistoricoId(null)}>Fechar</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
