import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FileBadge, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api";
import { dataBR, errMsg } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { StatusBadge, type Tone } from "@/components/common/StatusBadge";
import { useMotoristas, useVeiculos } from "@/hooks/useCadastros";
import { useMe } from "@/hooks/useSession";
import { SITUACAO_LABEL, TIPOS_DOC, type Documento, type DocumentoCreate, type EntidadeDoc, type SituacaoDoc } from "@/types/documentos";

type Filtro = "todos" | SituacaoDoc;
type FiltroEntidade = "todas" | EntidadeDoc;
const TOM: Record<SituacaoDoc, Tone> = { vigente: "ativo", vencendo: "desacoplado", vencido: "excluido" };

const vazio = (entidade: EntidadeDoc = "veiculo"): DocumentoCreate => ({
  entidade, entidade_id: "", tipo: TIPOS_DOC[entidade][0], numero: "", emissao: null, validade: "", observacoes: "",
});

function prazo(d: Documento) {
  if (d.dias_restantes < 0) return `vencido há ${-d.dias_restantes} d`;
  if (d.dias_restantes === 0) return "vence hoje";
  return `em ${d.dias_restantes} d`;
}

export default function Documentos() {
  const qc = useQueryClient();
  const { data: me } = useMe();
  const veiculos = useVeiculos();
  const motoristas = useMotoristas();
  const [filtro, setFiltro] = useState<Filtro>("todos");
  const [entidade, setEntidade] = useState<FiltroEntidade>("todas");
  const [open, setOpen] = useState(false);
  const [editando, setEditando] = useState<string | null>(null);
  const [form, setForm] = useState<DocumentoCreate>(vazio());
  const [excluirId, setExcluirId] = useState<string | null>(null);

  const q = useQuery({ queryKey: ["documentos"], queryFn: () => apiGet<Documento[]>("/documentos") });
  const todos = q.isError ? [] : (q.data ?? []);
  const porEntidade = useMemo(() => (entidade === "todas" ? todos : todos.filter((d) => d.entidade === entidade)), [todos, entidade]);
  const rows = filtro === "todos" ? porEntidade : porEntidade.filter((d) => d.situacao === filtro);
  const contagem = (s: SituacaoDoc) => porEntidade.filter((d) => d.situacao === s).length;

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: ["documentos"] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const salvar = useMutation({
    mutationFn: ({ id, body }: { id: string | null; body: DocumentoCreate }) =>
      id ? apiPut<Documento>(`/documentos/${id}`, body) : apiPost<Documento>("/documentos", body),
    onSuccess: (_d, v) => { toast.success(v.id ? "Documento atualizado" : "Documento cadastrado"); setOpen(false); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });
  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete<void>(`/documentos/${id}`),
    onSuccess: () => { toast.success("Documento excluído"); setExcluirId(null); invalidate(); },
    onError: (e) => toast.error(errMsg(e)),
  });

  const opcoesEntidade =
    form.entidade === "veiculo"
      ? (veiculos.data ?? []).map((v) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }))
      : (motoristas.data ?? []).map((m) => ({ value: m.id, label: m.nome }));
  const tiposForm = TIPOS_DOC[form.entidade].includes(form.tipo) ? TIPOS_DOC[form.entidade] : [form.tipo, ...TIPOS_DOC[form.entidade]];

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Documentos e vencimentos"
        description="CRLV, ANTT, seguro, MOPP, toxicológico… O dashboard avisa 30 dias antes de cada vencimento."
        actions={
          <Button onClick={() => { setEditando(null); setForm(vazio()); setOpen(true); }} data-testid="documento-new-button">
            <Plus className="size-4" /> Novo documento
          </Button>
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <Tabs value={filtro} onValueChange={(v) => setFiltro(v as Filtro)}>
          <TabsList>
            <TabsTrigger value="todos" data-testid="documento-tab-todos">Todos ({porEntidade.length})</TabsTrigger>
            {(["vencido", "vencendo", "vigente"] as SituacaoDoc[]).map((s) => (
              <TabsTrigger key={s} value={s} data-testid={`documento-tab-${s}`}>{SITUACAO_LABEL[s]} ({contagem(s)})</TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
        <div className="w-48">
          <FieldSelect
            value={entidade}
            onChange={(v) => setEntidade(v as FiltroEntidade)}
            options={[{ value: "todas", label: "Veículos e motoristas" }, { value: "veiculo", label: "Só veículos" }, { value: "motorista", label: "Só motoristas" }]}
            testId="documento-filtro-entidade"
          />
        </div>
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="documento-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Documento", "De", "Número", "Emissão", "Validade", "Prazo", "Situação", ""].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={8} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhum documento neste filtro."}</TableCell></TableRow>
            )}
            {rows.map((d) => (
              <TableRow key={d.id} className="border-slate-800/70" data-testid={`documento-row-${d.id}`}>
                <TableCell className="font-medium text-slate-100">{d.tipo}</TableCell>
                <TableCell>
                  <span className="text-xs text-slate-500">{d.entidade === "veiculo" ? "Veículo" : "Motorista"}</span>
                  <p className={d.entidade === "veiculo" ? "font-mono" : ""}>{d.entidade_label.split(" · ")[0]}</p>
                </TableCell>
                <TableCell className="font-mono text-xs text-slate-400">{d.numero || "—"}</TableCell>
                <TableCell className="font-mono text-sm text-slate-400">{dataBR(d.emissao)}</TableCell>
                <TableCell className="font-mono text-sm">{dataBR(d.validade)}</TableCell>
                <TableCell className={d.situacao === "vigente" ? "text-slate-400" : d.situacao === "vencido" ? "text-red-300" : "text-amber-300"}>{prazo(d)}</TableCell>
                <TableCell><StatusBadge tone={TOM[d.situacao]} testId={`documento-situacao-${d.id}`}>{SITUACAO_LABEL[d.situacao]}</StatusBadge></TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button size="icon-sm" variant="ghost" aria-label="Editar" data-testid={`documento-edit-${d.id}`}
                      onClick={() => { setEditando(d.id); setForm({ entidade: d.entidade, entidade_id: d.entidade_id, tipo: d.tipo, numero: d.numero, emissao: d.emissao, validade: d.validade, observacoes: d.observacoes }); setOpen(true); }}>
                      <Pencil className="size-4" />
                    </Button>
                    {me?.perfil === "admin" && (
                      <Button size="icon-sm" variant="ghost" className="text-red-300" aria-label="Excluir" onClick={() => setExcluirId(d.id)} data-testid={`documento-delete-${d.id}`}>
                        <Trash2 className="size-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-lg" data-testid="documento-dialog">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><FileBadge className="size-5 text-sky-400" /> {editando ? "Editar documento" : "Novo documento"}</DialogTitle>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate({ id: editando, body: { ...form, emissao: form.emissao || null } }); }}>
            <div className="grid gap-1.5">
              <Label>Pertence a *</Label>
              <FieldSelect value={form.entidade} onChange={(v) => setForm(vazio(v as EntidadeDoc))} options={[{ value: "veiculo", label: "Veículo" }, { value: "motorista", label: "Motorista" }]} testId="documento-form-entidade" />
            </div>
            <div className="grid gap-1.5">
              <Label>Tipo *</Label>
              <FieldSelect value={form.tipo} onChange={(v) => setForm((s) => ({ ...s, tipo: v }))} options={tiposForm.map((t) => ({ value: t, label: t }))} testId="documento-form-tipo" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>{form.entidade === "veiculo" ? "Veículo *" : "Motorista *"}</Label>
              <FieldSelect value={form.entidade_id} onChange={(v) => setForm((s) => ({ ...s, entidade_id: v }))} options={opcoesEntidade} placeholder="Selecione" testId="documento-form-entidade-id" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="doc-num">Número</Label>
              <Input id="doc-num" value={form.numero} onChange={(e) => setForm((s) => ({ ...s, numero: e.target.value }))} data-testid="documento-form-numero" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="doc-em">Emissão</Label>
              <Input id="doc-em" type="date" value={form.emissao ?? ""} onChange={(e) => setForm((s) => ({ ...s, emissao: e.target.value || null }))} data-testid="documento-form-emissao" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="doc-val">Validade *</Label>
              <Input id="doc-val" type="date" required value={form.validade} onChange={(e) => setForm((s) => ({ ...s, validade: e.target.value }))} data-testid="documento-form-validade" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="doc-obs">Observações</Label>
              <Textarea id="doc-obs" rows={2} value={form.observacoes} onChange={(e) => setForm((s) => ({ ...s, observacoes: e.target.value }))} data-testid="documento-form-observacoes" />
            </div>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={salvar.isPending || !form.entidade_id || !form.validade} data-testid="documento-form-submit">Salvar</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir documento?"
        description="Esta ação é registrada na auditoria e não pode ser desfeita."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="documento-excluir"
      />
    </div>
  );
}
