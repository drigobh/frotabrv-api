import os
import re

# 1. Criar a página de Usuários
path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

conteudo = r'''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Power, RotateCcw, Search, Shield } from "lucide-react";
import { apiGet, apiPatch } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

export default function Usuarios() {
  const qc = useQueryClient();
  const [busca, setBusca] = useState("");
  const { data: usuarios = [], isLoading } = useQuery({ 
    queryKey: ["usuarios"], 
    queryFn: () => apiGet<any[]>("/usuarios") 
  });

  const toggleStatus = useMutation({
    mutationFn: ({ id, ativo }: { id: string, ativo: boolean }) => 
      apiPatch(`/usuarios/${id}/status`, { ativo }),
    onSuccess: () => {
      toast.success("Status alterado com sucesso!");
      qc.invalidateQueries({ queryKey: ["usuarios"] });
    }
  });

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
            <Button className="bg-sky-600 hover:bg-sky-500 h-9">
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
                    <Button size="icon-sm" variant="ghost">
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
    </div>
  );
}
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Página Usuarios.tsx criada.")

# 2. Injetar no App.tsx
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "Usuarios" not in app_c:
    app_c = app_c.replace(
        'import Perfil from "@/pages/Perfil";',
        'import Perfil from "@/pages/Perfil";\nimport Usuarios from "@/pages/Usuarios";'
    )
    app_c = app_c.replace(
        '<Route path="/admin/parametrizacao"',
        '<Route path="/admin/usuarios" element={<Usuarios />} />\n          <Route path="/admin/parametrizacao"'
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_c)
    print("✅ Rota /admin/usuarios injetada.")