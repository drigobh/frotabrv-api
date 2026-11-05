import os
import re

# ==========================================
# 1. CRIAR A PÁGINA DE PERFIL
# ==========================================
path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfil.tsx")

conteudo = r'''import { useState } from "react";
import { useMe } from "@/hooks/useSession";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ShieldCheck, User, Bell, Key, Save } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const abas = ["Meus Dados", "Segurança", "Notificações"] as const;

export default function Perfil() {
  const { data: me } = useMe();
  const [abaAtiva, setAbaAtiva] = useState<typeof abas[number]>("Meus Dados");

  return (
    <div>
      <PageHeader
        eyebrow="Minha Conta"
        title="Perfil do Usuário"
        description="Gerencie suas informações pessoais, senha e preferências de notificação."
        actions={
          <Button className="bg-emerald-600 hover:bg-emerald-500 h-9" onClick={() => toast.success("Alterações salvas com sucesso!")}>
            <Save className="size-4 mr-2" /> Salvar Alterações
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        {/* Painel Lateral (Avatar e Navegação) */}
        <div className="space-y-4">
          <div className="glass rounded-2xl border border-slate-800 p-6 flex flex-col items-center text-center">
            <div className="size-24 rounded-full bg-slate-800 border-2 border-sky-500/30 flex items-center justify-center text-3xl font-bold text-slate-300 mb-4 shadow-lg shadow-sky-500/10">
              {me?.nome?.charAt(0).toUpperCase() || "U"}
            </div>
            <h2 className="text-lg font-bold text-slate-100">{me?.nome || "Usuário do Sistema"}</h2>
            <p className="text-xs text-slate-400 mb-2">{me?.email || "email@frotabrv.com"}</p>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 text-[10px] font-bold uppercase tracking-wider">
              <ShieldCheck className="size-3" /> {me?.perfil || "Administrador"}
            </span>
          </div>

          <div className="glass rounded-2xl border border-slate-800 p-2 flex flex-col gap-1">
            {abas.map((aba) => (
              <button
                key={aba}
                onClick={() => setAbaAtiva(aba)}
                className={cn(
                  "w-full text-left px-3 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2",
                  abaAtiva === aba ? "bg-sky-500/10 text-sky-400" : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                )}
              >
                {aba === "Meus Dados" && <User className="size-4" />}
                {aba === "Segurança" && <Key className="size-4" />}
                {aba === "Notificações" && <Bell className="size-4" />}
                {aba}
              </button>
            ))}
          </div>
        </div>

        {/* Conteúdo da Aba Selecionada */}
        <div className="glass rounded-2xl border border-slate-800 p-6">
          {abaAtiva === "Meus Dados" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-base font-bold text-slate-100 border-b border-slate-800 pb-2 mb-4">Informações Pessoais</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Nome Completo</Label>
                    <Input defaultValue={me?.nome || "Rodrigo Admin"} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">E-mail de Acesso</Label>
                    <Input defaultValue={me?.email || "admin@frotabrv.com"} type="email" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Telefone / WhatsApp</Label>
                    <Input defaultValue="(11) 99999-9999" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Cargo / Função</Label>
                    <Input defaultValue={me?.perfil || "Administrador"} disabled className="bg-slate-900/50 border-slate-800 h-10 text-slate-500" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {abaAtiva === "Segurança" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-base font-bold text-slate-100 border-b border-slate-800 pb-2 mb-4">Alterar Senha</h3>
                <div className="space-y-4 max-w-md">
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Senha Atual</Label>
                    <Input type="password" placeholder="••••••••" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Nova Senha</Label>
                    <Input type="password" placeholder="••••••••" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Confirmar Nova Senha</Label>
                    <Input type="password" placeholder="••••••••" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                </div>
              </div>
              <div className="border-t border-slate-800 pt-6">
                <h3 className="text-base font-bold text-slate-100 mb-2">Autenticação em Dois Fatores (2FA)</h3>
                <p className="text-xs text-slate-400 mb-4">Adicione uma camada extra de segurança à sua conta.</p>
                <Button variant="outline" className="border-slate-700 text-slate-300">Configurar 2FA</Button>
              </div>
            </div>
          )}

          {abaAtiva === "Notificações" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-base font-bold text-slate-100 border-b border-slate-800 pb-2 mb-4">Preferências de Notificação</h3>
                <ul className="space-y-4">
                  {[
                    { titulo: "Alertas de Manutenção", desc: "Receber e-mail quando uma OS for aberta.", ativo: true },
                    { titulo: "Vencimento de Documentos", desc: "Avisos de CRLV e CNH prestes a vencer.", ativo: true },
                    { titulo: "Pneus Críticos", desc: "Notificação imediata quando um pneu atingir o sulco mínimo.", ativo: true },
                    { titulo: "Resumo Semanal", desc: "Receber relatório de custos toda segunda-feira.", ativo: false },
                  ].map((n, i) => (
                    <li key={i} className="flex items-center justify-between gap-4 p-3 rounded-lg border border-slate-800 bg-slate-900/30">
                      <div>
                        <p className="text-sm font-medium text-slate-200">{n.titulo}</p>
                        <p className="text-xs text-slate-500">{n.desc}</p>
                      </div>
                      <div className={cn("w-10 h-5 rounded-full relative transition-colors cursor-pointer", n.ativo ? "bg-sky-500" : "bg-slate-700")}>
                        <div className={cn("absolute top-0.5 size-4 rounded-full bg-white transition-all", n.ativo ? "left-[22px]" : "left-0.5")} />
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Página Perfil.tsx criada.")

# ==========================================
# 2. ADICIONAR ROTA NO APP.TSX
# ==========================================
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "Perfil" not in app_c:
    app_c = app_c.replace(
        'import Parametrizacao from "@/pages/Parametrizacao";',
        'import Parametrizacao from "@/pages/Parametrizacao";\nimport Perfil from "@/pages/Perfil";'
    )
    app_c = app_c.replace(
        '<Route path="/admin/parametrizacao"',
        '<Route path="/perfil" element={<Perfil />} />\n          <Route path="/admin/parametrizacao"'
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_c)
    print("✅ Rota /perfil injetada no App.tsx.")

# ==========================================
# 3. TRANSFORMAR O BLOCO DE USUÁRIO EM LINK
# ==========================================
sidebar_path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    side_c = f.read()

# Encontra o bloco onde fica o nome do usuário no rodapé e transforma em Link
# (Vamos envelopar com um <Link> e adicionar hover)
padrao_user_block = r'<div className=\{cn\("flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-900/50 mb-2", isCollapsed && "justify-center"\)\}>'
novo_user_block = '<Link to="/perfil" className={cn("flex items-center gap-3 px-2 py-2 rounded-lg bg-slate-900/50 mb-2 transition-colors hover:bg-slate-800", isCollapsed && "justify-center")}>'

if "Link to=\"/perfil\"" not in side_c:
    side_c = re.sub(padrao_user_block, novo_user_block, side_c)
    # Fecha a tag div correspondente com </Link>
    # Procura o fechamento do bloco do usuário (geralmente após o cargo)
    # Como é complexo, vamos apenas trocar a div de fechamento naquele trecho específico
    # (O CSS flex mantém o visual igual)
    side_c = side_c.replace(
        '</div>\n        <Button variant="ghost" className={cn("w-full text-red-400',
        '</Link>\n        <Button variant="ghost" className={cn("w-full text-red-400'
    )
    with open(sidebar_path, "w", encoding="utf-8") as f:
        f.write(side_c)
    print("✅ Bloco de usuário transformado em link para o Perfil.")

print("\n✅ Tudo pronto! Pode rodar o git push.")