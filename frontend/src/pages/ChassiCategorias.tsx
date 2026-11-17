import { useState, type FormEvent } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus, Power, RotateCcw, Trash2 } from "lucide-react";
import { apiDelete, apiGet, apiPatch, apiPost, apiPut } from "@/lib/api";
import { errMsg } from "@/lib/format";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type TipoAplicacao = { id: string; nome: string; destino: string; ativo: boolean };
type Categoria = { id: string; nome: string; familia: string; ativo: boolean };
type Acao = { tipo: "salvar"; id?: string; nome: string; familia: string }
  | { tipo: "status"; categoria: Categoria }
  | { tipo: "excluir"; id: string };

const endpointTipos = "/chassi-tipos-aplicacao";
const endpointCategorias = "/chassi-categorias";
const destinos: Record<string, string> = {
  CAVALO: "Veículos",
  CARRETA: "Carretas",
  SEM_VINCULO: "Sem vínculo com veículos ou carretas",
};

export default function ChassiCategorias({ gerenciarAplicacoes = false }: { gerenciarAplicacoes?: boolean }) {
  const qc = useQueryClient();
  const endpoint = gerenciarAplicacoes ? endpointTipos : endpointCategorias;
  const tipos = useQuery({ queryKey: ["chassi-tipos-aplicacao"], queryFn: () => apiGet<TipoAplicacao[]>(endpointTipos) });
  const categorias = useQuery({
    queryKey: ["chassi-categorias"],
    queryFn: () => apiGet<Categoria[]>(endpointCategorias),
    enabled: !gerenciarAplicacoes,
  });
  const lista = gerenciarAplicacoes ? tipos : categorias;
  const registros = gerenciarAplicacoes
    ? tipos.data?.map((tipo) => ({ ...tipo, familia: tipo.destino }))
    : categorias.data;
  const singular = gerenciarAplicacoes ? "tipo de aplicação" : "categoria";
  const [form, setForm] = useState<{ id?: string; nome: string; familia: string } | null>(null);
  const opcoes = gerenciarAplicacoes
    ? Object.entries(destinos).map(([id, nome]) => ({ id, nome }))
    : (tipos.data ?? []).filter((tipo) => tipo.ativo || (form?.id && tipo.id === form.familia))
        .map((tipo) => ({ id: tipo.id, nome: tipo.ativo ? tipo.nome : `${tipo.nome} (inativo)` }));
  if (form?.id && form.familia && !opcoes.some((opcao) => opcao.id === form.familia)) {
    opcoes.push({ id: form.familia, nome: "Tipo de aplicação atual" });
  }
  const [exclusao, setExclusao] = useState<Categoria | null>(null);
  const alterar = useMutation({
    mutationFn: (acao: Acao) => {
      if (acao.tipo === "excluir") return apiDelete(`${endpoint}/${acao.id}`);
      if (acao.tipo === "status") {
        return apiPatch(`${endpoint}/${acao.categoria.id}/status`, { ativo: !acao.categoria.ativo });
      }
      const dados = gerenciarAplicacoes
        ? { nome: acao.nome, destino: acao.familia }
        : { nome: acao.nome, familia: acao.familia };
      return acao.id ? apiPut(`${endpoint}/${acao.id}`, dados) : apiPost(endpoint, dados);
    },
    onSuccess: async () => {
      await Promise.all([
        qc.invalidateQueries({ queryKey: ["chassi-categorias"] }),
        qc.invalidateQueries({ queryKey: ["chassi-tipos-aplicacao"] }),
        qc.invalidateQueries({ queryKey: ["chassi-templates"] }),
      ]);
      setForm(null);
      setExclusao(null);
    },
  });

  const erro = alterar.error ? <p role="alert" className="rounded-md border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-200">{errMsg(alterar.error)}</p> : null;
  const abrir = (categoria?: Categoria) => {
    alterar.reset();
    setForm(categoria ?? { nome: "", familia: gerenciarAplicacoes ? "SEM_VINCULO" : "" });
  };
  const salvar = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (form && form.nome.trim() && form.familia && !alterar.isPending) alterar.mutate({ tipo: "salvar", ...form, nome: form.nome.trim() });
  };

  return (
    <div>
      <PageHeader eyebrow="Cadastros" title={gerenciarAplicacoes ? "Tipos de Aplicação de Chassi" : "Categorias de Chassi"}
        description={gerenciarAplicacoes ? "Gerencie os tipos disponíveis para as categorias de chassi." : "Gerencie as categorias disponíveis no cadastro de templates de chassi."}
        actions={<Button disabled={alterar.isPending} onClick={() => abrir()}><Plus className="size-4" /> {gerenciarAplicacoes ? "Novo tipo de aplicação" : "Nova categoria"}</Button>} />
      {!form && !exclusao && erro}
      <div className="glass overflow-x-auto rounded-2xl border border-slate-800">
        <Table>
          <TableHeader><TableRow><TableHead>Nome</TableHead><TableHead>{gerenciarAplicacoes ? "Compatibilidade com a frota" : "Tipo de aplicação"}</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Ações</TableHead></TableRow></TableHeader>
          <TableBody>
            {lista.isPending && <TableRow><TableCell colSpan={4}>Carregando…</TableCell></TableRow>}
            {lista.isError && <TableRow><TableCell colSpan={4} role="alert">{errMsg(lista.error)}</TableCell></TableRow>}
            {registros?.length === 0 && <TableRow><TableCell colSpan={4}>Nenhum registro cadastrado.</TableCell></TableRow>}
            {registros?.map((categoria) => (
              <TableRow key={categoria.id}>
                <TableCell className="font-medium">{categoria.nome}</TableCell>
                <TableCell>{gerenciarAplicacoes ? destinos[categoria.familia] : tipos.data?.find((tipo) => tipo.id === categoria.familia)?.nome ?? "—"}</TableCell>
                <TableCell>{categoria.ativo ? "Ativa" : "Inativa"}</TableCell>
                <TableCell><div className="flex justify-end gap-1">
                  <Button variant="ghost" size="icon-sm" title="Editar" aria-label={`Editar ${singular}`} disabled={alterar.isPending} onClick={() => abrir(categoria)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button variant="ghost" size="icon-sm" title={categoria.ativo ? "Desativar" : "Ativar"} aria-label={`${categoria.ativo ? "Desativar" : "Ativar"} ${singular}`} disabled={alterar.isPending}
                    onClick={() => alterar.mutate({ tipo: "status", categoria })}>
                    {categoria.ativo ? <Power className="size-4 text-amber-400" /> : <RotateCcw className="size-4 text-emerald-400" />}
                  </Button>
                  <Button variant="ghost" size="icon-sm" title="Excluir" aria-label={`Excluir ${singular}`} disabled={alterar.isPending} onClick={() => { alterar.reset(); setExclusao(categoria); }}><Trash2 className="size-4 text-rose-400" /></Button>
                </div></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      <Dialog open={form !== null} onOpenChange={(open) => { if (!open && !alterar.isPending) setForm(null); }}>
        <DialogContent>
          <DialogHeader><DialogTitle>{form?.id ? `Editar ${singular}` : gerenciarAplicacoes ? "Novo tipo de aplicação" : "Nova categoria"}</DialogTitle></DialogHeader>
          {form && <form onSubmit={salvar} className="grid gap-4">
            <div className="grid gap-2"><Label htmlFor="chassi-categoria-nome">Nome</Label>
              <Input id="chassi-categoria-nome" required maxLength={100} value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} /></div>
            <div className="grid gap-2"><Label htmlFor="chassi-categoria-familia">{gerenciarAplicacoes ? "Compatibilidade com a frota" : "Tipo de aplicação"}</Label>
              <select id="chassi-categoria-familia" className="h-9 rounded-md border border-slate-700 bg-slate-900 px-3" required
                value={form.familia} onChange={(e) => setForm({ ...form, familia: e.target.value })}>
                {!gerenciarAplicacoes && <option value="">Selecione um tipo de aplicação</option>}
                {opcoes.map((opcao) => <option key={opcao.id} value={opcao.id}>{opcao.nome}</option>)}
              </select>
              {!gerenciarAplicacoes && tipos.isError && <p role="alert">{errMsg(tipos.error)}</p>}
            </div>
            {erro}
            <DialogFooter><Button type="button" variant="outline" disabled={alterar.isPending} onClick={() => setForm(null)}>Cancelar</Button>
              <Button type="submit" disabled={alterar.isPending || !form.nome.trim() || !form.familia}>Salvar</Button></DialogFooter>
          </form>}
        </DialogContent>
      </Dialog>
      <Dialog open={exclusao !== null} onOpenChange={(open) => { if (!open && !alterar.isPending) setExclusao(null); }}>
        <DialogContent>
          <DialogHeader><DialogTitle>Excluir {singular}?</DialogTitle></DialogHeader>
          <p className="text-sm">Confirme a exclusão definitiva de “{exclusao?.nome}”.</p>
          {erro}
          <DialogFooter><Button variant="outline" disabled={alterar.isPending} onClick={() => setExclusao(null)}>Cancelar</Button>
            <Button variant="destructive" disabled={!exclusao || alterar.isPending} onClick={() => exclusao && alterar.mutate({ tipo: "excluir", id: exclusao.id })}>Excluir</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
