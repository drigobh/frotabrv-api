import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Power, RotateCcw, Search, Shield, X, Check, User, Key, Lock, Users, Bell, UserCheck, ShieldAlert, ShieldCheck, UserX } from "lucide-react";
import { apiGet, apiPatch, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function Usuarios() {
  const qc = useQueryClient();
  const [busca, setBusca] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<any>(null);
  const [form, setForm] = useState<any>({ 
    nome: "", email: "", perfil_id: "", setor: "", cargo: "", telefone: "", whatsapp: "", foto_url: "", senha: "",
    notificacoes: { manutencao: true, documentos: true, pneus: true, resumo_semanal: false }
  });

  const { data: perfis = [] } = useQuery({ queryKey: ["perfis"], queryFn: () => apiGet<any[]>("/perfis") });
  const { data: usuarios = [], isLoading } = useQuery({ queryKey: ["usuarios"], queryFn: () => apiGet<any[]>("/usuarios") });

  const toggleStatus = useMutation({
    mutationFn: ({ id, ativo }: { id: string, ativo: boolean }) => apiPatch(`/usuarios/${id}/status`, { ativo }),
    onSuccess: () => { toast.success("Status alterado!"); qc.invalidateQueries({ queryKey: ["usuarios"] }); }
  });

  const destravar = useMutation({
    mutationFn: (id: string) => apiPatch(`/usuarios/${id}/destravar`, {}),
    onSuccess: () => {
      toast.success("Usuário destravado com sucesso!");
      qc.invalidateQueries({ queryKey: ["usuarios"] });
    }
  });

  const salvar = useMutation({
    mutationFn: (payload: any) => editando ? apiPut(`/usuarios/${editando.id}`, payload) : apiPost("/usuarios", payload),
    onSuccess: () => {
      toast.success(editando ? "Usuário atualizado!" : "Usuário criado!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["usuarios"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar.")
  });

  const abrirNovo = () => {
    setEditando(null);
    setForm({ nome: "", email: "", perfil_id: "", setor: "", cargo: "", telefone: "", whatsapp: "", foto_url: "", senha: "", notificacoes: { manutencao: true, documentos: true, pneus: true, resumo_semanal: false } });
    setModalOpen(true);
  };

  const abrirEdicao = (u: any) => {
    setEditando(u);
    setForm({ 
      nome: u.nome || "", email: u.email || "", perfil_id: u.perfil_id || "", setor: u.setor || "", cargo: u.cargo || "", 
      telefone: u.telefone || "", whatsapp: u.whatsapp || "", foto_url: u.foto_url || "", senha: "",
      notificacoes: u.notificacoes || { manutencao: true, documentos: true, pneus: true, resumo_semanal: false }
    });
    setModalOpen(true);
  };

  // KPIs
  const total = usuarios.length;
  const ativos = usuarios.filter((u: any) => u.ativo).length;
  const inativos = total - ativos;
  const admins = usuarios.filter((u: any) => u.perfil_id === "perfil-admin").length;
  const com2FA = usuarios.filter((u: any) => u.two_factor_enabled).length;
  const semFoto = usuarios.filter((u: any) => !u.foto_url).length;

  const filtrados = usuarios.filter((u: any) => 
    (u.nome || "").toLowerCase().includes(busca.toLowerCase()) ||
    (u.email || "").toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Usuários"
        description="Gestão completa de acessos, perfis e segurança."
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input placeholder="Buscar usuário..." value={busca} onChange={(e) => setBusca(e.target.value)} className="pl-9 h-9 w-64" />
            </div>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">
              <Plus className="size-4 mr-2" /> Novo Usuário
            </Button>
          </div>
        }
      />

      {/* Cards de KPI */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Total</p>
            <p className="text-lg font-bold text-slate-100">{total}</p>
          </div>
          <Users className="size-5 text-sky-400" />
        </div>
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Ativos</p>
            <p className="text-lg font-bold text-emerald-400">{ativos}</p>
          </div>
          <UserCheck className="size-5 text-emerald-400" />
        </div>
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Inativos</p>
            <p className="text-lg font-bold text-rose-400">{inativos}</p>
          </div>
          <UserX className="size-5 text-rose-400" />
        </div>
        <div className="glass p-3 rounded-lg border border-slate-800 flex items-center justify-between">
          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium">Administradores</p>
            <p className="text-lg font-bold text-amber-400">{admins}</p>
          </div>
          <ShieldAlert className="size-5 text-amber-400" />
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-500">
              <th className="px-5 py-3 font-medium">Usuário</th>
              <th className="px-3 py-3 font-medium">Setor / Cargo</th>
              <th className="px-3 py-3 font-medium">Perfil</th>
              <th className="px-3 py-3 font-medium text-center">2FA</th>
              <th className="px-3 py-3 font-medium">Cadastro</th>
              <th className="px-3 py-3 font-medium">Último Acesso</th>
              <th className="px-3 py-3 font-medium">Status</th>
              <th className="px-3 py-3 text-right font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {isLoading ? (
              <tr><td colSpan={8} className="p-8 text-center text-slate-500">Carregando...</td></tr>
            ) : filtrados.length === 0 ? (
              <tr><td colSpan={8} className="p-8 text-center text-slate-500">Nenhum usuário encontrado.</td></tr>
            ) : (
              filtrados.map((u: any) => (
                <tr key={u.id} className={cn("hover:bg-slate-800/30 transition-colors", !u.ativo && "opacity-60")}>
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-3">
                      <div className="size-9 rounded-full bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-300 overflow-hidden">
                        {u.foto_url ? <img src={u.foto_url} alt={u.nome} className="size-full object-cover" /> : (u.nome?.charAt(0) || "U")}
                      </div>
                      <div>
                        <p className="font-medium text-slate-200">{u.nome}</p>
                        <p className="text-xs text-slate-400">{u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-3">
                    <p className="text-slate-300">{u.setor || "—"}</p>
                    <p className="text-xs text-slate-500">{u.cargo || "—"}</p>
                  </td>
                  <td className="px-3 py-3">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-sky-500/10 text-sky-400">
                      <Shield className="size-3" /> {perfis.find((p: any) => p.id === u.perfil_id)?.nome || "Sem perfil"}
                    </span>
                  </td>
                  
                  <td className="px-3 py-3 text-center">
                    {u.two_factor_enabled ? (
                      <span className="text-emerald-500" title="Ativo"><ShieldCheck className="size-4 mx-auto" /></span>
                    ) : (
                      <span className="text-rose-500" title="Inativo"><ShieldAlert className="size-4 mx-auto" /></span>
                    )}
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-400 font-mono">
                    {u.data_cadastro ? new Date(u.data_cadastro).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "—"}
                  </td>
                  <td className="px-3 py-3 text-xs text-slate-400 font-mono">
                    {u.ultimo_acesso ? new Date(u.ultimo_acesso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "—"}
                  </td>
                  <td className="px-3 py-3">
                    <Badge tone={u.ativo ? "ativo" : "inativo"}>{u.ativo ? "Ativo" : "Inativo"}</Badge>
                  </td>
                  <td className="px-3 py-3 text-right flex justify-end gap-1">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(u)}><Pencil className="size-4 text-sky-400" /></Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => destravar.mutate(u.id)} title="Destravar Login">
                      <ShieldAlert className="size-4 text-amber-400" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => toggleStatus.mutate({ id: u.id, ativo: !u.ativo })} className={u.ativo ? "text-amber-400" : "text-emerald-400"}>
                      {u.ativo ? <Power className="size-4" /> : <RotateCcw className="size-4" />}
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Completo */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-3xl flex flex-col max-h-[90vh]">
            <div className="flex justify-between items-center border-b border-slate-800 px-6 py-4 shrink-0">
              <div>
                <h2 className="text-lg font-bold text-slate-100">{editando ? "Editar Usuário" : "Novo Usuário"}</h2>
                <p className="text-xs text-slate-400 mt-1">Preencha as informações e defina o perfil de acesso.</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}><X className="size-5" /></Button>
            </div>

            <div className="p-6 space-y-6 overflow-y-auto flex-1">
              {/* Dados Pessoais */}
              <div>
                <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                  <User className="size-4 text-sky-400" /> Dados Pessoais
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="grid gap-1.5 md:col-span-2">
                    <Label className="text-xs text-slate-400">Nome Completo *</Label>
                    <Input value={form.nome} onChange={(e) => setForm((s: any) => ({ ...s, nome: e.target.value }))} />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Foto (URL)</Label>
                    <Input value={form.foto_url} onChange={(e) => setForm((s: any) => ({ ...s, foto_url: e.target.value }))} placeholder="https://..." />
                  </div>
                  <div className="grid gap-1.5 md:col-span-2">
                    <Label className="text-xs text-slate-400">E-mail *</Label>
                    <Input type="email" value={form.email} onChange={(e) => setForm((s: any) => ({ ...s, email: e.target.value }))} />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Telefone</Label>
                    <Input value={form.telefone} onChange={(e) => setForm((s: any) => ({ ...s, telefone: e.target.value }))} />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Setor</Label>
                    <Input value={form.setor} onChange={(e) => setForm((s: any) => ({ ...s, setor: e.target.value }))} />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Cargo</Label>
                    <Input value={form.cargo} onChange={(e) => setForm((s: any) => ({ ...s, cargo: e.target.value }))} />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">WhatsApp</Label>
                    <Input value={form.whatsapp} onChange={(e) => setForm((s: any) => ({ ...s, whatsapp: e.target.value }))} />
                  </div>
                </div>
              </div>

              {/* Segurança */}
              <div>
                <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                  <Lock className="size-4 text-amber-400" /> Segurança e Acesso
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Perfil de Acesso (RBAC) *</Label>
                    
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Ativação (Automático)</Label>
                    <Input 
                      value={editando && editando.data_cadastro ? new Date(editando.data_cadastro).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : (new Date().toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }))} 
                      disabled 
                      className="bg-slate-900/50 border-slate-800 text-slate-400 font-mono" 
                    />
                  </div>
                  <div className="grid gap-1.5">
                    <select value={form.perfil_id} onChange={(e) => setForm((s: any) => ({ ...s, perfil_id: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="">Selecione um perfil...</option>
                      {perfis.map((p: any) => <option key={p.id} value={p.id}>{p.nome}</option>)}
                    </select>
                  </div>
                  {!editando && (
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Senha Inicial *</Label>
                      <Input type="password" value={form.senha} onChange={(e) => setForm((s: any) => ({ ...s, senha: e.target.value }))} />
                    </div>
                  )}
                  
                </div>
              </div>

              {/* Notificações */}
              <div>
                <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                  <Bell className="size-4 text-sky-400" /> Notificações
                </h3>
                <div className="space-y-3">
                  {[
                    { key: "manutencao", label: "Alertas de Manutenção", desc: "Quando uma OS for aberta." },
                    { key: "documentos", label: "Vencimento de Documentos", desc: "CRLV e CNH a vencer." },
                    { key: "pneus", label: "Pneus Críticos", desc: "Sulco abaixo de 3mm." },
                    { key: "resumo_semanal", label: "Resumo Semanal", desc: "Relatório de custos toda segunda." },
                  ].map((n) => (
                    <label key={n.key} className="flex items-center justify-between p-3 rounded-lg border border-slate-800 bg-slate-900/30 cursor-pointer">
                      <div>
                        <p className="text-sm font-medium text-slate-200">{n.label}</p>
                        <p className="text-xs text-slate-500">{n.desc}</p>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={form.notificacoes?.[n.key] || false} 
                        onChange={(e) => setForm((s: any) => ({ ...s, notificacoes: { ...s.notificacoes, [n.key]: e.target.checked } }))}
                        className="size-4 rounded border-slate-600 text-sky-500 focus:ring-sky-500/20"
                      />
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 border-t border-slate-800 px-6 py-4 shrink-0">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button onClick={() => salvar.mutate(form)} disabled={salvar.isPending || !form.nome || !form.email || !form.perfil_id} className="bg-emerald-600 hover:bg-emerald-500 text-white px-6">
                <Check className="size-4 mr-2" /> Salvar Usuário
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
