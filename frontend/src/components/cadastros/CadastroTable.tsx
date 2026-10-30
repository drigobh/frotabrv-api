import { useMemo, useState, useEffect, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Check, Pencil, Plus, Power, RotateCcw, Search, X } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPatch, apiPost, apiPut } from "@/lib/api";
import { errMsg } from "@/lib/format";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { PageHeader } from "@/components/common/PageHeader";
import { StatusBadge } from "@/components/common/StatusBadge";

export interface CadastroRow {
  id: string;
  ativo: boolean;
  acoplado: boolean;
}

export interface ColumnDef<T> {
  key: keyof T & string;
  label: string;
  type?: "text" | "number" | "date" | "email";
  mono?: boolean;
  required?: boolean;
  placeholder?: string;
  options?: string[];
  fetchOptions?: { endpoint: string; labelKey: string; filterKey?: string; filterValue?: string; valueKey?: string };
  defaultValue?: string;
  format?: (row: T) => ReactNode;
}

interface Props<T extends CadastroRow> {
  title: string;
  description: string;
  endpoint: string;
  queryKey: string;
  entityLabel: string;
  testPrefix: string;
  columns: ColumnDef<T>[];
  searchKeys: (keyof T & string)[];
}

type FormValues = Record<string, string>;

function emptyValues<T>(cols: ColumnDef<T>[]): FormValues {
  return Object.fromEntries(cols.map((c) => [c.key, c.defaultValue ?? ""]));
}

function rowValues<T>(row: T, cols: ColumnDef<T>[]): FormValues {
  const r = row as unknown as Record<string, unknown>;
  return Object.fromEntries(cols.map((c) => [c.key, r[c.key] == null ? "" : String(r[c.key])]));
}

function toPayload<T>(v: FormValues, cols: ColumnDef<T>[]): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const c of cols) {
    const raw = (v[c.key] ?? "").trim();
    out[c.key] = c.type === "number" ? Number(raw.replace(",", ".") || 0) : c.type === "date" ? raw || null : raw;
  }
  return out;
}

function missingRequired<T>(v: FormValues, cols: ColumnDef<T>[]): string | null {
  const c = cols.find((col) => col.required && !(v[col.key] ?? "").trim());
  return c ? `Preencha o campo "${c.label}"` : null;
}

function FieldInput<T>({ col, value, onChange, testId }: { col: ColumnDef<T>; value: string; onChange: (v: string) => void; testId: string }) {
  const [dynamicOptions, setDynamicOptions] = useState<{ value: string; label: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (col.fetchOptions) {
      setLoading(true);
      apiGet<any[]>(col.fetchOptions.endpoint)
        .then((data) => {
          let filtered = data;
          if (col.fetchOptions?.filterKey && col.fetchOptions?.filterValue) {
            filtered = data.filter((item: any) => item[col.fetchOptions!.filterKey!] === col.fetchOptions!.filterValue);
          }
          const opts = filtered.map((item: any) => ({
            value: item[col.fetchOptions!.valueKey || "id"],
            label: item[col.fetchOptions!.labelKey] || item[col.fetchOptions!.valueKey || "id"]
          }));
          setDynamicOptions(opts);
        })
        .catch(() => setDynamicOptions([]))
        .finally(() => setLoading(false));
    }
  }, [col.fetchOptions]);

  if (col.fetchOptions) {
    return (
      <FieldSelect 
        value={value} 
        onChange={onChange} 
        options={loading ? [{ value: "", label: "Carregando..." }] : dynamicOptions} 
        placeholder={col.placeholder}
        testId={testId} 
      />
    );
  }

  if (col.options) {
    return (
      <FieldSelect value={value} onChange={onChange} options={col.options.map((o) => ({ value: o, label: o }))} testId={testId} />
    );
  }
  return (
    <Input
      type={col.type ?? "text"}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={col.placeholder}
      className={cn("h-8", col.mono && "font-mono uppercase")}
      data-testid={testId}
    />
  );
}

