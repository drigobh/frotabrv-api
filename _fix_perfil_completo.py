import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfil.tsx")

conteudo = r'''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useMe } from "@/hooks/useSession";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ShieldCheck, User, Bell, Key, Save, Camera } from "lucide-react";
import { apiPut } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

const abas = ["Meus Dados", "Segurança", "Notificações"] as const;

export default function Perfil() {
  const { data: me, refetch } = useMe();
  const qc = useQueryClient();
  const [abaAtiva, setAbaAtiva] = useState<typeof abas[number]>("Meus Dados");

  const [form, setForm] = useState<any>({
    nome: me?.nome || "",
    email: me?.email || "",
    telefone: me?.telefone || "",
    whatsapp: me?.whatsapp || "",
    setor: me?.setor || "",
    cargo: me?.cargo || "",
    foto_url: me?.foto_url || "",
  });

  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");

  const salvarPerfil = useMutation({
    mutationFn: (payload: any) => apiPut("/auth/perfil", payload),
    onSuccess: () => {
      toast.success("Perfil atualizado com sucesso!");
      refetch();
      qc.invalidateQueries({ queryKey: ["me"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao salvar.")
  });

  const alterarSenha = async () => {
    if (novaSenha !== confirmarSenha) {
      return toast.error("As senhas não coincidem.");
    }
    if (novaSenha.length < 6) {
      return toast.error("A senha deve ter no mínimo 6 caracteres.");
    }
    try {
      await apiPut("/auth/perfil", { senha_atual: senhaAtual, nova_senha: novaSenha });
      toast.success("Senha alterada com sucesso!");
      setSenhaAtual(""); setNovaSenha(""); setConfirmarSenha("");
    } catch (e: any) {
      toast.error(e.message || "Erro ao alterar senha.");
    }
  };

  return (
    <div>
      <PageHeader
        eyebrow="Minha Conta"
        title="Perfil do Usuário"
        description="Gerencie suas informações pessoais, senha e preferências."
        actions={
          <Button onClick={() => salvarPerfil.mutate(form)} disabled={salvarPerfil.isPending} className="bg-emerald-600 hover:bg-emerald-500 h-9">
            <Save className="size-4 mr-2" /> Salvar Alterações
          </Button>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        {/* Painel Lateral (Avatar e Navegação) */}
        <div className="space-y-4">
          <div className="glass rounded-2xl border border-slate-800 p-6 flex flex-col items-center text-center">
            <div className="relative mb-4">
              <div className="size-24 rounded-full bg-slate-800 border-2 border-sky-500/30 flex items-center justify-center text-3xl font-bold text-slate-300 shadow-lg shadow-sky-500/10 overflow-hidden">
                {form.foto_url ? (
                  <img src={form.foto_url} alt={form.nome} className="size-full object-cover" />
                ) : (
                  form.nome?.charAt(0).toUpperCase() || "U"
                )}
              </div>
              <button className="absolute bottom-0 right-0 p-1.5 bg-slate-800 rounded-full border border-slate-600 hover:bg-slate-700 transition-colors">
                <Camera className="size-3.5 text-slate-300" />
              </button>
            </div>
            <h2 className="text-lg font-bold text-slate-100">{form.nome || "Usuário"}</h2>
            <p className="text-xs text-slate-400 mb-2">{form.email || "email@frotabrv.com"}</p>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 text-[10px] font-bold uppercase tracking-wider">
              <ShieldCheck className="size-3" /> {me?.perfil || "Usuário"}
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
                    <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">E-mail</Label>
                    <Input value={form.email} disabled className="bg-slate-900/50 border-slate-800 h-10 text-slate-500" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Telefone</Label>
                    <Input value={form.telefone} onChange={(e) => setForm(s => ({ ...s, telefone: e.target.value }))} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">WhatsApp</Label>
                    <Input value={form.whatsapp} onChange={(e) => setForm(s => ({ ...s, whatsapp: e.target.value }))} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Setor</Label>
                    <Input value={form.setor} onChange={(e) => setForm(s => ({ ...s, setor: e.target.value }))} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Cargo</Label>
                    <Input value={form.cargo} onChange={(e) => setForm(s => ({ ...s, cargo: e.target.value }))} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2 md:col-span-2">
                    <Label className="text-xs text-slate-400">URL da Foto de Perfil</Label>
                    <Input value={form.foto_url} onChange={(e) => setForm(s => ({ ...s, foto_url: e.target.value }))} placeholder="https://..." className="bg-slate-950 border-slate-700 h-10" />
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
                    <Input type="password" value={senhaAtual} onChange={(e) => setSenhaAtual(e.target.value)} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Nova Senha</Label>
                    <Input type="password" value={novaSenha} onChange={(e) => setNovaSenha(e.target.value)} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-2">
                    <Label className="text-xs text-slate-400">Confirmar Nova Senha</Label>
                    <Input type="password" value={confirmarSenha} onChange={(e) => setConfirmarSenha(e.target.value)} className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <Button onClick={alterarSenha} className="bg-sky-600 hover:bg-sky-500">Alterar Senha</Button>
                </div>
              </div>
              <div className="border-t border-slate-800 pt-6">
                <h3 className="text-base font-bold text-slate-100 mb-2">Autenticação em Dois Fatores (2FA)</h3>
                <p className="text-xs text-slate-400 mb-4">Adicione uma camada extra de segurança.</p>
                <Button variant="outline" className="border-slate-700 text-slate-300">Configurar 2FA</Button>
              </div>
            </div>
          )}

          {abaAtiva === "Notificações" && (
            <div className="space-y-6">
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
          )}
        </div>
      </div>
    </div>
  );
}
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)

print("✅ Perfil.tsx reescrito para exibir e salvar todos os campos do usuário!")