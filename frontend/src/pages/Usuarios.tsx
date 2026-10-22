import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KeyRound, Plus, Power, RotateCcw } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut } from "@/lib/api";
import { dataHoraBR, errMsg } from "@/lib/format";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PageHeader } from "@/components/common/PageHeader";
import { FieldSelect } from "@/components/common/FieldSelect";
import { StatusBadge } from "@/components/common/StatusBadge";
import { AdminOnly } from "@/components/layout/AdminOnly";
import { useMe } from "@/hooks/useSession";
import type { OkOut, Perfil, Usuario } from "@/types/auth";

const PERFIS = [{ value: "admin", label: "Administrador" }, { value: "operador", label: "Operador" }];

function UsuariosConteudo() {
  const qc = useQueryClient();
  const { data: me } = useMe();
  const q = useQuery({ queryKey: ["usuarios"], queryFn: () => apiGet<Usuario[]>("/usuarios") });
  const [novoOpen, setNovoOpen] = useState(false);
  const [novo, setNovo] = useState({ nome: "", email: "", senha: "", perfil: "operador" as Perfil });
  const [resetUser, setResetUser] = useState<Usuario | null>(null);
  const [novaSenha, setNovaSenha] = useState("");

  const invalidate = () => void qc.invalidateQueries({ queryKey: ["usuarios"] });
  const onError = (e: unknown) => toast.error(errMsg(e));

  const criar = useMutation({
    mutationFn: () => apiPost<Usuario>("/usuarios", novo),
    onSuccess: () => { toast.success("Usuário criado"); setNovoOpen(false); setNovo({ nome: "", email: "", senha: "", perfil: "operador" }); invalidate(); },
    onError,
  });
  const editar = useMutation({
    mutationFn: (u: Usuario) => apiPut<Usuario>(`/usuarios/${u.id}`, { nome: u.nome, perfil: u.perfil, ativo: u.ativo }),
    onSuccess: () => { toast.success("Usuário atualizado"); invalidate(); },
    onError,
  });
  const reset = useMutation({
    mutationFn: () => apiPost<OkOut>(`/usuarios/${resetUser?.id}/senha`, { senha: novaSenha }),
    onSuccess: () => { toast.success("Senha redefinida"); setResetUser(null); setNovaSenha(""); },
    onError,
  });

  const rows = q.isError ? [] : (q.data ?? []);

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Usuários"
        description="Administradores têm acesso total. Operadores cadastram e operam, mas não excluem registros nem gerenciam usuários."
        actions={<Button onClick={() => setNovoOpen(true)} data-testid="usuario-new-button"><Plus className="size-4" /> Novo usuário</Button>}
      />
      <div className="glass overflow-hidden rounded-2xl">
        <Table data-testid="usuario-table">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Nome", "E-mail", "Perfil", "2FA", "Status", "Criado em", ""].map((h) => (
                <TableHead key={h} className="text-xs uppercase tracking-wider text-slate-500">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((u) => {
              const self = u.id === me?.id;
              return (
                <TableRow key={u.id} className="border-slate-800/70" data-testid={`usuario-row-${u.email}`}>
                  <TableCell className="font-medium">{u.nome}{self && <span className="ml-2 text-xs text-sky-400">(você)</span>}</TableCell>
                  <TableCell className="text-slate-300">{u.email}</TableCell>
                  <TableCell className="w-44">
                    {self ? (
                      <span className="text-sm">Administrador</span>
                    ) : (
                      <FieldSelect value={u.perfil} onChange={(v) => editar.mutate({ ...u, perfil: v as Perfil })} options={PERFIS} testId={`usuario-perfil-${u.email}`} />
                    )}
                  </TableCell>
                  <TableCell>{u.totp_enabled ? <StatusBadge tone="ativo">Ativo</StatusBadge> : <StatusBadge tone="inativo">Off</StatusBadge>}</TableCell>
                  <TableCell><StatusBadge tone={u.ativo ? "ativo" : "inativo"}>{u.ativo ? "Ativo" : "Inativo"}</StatusBadge></TableCell>
                  <TableCell className="text-sm text-slate-400">{dataHoraBR(u.created_at)}</TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button size="icon-sm" variant="ghost" onClick={() => setResetUser(u)} aria-label="Redefinir senha" title="Redefinir senha" data-testid={`usuario-reset-${u.email}`}>
                        <KeyRound className="size-4" />
                      </Button>
                      {!self && (
                        <Button
                          size="icon-sm"
                          variant="ghost"
                          className={u.ativo ? "text-amber-300" : "text-emerald-300"}
                          onClick={() => editar.mutate({ ...u, ativo: !u.ativo })}
                          title={u.ativo ? "Inativar" : "Reativar"}
                          data-testid={`usuario-toggle-${u.email}`}
                        >
                          {u.ativo ? <Power className="size-4" /> : <RotateCcw className="size-4" />}
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <Dialog open={novoOpen} onOpenChange={setNovoOpen}>
        <DialogContent data-testid="usuario-dialog">
          <DialogHeader><DialogTitle>Novo usuário</DialogTitle></DialogHeader>
          <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); criar.mutate(); }}>
            <div className="grid gap-1.5"><Label htmlFor="u-nome">Nome *</Label><Input id="u-nome" value={novo.nome} onChange={(e) => setNovo((s) => ({ ...s, nome: e.target.value }))} required data-testid="usuario-form-nome" /></div>
            <div className="grid gap-1.5"><Label htmlFor="u-email">E-mail *</Label><Input id="u-email" type="email" value={novo.email} onChange={(e) => setNovo((s) => ({ ...s, email: e.target.value }))} required data-testid="usuario-form-email" /></div>
            <div className="grid gap-1.5"><Label htmlFor="u-senha">Senha inicial * (mín. 8)</Label><Input id="u-senha" type="password" minLength={8} value={novo.senha} onChange={(e) => setNovo((s) => ({ ...s, senha: e.target.value }))} required data-testid="usuario-form-senha" /></div>
            <div className="grid gap-1.5"><Label>Perfil</Label><FieldSelect value={novo.perfil} onChange={(v) => setNovo((s) => ({ ...s, perfil: v as Perfil }))} options={PERFIS} testId="usuario-form-perfil" /></div>
            <DialogFooter><Button type="submit" disabled={criar.isPending} data-testid="usuario-form-submit">Criar</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={resetUser !== null} onOpenChange={(o) => !o && setResetUser(null)}>
        <DialogContent data-testid="usuario-reset-dialog">
          <DialogHeader><DialogTitle>Redefinir senha de {resetUser?.nome}</DialogTitle></DialogHeader>
          <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); reset.mutate(); }}>
            <Input type="password" minLength={8} placeholder="Nova senha (mín. 8)" value={novaSenha} onChange={(e) => setNovaSenha(e.target.value)} required data-testid="usuario-reset-input" />
            <DialogFooter><Button type="submit" disabled={reset.isPending} data-testid="usuario-reset-submit">Redefinir</Button></DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function Usuarios() {
  return <AdminOnly><UsuariosConteudo /></AdminOnly>;
}