export function CadastroTable<T extends CadastroRow>({ title, description, endpoint, queryKey, entityLabel, testPrefix, columns, searchKeys }: Props<T>) {
  const qc = useQueryClient();
  const [inativos, setInativos] = useState(false);
  const [busca, setBusca] = useState("");
  const [editId, setEditId] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<FormValues>({});
  const [pulseId, setPulseId] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [createValues, setCreateValues] = useState<FormValues>(() => emptyValues(columns));

  const list = useQuery({ queryKey: [queryKey, inativos], queryFn: () => apiGet<T[]>(`${endpoint}?inativos=${inativos}`) });

  const invalidate = () => {
    void qc.invalidateQueries({ queryKey: [queryKey] });
    void qc.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const createMut = useMutation({
    mutationFn: (v: FormValues) => apiPost<T>(endpoint, toPayload(v, columns)),
    onSuccess: () => {
      toast.success(`${entityLabel[0].toUpperCase()}${entityLabel.slice(1)} cadastrado(a)`);
      setCreateOpen(false);
      setCreateValues(emptyValues(columns));
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const updateMut = useMutation({
    mutationFn: ({ id, v }: { id: string; v: FormValues }) => apiPut<T>(`${endpoint}/${id}`, toPayload(v, columns)),
    onSuccess: (_d, vars) => {
      toast.success("Alterações salvas");
      setEditId(null);
      setPulseId(vars.id);
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const statusMut = useMutation({
    mutationFn: ({ id, ativo }: { id: string; ativo: boolean }) => apiPatch<T>(`${endpoint}/${id}/status`, { ativo }),
    onSuccess: (_d, vars) => {
      toast.success(vars.ativo ? "Registro reativado" : "Registro inativado");
      invalidate();
    },
    onError: (e) => toast.error(errMsg(e)),
  });

  const rows = useMemo(() => {
    const data = list.isError ? [] : (list.data ?? []);
    const q = busca.trim().toLowerCase();
    if (!q) return data;
    return data.filter((r) =>
      searchKeys.some((k) => String((r as unknown as Record<string, unknown>)[k] ?? "").toLowerCase().includes(q)),
    );
  }, [list.data, list.isError, busca, searchKeys]);

  const submitCreate = () => {
    const err = missingRequired(createValues, columns);
    if (err) return void toast.error(err);
    createMut.mutate(createValues);
  };

  const saveEdit = () => {
    if (!editId) return;
    const err = missingRequired(editValues, columns);
    if (err) return void toast.error(err);
    updateMut.mutate({ id: editId, v: editValues });
  };

  return (
    <div>
      <PageHeader
        eyebrow="Cadastros"
        title={title}
        description={description}
        actions={
          <>
            <div className="relative">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-slate-500" />
              <Input
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                placeholder="Buscar…"
                className="w-52 pl-8"
                data-testid={`${testPrefix}-search-input`}
              />
            </div>
            <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-slate-800 px-3 py-1.5 text-sm text-slate-300">
              <Checkbox checked={inativos} onCheckedChange={(c) => setInativos(Boolean(c))} data-testid={`${testPrefix}-toggle-inativos`} />
              Mostrar inativos
            </label>
            <Button onClick={() => setCreateOpen(true)} data-testid={`${testPrefix}-new-button`}>
              <Plus className="size-4" /> Novo {entityLabel}
            </Button>
          </>
        }
      />

      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid={`${testPrefix}-table`}>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {columns.map((c) => (
                <TableHead key={c.key} className="text-xs uppercase tracking-wider text-slate-500">{c.label}</TableHead>
              ))}
              <TableHead className="text-xs uppercase tracking-wider text-slate-500">Status</TableHead>
              <TableHead className="text-right text-xs uppercase tracking-wider text-slate-500">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {list.isPending && (
              <TableRow><TableCell colSpan={columns.length + 2} className="py-10 text-center text-slate-500">Carregando…</TableCell></TableRow>
            )}
            {!list.isPending && rows.length === 0 && (
              <TableRow>
                <TableCell colSpan={columns.length + 2} className="py-10 text-center text-slate-500" data-testid={`${testPrefix}-empty`}>
                  {list.isError ? "Não foi possível carregar os dados." : "Nenhum registro encontrado."}
                </TableCell>
              </TableRow>
            )}
            {rows.map((row) => {
              const editing = editId === row.id;
              const r = row as unknown as Record<string, unknown>;
              return (
                <TableRow
                  key={row.id}
                  data-testid={`${testPrefix}-row-${row.id}`}
                  onAnimationEnd={() => setPulseId(null)}
                  className={cn(
                    "border-slate-800/70 transition-colors",
                    !row.ativo && "opacity-60",
                    editing && "bg-sky-950/30 outline outline-1 -outline-offset-1 outline-emerald-500/50",
                    pulseId === row.id && "animate-save-pulse",
                  )}
                >
                  {columns.map((c) => (
                    <TableCell key={c.key} className={cn("py-2.5", c.mono && "font-mono")}>
                      {editing ? (
                        <FieldInput
                          col={c}
                          value={editValues[c.key] ?? ""}
                          onChange={(v) => setEditValues((s) => ({ ...s, [c.key]: v }))}
                          testId={`${testPrefix}-inline-${c.key}`}
                        />
                      ) : c.format ? (
                        c.format(row)
                      ) : (
                        <span className={cn(c.key === "observacoes" && "text-slate-400")}>{String(r[c.key] ?? "") || "—"}</span>
                      )}
                    </TableCell>
                  ))}
                  <TableCell>
                    <div className="flex gap-1.5">
                      <StatusBadge tone={row.ativo ? "ativo" : "inativo"} testId={`${testPrefix}-status-${row.id}`}>
                        {row.ativo ? "Ativo" : "Inativo"}
                      </StatusBadge>
                      {row.acoplado && <StatusBadge tone="acoplado">Acoplado</StatusBadge>}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    {editing ? (
                      <div className="flex justify-end gap-1">
                        <Button size="icon-sm" className="bg-emerald-600 hover:bg-emerald-500" onClick={saveEdit} disabled={updateMut.isPending} aria-label="Confirmar" data-testid={`${testPrefix}-inline-confirm`}>
                          <Check className="size-4" />
                        </Button>
                        <Button size="icon-sm" variant="outline" onClick={() => setEditId(null)} aria-label="Cancelar" data-testid={`${testPrefix}-inline-cancel`}>
                          <X className="size-4" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex justify-end gap-1">
                        <Button
                          size="icon-sm"
                          variant="ghost"
                          onClick={() => { setEditId(row.id); setEditValues(rowValues(row, columns)); }}
                          aria-label="Editar"
                          data-testid={`${testPrefix}-edit-${row.id}`}
                        >
                          <Pencil className="size-4" />
                        </Button>
                        <Button
                          size="icon-sm"
                          variant="ghost"
                          className={row.ativo ? "text-amber-300 hover:text-amber-200" : "text-emerald-300 hover:text-emerald-200"}
                          disabled={statusMut.isPending || (row.ativo && row.acoplado)}
                          title={row.ativo && row.acoplado ? "Libere o acoplamento antes de inativar" : row.ativo ? "Inativar" : "Reativar"}
                          onClick={() => statusMut.mutate({ id: row.id, ativo: !row.ativo })}
                          data-testid={`${testPrefix}-toggle-status-${row.id}`}
                        >
                          {row.ativo ? <Power className="size-4" /> : <RotateCcw className="size-4" />}
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
      <p className="mt-3 text-xs text-slate-500" data-testid={`${testPrefix}-count`}>{rows.length} registro(s)</p>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent data-testid={`${testPrefix}-create-dialog`}>
          <DialogHeader>
            <DialogTitle>Novo {entityLabel}</DialogTitle>
          </DialogHeader>
          <form
            className="grid gap-3"
            onSubmit={(e) => { e.preventDefault(); submitCreate(); }}
          >
            {columns.map((c) => (
              <div key={c.key} className="grid gap-1.5">
                <Label htmlFor={`${testPrefix}-form-${c.key}`}>{c.label}{c.required && " *"}</Label>
                <FieldInput
                  col={c}
                  value={createValues[c.key] ?? ""}
                  onChange={(v) => setCreateValues((s) => ({ ...s, [c.key]: v }))}
                  testId={`${testPrefix}-form-${c.key}`}
                />
              </div>
            ))}
            <DialogFooter className="mt-2">
              <Button type="submit" disabled={createMut.isPending} data-testid={`${testPrefix}-form-submit`}>
                Salvar
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
