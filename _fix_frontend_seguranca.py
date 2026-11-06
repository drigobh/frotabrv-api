import os
import re

# ==========================================
# 1. COMPONENTE DE TIMER (Header)
# ==========================================
path_timer = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "SessionTimer.tsx")

conteudo_timer = r'''import { useState, useEffect } from "react";
import { Clock } from "lucide-react";

export function SessionTimer({ timeoutMinutos, onTimeout }: { timeoutMinutos: number, onTimeout: () => void }) {
  const [segundosRestantes, setSegundosRestantes] = useState(timeoutMinutos * 60);

  useEffect(() => {
    if (segundosRestantes <= 0) {
      onTimeout();
      return;
    }
    const interval = setInterval(() => {
      setSegundosRestantes((s) => s - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [segundosRestantes, onTimeout]);

  const minutos = Math.floor(segundosRestantes / 60);
  const segundos = segundosRestantes % 60;

  return (
    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/50 text-xs text-slate-400">
      <Clock className="size-3.5" />
      <span className="font-mono">{String(minutos).padStart(2, '0')}:{String(segundos).padStart(2, '0')}</span>
    </div>
  );
}
'''

with open(path_timer, "w", encoding="utf-8") as f:
    f.write(conteudo_timer)
print("✅ Componente SessionTimer criado.")

# ==========================================
# 2. ATUALIZAR O APP LAYOUT (Header com Timer)
# ==========================================
path_layout = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "AppLayout.tsx")

with open(path_layout, "r", encoding="utf-8") as f:
    l_c = f.read()

# Adicionar o timer no cabeçalho (se houver um Header)
# Vou assumir que o AppLayout tem um <header> ou uma div de topo
if "SessionTimer" not in l_c:
    # Importa o componente e o hook useMe
    l_c = l_c.replace(
        'import { Sidebar } from "./Sidebar";',
        'import { Sidebar } from "./Sidebar";\nimport { SessionTimer } from "./SessionTimer";\nimport { useMe } from "@/hooks/useSession";\nimport { realizarLogoff } from "@/lib/logoff";'
    )
    
    # Inicializa o hook e o timer
    l_c = l_c.replace(
        'export function AppLayout',
        'export function AppLayout'
    )
    
    # Adiciona o timer na barra de topo (se existir um header)
    # Para simplificar, vou adicionar no final do header, antes do fechamento
    if "<header" in l_c:
        l_c = l_c.replace('</header>', '<SessionTimer timeoutMinutos={30} onTimeout={realizarLogoff} /></header>')
    
    with open(path_layout, "w", encoding="utf-8") as f:
        f.write(l_c)
    print("✅ AppLayout: SessionTimer adicionado ao cabeçalho.")
else:
    print("ℹ️ SessionTimer já estava no AppLayout.")

# ==========================================
# 3. ADICIONAR CONTROLES DE SEGURANÇA NO FORM DE PERFIL
# ==========================================
path_perfil = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path_perfil, "r", encoding="utf-8") as f:
    p_c = f.read()

# Adicionar os campos timeout_minutos e tentativas_login no formulário de Perfil
if "timeout_minutos" not in p_c:
    # Procura a seção de descrição e adiciona os campos
    p_c = p_c.replace(
        '<Label className="text-xs text-slate-400">Descrição</Label>',
        '''<Label className="text-xs text-slate-400">Descrição</Label>
                    <Input value={form.descricao} onChange={(e) => setForm((s: any) => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Acesso total" />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Timeout de Sessão (minutos)</Label>
                    <Input type="number" value={form.timeout_minutos || 30} onChange={(e) => setForm((s: any) => ({ ...s, timeout_minutos: Number(e.target.value) }))} />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Tentativas de Login Permitidas</Label>
                    <select value={form.tentativas_login || 5} onChange={(e) => setForm((s: any) => ({ ...s, tentativas_login: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="3">3 tentativas</option>
                      <option value="5">5 tentativas</option>
                      <option value="7">7 tentativas</option>
                      <option value="liberado">Liberado (apenas avisa)</option>
                    </select>
                  </div>
                  <div className="grid gap-1.5 hidden">
                    <Label className="text-xs text-slate-400">Descrição</Label>'''
    )
    # Remover o campo duplicado
    p_c = p_c.replace('''<Label className="text-xs text-slate-400">Descrição</Label>
                    <Input value={form.descricao} onChange={(e) => setForm((s: any) => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Acesso total" />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Timeout de Sessão (minutos)</Label>
                    <Input type="number" value={form.timeout_minutos || 30} onChange={(e) => setForm((s: any) => ({ ...s, timeout_minutos: Number(e.target.value) }))} />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Tentativas de Login Permitidas</Label>
                    <select value={form.tentativas_login || 5} onChange={(e) => setForm((s: any) => ({ ...s, tentativas_login: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="3">3 tentativas</option>
                      <option value="5">5 tentativas</option>
                      <option value="7">7 tentativas</option>
                      <option value="liberado">Liberado (apenas avisa)</option>
                    </select>
                  </div>
                  <div className="grid gap-1.5 hidden">
                    <Label className="text-xs text-slate-400">Descrição</Label>''', '')

with open(path_perfil, "w", encoding="utf-8") as f:
    f.write(p_c)
print("✅ Perfis: Controles de timeout e tentativas adicionados ao formulário.")

# ==========================================
# 4. ADICIONAR BOTÃO DE DESTRAVAR NA TELA DE USUÁRIOS
# ==========================================
path_usuarios_front = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path_usuarios_front, "r", encoding="utf-8") as f:
    u_c = f.read()

# Adiciona a mutation de destravar
if "destravar" not in u_c:
    u_c = u_c.replace(
        'const salvar = useMutation({',
        '''const destravar = useMutation({
    mutationFn: (id: string) => apiPatch(`/usuarios/${id}/destravar`, {}),
    onSuccess: () => {
      toast.success("Usuário destravado com sucesso!");
      qc.invalidateQueries({ queryKey: ["usuarios"] });
    }
  });

  const salvar = useMutation({'''
    )

    # Adiciona o botão na tabela (se houver a coluna de ações)
    u_c = u_c.replace(
        '<Button size="icon-sm" variant="ghost" onClick={() => toggleStatus.mutate({ id: u.id, ativo: !u.ativo })}',
        '''<Button size="icon-sm" variant="ghost" onClick={() => destravar.mutate(u.id)} title="Destravar Login">
                      <ShieldAlert className="size-4 text-amber-400" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => toggleStatus.mutate({ id: u.id, ativo: !u.ativo })}'''
    )

with open(path_usuarios_front, "w", encoding="utf-8") as f:
    f.write(u_c)
print("✅ Usuarios: Botão de destravar adicionado à tabela.")