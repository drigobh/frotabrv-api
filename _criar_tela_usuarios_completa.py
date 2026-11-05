import os
import re

# ==========================================
# 1. FRONTEND: TELA COMPLETA DE USUÁRIOS
# ==========================================
path_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

conteudo = r'''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Power, RotateCcw, Search, Shield, X, Check } from "lucide-react";
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
  const [form, setForm] = useState({ nome: "", email: "", perfil: "Operador", senha: "" });

  const { data: usuarios = [], isLoading } = useQuery({ 
    queryKey: ["usuarios"], 
    queryFn: () => apiGet<any[]>("/usuarios") 
  });

  const toggleStatus = useMutation({
    mutationFn: ({ id, ativo }: { id: string, ativo: boolean }) => 
      apiPatch(`/usuarios/${id}/status`, { ativo }),
    onSuccess: () => {
      toast.success("Status alterado!");
      qc.invalidateQueries({ queryKey: ["usuarios"] });
    }
  });

  const salvar = useMutation({
    mutationFn: (payload: any) => {
      if (editando) return apiPut(`/usuarios/${editando.id}`, payload);
      return apiPost("/usuarios", payload);
    },
    onSuccess: () => {
      toast.success(editando ? "Usuário atualizado!" : "Usuário criado!");
      setModalOpen(false);
      qc.invalidateQueries({ queryKey: ["usuarios"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar.")
  });

  const abrirNovo = () => {
    setEditando(null);
    setForm({ nome: "", email: "", perfil: "Operador", senha: "" });
    setModalOpen(true);
  };

  const abrirEdicao = (u: any) => {
    setEditando(u);
    setForm({ nome: u.nome, email: u.email, perfil: u.perfil || "Operador", senha: "" });
    setModalOpen(true);
  };

  const filtrados = usuarios.filter((u: any) => 
    (u.nome || "").toLowerCase().includes(busca.toLowerCase()) ||
    (u.email || "").toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Usuários"
        description="Gestão de acessos e perfis do sistema."
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
              <Input 
                placeholder="Buscar usuário..." 
                value={busca} 
                onChange={(e) => setBusca(e.target.value)} 
                className="pl-9 h-9 w-64" 
              />
            </div>
            <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500 h-9">
              <Plus className="size-4 mr-2" /> Novo Usuário
            </Button>
          </div>
        }
      />

      <div className="glass rounded-2xl overflow-hidden border border-slate-800">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-[11px] uppercase tracking-wider text-slate-500">
              <th className="px-5 py-3 font-medium">Nome</th>
              <th className="px-3 py-3 font-medium">E-mail</th>
              <th className="px-3 py-3 font-medium">Perfil</th>
              <th className="px-3 py-3 font-medium">Status</th>
              <th className="px-3 py-3 text-right font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {isLoading ? (
              <tr><td colSpan={5} className="p-8 text-center text-slate-500">Carregando usuários...</td></tr>
            ) : filtrados.length === 0 ? (
              <tr><td colSpan={5} className="p-8 text-center text-slate-500">Nenhum usuário encontrado.</td></tr>
            ) : (
              filtrados.map((u: any) => (
                <tr key={u.id} className={cn("hover:bg-slate-800/30 transition-colors", !u.ativo && "opacity-60")}>
                  <td className="px-5 py-3 font-medium text-slate-200">{u.nome}</td>
                  <td className="px-3 py-3 text-slate-400">{u.email}</td>
                  <td className="px-3 py-3">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-sky-500/10 text-sky-400">
                      <Shield className="size-3" /> {u.perfil || "Operador"}
                    </span>
                  </td>
                  <td className="px-3 py-3">
                    <Badge tone={u.ativo ? "ativo" : "inativo"}>{u.ativo ? "Ativo" : "Inativo"}</Badge>
                  </td>
                  <td className="px-3 py-3 text-right flex justify-end gap-1">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(u)}>
                      <Pencil className="size-4 text-sky-400" />
                    </Button>
                    <Button 
                      size="icon-sm" 
                      variant="ghost" 
                      onClick={() => toggleStatus.mutate({ id: u.id, ativo: !u.ativo })}
                      className={u.ativo ? "text-amber-400" : "text-emerald-400"}
                    >
                      {u.ativo ? <Power className="size-4" /> : <RotateCcw className="size-4" />}
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de Cadastro/Edição */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-slate-100">{editando ? "Editar Usuário" : "Novo Usuário"}</h2>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)}>
                <X className="size-4" />
              </Button>
            </div>

            <div className="space-y-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Nome Completo *</Label>
                <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: João da Silva" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">E-mail *</Label>
                <Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} placeholder="joao@frotabrv.com" />
              </div>
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Perfil de Acesso</Label>
                <select 
                  value={form.perfil} 
                  onChange={(e) => setForm(s => ({ ...s, perfil: e.target.value }))}
                  className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3"
                >
                  <option value="Administrador">Administrador</option>
                  <option value="Gestor">Gestor</option>
                  <option value="Operador">Operador</option>
                  <option value="Manutenção">Manutenção</option>
                  <option value="Financeiro">Financeiro</option>
                  <option value="Motorista">Motorista</option>
                </select>
              </div>
              {!editando && (
                <div className="grid gap-1.5">
                  <Label className="text-xs text-slate-400">Senha Inicial *</Label>
                  <Input type="password" value={form.senha} onChange={(e) => setForm(s => ({ ...s, senha: e.target.value }))} placeholder="••••••••" />
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setModalOpen(false)}>Cancelar</Button>
              <Button 
                onClick={() => salvar.mutate(form)} 
                disabled={salvar.isPending || !form.nome || !form.email}
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                <Check className="size-4 mr-2" /> Salvar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''

with open(path_front, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Frontend: Tela de Usuários completa criada.")

# ==========================================
# 2. BACKEND: ROTAS POST E PUT NO USUARIOS.PY
# ==========================================
path_back = os.path.join(os.getcwd(), "app", "backend", "routers", "usuarios.py")

with open(path_back, "r", encoding="utf-8") as f:
    c = f.read()

if "@router.post" not in c:
    rotas_crud = '''

@router.post("")
async def criar_usuario(body: dict, _u: dict = Depends(require("write"))):
    import uuid
    import bcrypt
    senha_hash = bcrypt.hashpw(body.get("senha", "").encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    novo = {
        "id": str(uuid.uuid4()),
        "nome": body.get("nome"),
        "email": body.get("email"),
        "perfil": body.get("perfil", "Operador"),
        "senha": senha_hash,
        "ativo": True
    }
    await db.usuarios.insert_one(novo)
    novo.pop("_id", None)
    novo.pop("senha", None)
    return novo

@router.put("/{id}")
async def atualizar_usuario(id: str, body: dict, _u: dict = Depends(require("write"))):
    update = {"nome": body.get("nome"), "email": body.get("email"), "perfil": body.get("perfil")}
    await db.usuarios.update_one({"id": id}, {"$set": update})
    return {"status": "ok"}
'''
    c += rotas_crud
    if "import bcrypt" not in c:
        c = "import bcrypt\n" + c
    with open(path_back, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Backend: Rotas POST /usuarios e PUT /usuarios/{id} adicionadas.")

print("\n✅ Tudo pronto! Faça o git push.")