import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, ShieldCheck, X, Check, Lock } from "lucide-react";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const MODULOS = [
  { nome: "Dashboard", acoes: ["Ver"] },
  { nome: "Abastecimentos", acoes: ["Ver", "Criar", "Editar", "Excluir"] },
  { nome: "Pneus", acoes: ["Ver", "Criar", "Editar", "Excluir"] },
  { nome: "Manutenção", acoes: ["Ver", "Criar", "Editar", "Aprovar"] },
  { nome: "Frota", acoes: ["Ver", "Criar", "Editar", "Excluir"] },
  { nome: "Financeiro", acoes: ["Ver", "Criar", "Editar", "Aprovar"] },
  { nome: "Relatórios", acoes: ["Ver", "Exportar"] },
  { nome: "Cadastros", acoes: ["Ver", "Criar", "Editar", "Excluir"] },
  { nome: "Administração", acoes: ["Ver", "Criar", "Editar", "Excluir"] },
];

export default function Perfis() {
  const qc = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [editando, setEditando] = useState<any>(null);
  const [form, setForm] = useState<any>({ nome: "", descricao: "", permissoes: [] });

  const { data: perfis = [], isLoading } = useQuery({ 
    queryKey: ["perfis"], 
    queryFn: () => apiGet<any[]>("/perfis") 
  });

  const salvar = useMutation({
    mutationFn: (payload: any) => {
      if (editando) return apiPut(`/perfis/${editando.id}`, payload);
      return apiPost("/perfis", payload);
    },
    onSuccess: () => {
      toast.success(editando ? "Perfil atualizado!" : "Perfil criado!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["perfis"] });
    }
  });

  const excluir = useMutation({
    mutationFn: (id: string) => apiDelete(`/perfis/${id}`),
    onSuccess: () => {
      toast.success("Perfil removido.");
      qc.invalidateQueries({ queryKey: ["perfis"] });
    }
  });

  const abrirNovo = () => {
    setEditando(null);
    setForm({ nome: "", descricao: "", permissoes: [] });
    setModalOpen(true);
  };

  const abrirEdicao = (p: any) => {
    setEditando(p);
    setForm({ nome: p.nome, descricao: p.descricao || "", permissoes: Array.isArray(p.permissoes) ? p.permissoes : [] });
    setModalOpen(true);
  };

  const togglePermissao = (modulo: string, acao: string) => {
    const chave = `${modulo}:${acao}`;
    setForm((s: any) => ({
      ...s,
      permissoes: (Array.isArray(s.permissoes) ? s.permissoes : []).includes(chave)
        ? s.permissoes.filter((p: string) => p !== chave)
        : [...s.permissoes, chave]
    }));
  };

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Perfis de Acesso (RBAC)"
        description="Defina os perfis e as permissões granulares. Os usuários herdam as regras do seu perfil."
        actions={
          <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">
            <Plus className="size-4 mr-2" /> Novo Perfil
          </Button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          <p className="text-slate-500">Carregando perfis...</p>
        ) : perfis.length === 0 ? (
          <p className="text-slate-500">Nenhum perfil criado. Crie um para começar.</p>
        ) : (
          perfis.map((p: any) => (
            <div key={p.id} className="glass p-5 rounded-2xl border border-slate-800 flex flex-col">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="size-5 text-sky-400" />
                  <h3 className="font-bold text-slate-100">{p.nome}</h3>
                </div>
                <div className="flex gap-1">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(p)}>
                    <Pencil className="size-3.5 text-slate-400" />
                  </Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => excluir.mutate(p.id)}>
                    <Trash2 className="size-3.5 text-rose-400" />
                  </Button>
                </div>
              </div>
              <p className="text-xs text-slate-400 mb-4 line-clamp-2">{p.descricao || "Sem descrição."}</p>
              <div className="flex flex-wrap gap-1 mt-auto">
                <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-400 font-medium">
                  {p.permissoes?.length || 0} permissões
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-3xl flex flex-col">
            <div className="flex justify-between items-center border-b border-slate-800 px-6 py-4">
              <div>
                <h2 className="text-lg font-bold text-slate-100">{editando ? "Editar Perfil" : "Novo Perfil"}</h2>
                <p className="text-xs text-slate-400 mt-1">Defina o nome e as permissões do perfil.</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}>
                <X className="size-5" />
              </Button>
            </div>

            <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Nome do Perfil *</Label>
                  <Input value={form.nome} onChange={(e) => setForm((s: any) => ({ ...s, nome: e.target.value }))} placeholder="Ex: Gestor de Frota" />
                </div>
                <div className="grid gap-1.5">
                  
                  <Input value={form.descricao} onChange={(e) => setForm((s: any) => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Acesso total ao módulo de frotas" />
                </div>
              </div>

              <div>
                <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                  <Lock className="size-4 text-amber-400" /> Matriz de Permissões
                </h3>
                <div className="space-y-2">
                  {MODULOS.map((mod) => (
                    <div key={mod.nome} className="rounded-lg border border-slate-800 p-3">
                      <p className="text-sm font-medium text-slate-200 mb-2">{mod.nome}</p>
                      <div className="flex flex-wrap gap-2">
                        {mod.acoes.map((acao) => {
                          const ativo = form.permissoes.includes(`${mod.nome}:${acao}`);
                          return (
                            <button
                              key={acao}
                              onClick={() => togglePermissao(mod.nome, acao)}
                              className={cn(
                                "px-3 py-1 text-xs rounded-md border transition-colors",
                                ativo ? "bg-sky-500/20 border-sky-500/50 text-sky-400" : "border-slate-700 text-slate-500 hover:border-slate-600"
                              )}
                            >
                              {ativo && <Check className="size-3 inline mr-1" />}
                              {acao}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 border-t border-slate-800 px-6 py-4">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button 
                onClick={() => salvar.mutate(form)} 
                disabled={!form.nome}
                className="bg-emerald-600 hover:bg-emerald-500 text-white px-6"
              >
                Salvar Perfil
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
