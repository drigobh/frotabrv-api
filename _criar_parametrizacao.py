import os
import re

# ==========================================
# 1. CRIAR A PÁGINA DE PARAMETRIZAÇÃO
# ==========================================
path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Parametrizacao.tsx")

conteudo = r'''import { useState } from "react";
import { Check, Info, Lock, Plus, Save, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const perfis = ["Administrador", "Gestor", "Manutenção", "Financeiro", "Motorista"] as const;
type Perfil = typeof perfis[number];

const modulos = [
  { nome: "Frota e Acoplamentos", novo: false },
  { nome: "Abastecimentos", novo: false },
  { nome: "Pneus", novo: false },
  { nome: "Manutenção e Oficina", novo: false },
  { nome: "Financeiro", novo: false },
  { nome: "Estoque", novo: false },
  { nome: "Relatórios", novo: false },
  { nome: "Multas e Infrações", novo: true },
  { nome: "Seguros e Sinistros", novo: true },
  { nome: "Checklist de Viagem", novo: true },
];

const acoes = ["Ver", "Criar", "Editar", "Excluir", "Aprovar"] as const;
type Acao = typeof acoes[number];

// Lógica de permissões padrão (simulando um banco de dados)
const padrao: Record<string, boolean> = {};
for (const perfil of perfis) {
  for (const m of modulos) {
    for (const a of acoes) {
      const chave = `${perfil}|${m.nome}|${a}`;
      if (perfil === "Administrador") padrao[chave] = true;
      else if (perfil === "Gestor") padrao[chave] = a !== "Excluir";
      else if (perfil === "Manutenção") padrao[chave] = ["Ver", "Criar", "Editar"].includes(a) && ["Pneus", "Manutenção e Oficina", "Estoque", "Frota e Acoplamentos"].includes(m.nome);
      else if (perfil === "Financeiro") padrao[chave] = ["Ver", "Aprovar", "Editar"].includes(a) && ["Financeiro", "Abastecimentos", "Relatórios"].includes(m.nome);
      else padrao[chave] = a === "Ver" && ["Frota e Acoplamentos", "Checklist de Viagem"].includes(m.nome);
    }
  }
}

const liberacoesIniciais = [
  { modulo: "Frota e Acoplamentos", plano: "Essencial", ativo: true, escopo: "Todos os usuários" },
  { modulo: "Abastecimentos", plano: "Essencial", ativo: true, escopo: "Todos os usuários" },
  { modulo: "Pneus", plano: "Pro", ativo: true, escopo: "Gestores e manutenção" },
  { modulo: "Manutenção e Oficina", plano: "Pro", ativo: true, escopo: "Gestores e manutenção" },
  { modulo: "Financeiro", plano: "Pro", ativo: true, escopo: "Financeiro e gestores" },
  { modulo: "Multas e Infrações", plano: "Pro", ativo: false, escopo: "Ainda não liberado" },
  { modulo: "Checklist de Viagem", plano: "Essencial", ativo: false, escopo: "Piloto com motoristas" },
];

export default function Parametrizacao() {
  const [perfil, setPerfil] = useState<Perfil>("Gestor");
  const [perms, setPerms] = useState<Record<string, boolean>>(padrao);
  const [flags, setFlags] = useState(liberacoesIniciais.map((l) => l.ativo));

  const alternar = (modulo: string, acao: Acao) => {
    const chave = `${perfil}|${modulo}|${acao}`;
    setPerms((p) => ({ ...p, [chave]: !p[chave] }));
  };

  const totalPermitidas = modulos.reduce(
    (s, m) => s + acoes.filter((a) => perms[`${perfil}|${m.nome}|${a}`]).length,
    0,
  );

  return (
    <div>
      <PageHeader
        eyebrow="Administração"
        title="Parametrização e Liberação"
        description="Controle quem acessa o quê, quais módulos estão ativos e as regras de negócio do sistema."
        actions={
          <div className="flex gap-2">
            <Button variant="outline" className="h-9 border-slate-700 text-slate-300">Descartar</Button>
            <Button className="h-9 bg-emerald-600 hover:bg-emerald-500">
              <Save className="size-4 mr-2" /> Salvar Alterações
            </Button>
          </div>
        }
      />

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Perfis Ativos</p>
          <p className="mt-2 font-mono text-2xl font-bold text-slate-100">{perfis.length}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Módulos Liberados</p>
          <p className="mt-2 font-mono text-2xl font-bold text-slate-100">{flags.filter(Boolean).length} <span className="text-sm font-normal text-slate-500">/ {modulos.length}</span></p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Permissões do Perfil</p>
          <p className="mt-2 font-mono text-2xl font-bold text-sky-400">{totalPermitidas}</p>
        </div>
        <div className="glass p-4 rounded-xl border border-slate-800">
          <p className="text-[11px] uppercase tracking-widest text-slate-400">Última Alteração</p>
          <p className="mt-2 text-sm text-slate-300">Hoje, às 14:32</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Matriz de Permissões por Perfil */}
        <div className="lg:col-span-2 glass rounded-2xl border border-slate-800 overflow-hidden">
          <div className="p-5 border-b border-slate-800">
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
              <ShieldCheck className="size-4 text-sky-400" /> Matriz de Permissões
            </h2>
            <p className="text-xs text-slate-400 mt-1">Defina as ações permitidas para cada perfil.</p>
          </div>
          
          {/* Abas de Perfis */}
          <div className="flex gap-1 bg-slate-900/50 px-3 py-2 border-b border-slate-800 overflow-x-auto">
            {perfis.map((p) => (
              <button
                key={p}
                onClick={() => setPerfil(p)}
                className={cn(
                  "px-3 py-1.5 text-xs font-medium rounded-lg whitespace-nowrap transition-colors",
                  perfil === p ? "bg-sky-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                )}
              >
                {p}
              </button>
            ))}
          </div>

          {/* Tabela de Matriz */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/30">
                <tr className="text-[10px] uppercase tracking-wider text-slate-500">
                  <th className="px-5 py-3 font-medium">Módulo</th>
                  {acoes.map((a) => (
                    <th key={a} className="px-3 py-3 text-center font-medium">{a}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {modulos.map((m) => (
                  <tr key={m.nome} className="hover:bg-slate-800/30">
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-200">{m.nome}</span>
                        {m.novo && <Badge className="bg-sky-500/20 text-sky-400 border-sky-500/30 text-[9px] px-1.5 py-0"><Sparkles className="size-2.5 mr-1" /> Novo</Badge>}
                      </div>
                    </td>
                    {acoes.map((a) => {
                      const ativo = perms[`${perfil}|${m.nome}|${a}`];
                      return (
                        <td key={a} className="px-3 py-3 text-center">
                          <button
                            onClick={() => alternar(m.nome, a)}
                            className={cn(
                              "size-5 rounded border flex items-center justify-center transition-colors",
                              ativo ? "bg-sky-600 border-sky-600 text-white" : "border-slate-600 text-transparent hover:border-sky-500"
                            )}
                          >
                            <Check className="size-3.5" />
                          </button>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Módulos Liberados e Regras */}
        <div className="space-y-6">
          {/* Liberação de Módulos */}
          <div className="glass rounded-2xl border border-slate-800 overflow-hidden">
            <div className="p-5 border-b border-slate-800">
              <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Lock className="size-4 text-amber-400" /> Liberação de Módulos
              </h2>
              <p className="text-xs text-slate-400 mt-1">Ative ou desative módulos por empresa.</p>
            </div>
            <ul className="divide-y divide-slate-800">
              {liberacoesIniciais.map((l, i) => (
                <li key={l.modulo} className="flex items-center justify-between p-4">
                  <div>
                    <p className="text-sm font-medium text-slate-200">{l.modulo}</p>
                    <p className="text-[10px] text-slate-500">{flags[i] ? l.escopo : "Oculto para todos"}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className={cn("text-[9px]", l.plano === "Pro" ? "border-sky-500/30 text-sky-400" : "border-slate-600 text-slate-400")}>{l.plano}</Badge>
                    <button
                      onClick={() => setFlags((f) => f.map((v, idx) => (idx === i ? !v : v)))}
                      className={cn(
                        "w-9 h-5 rounded-full relative transition-colors",
                        flags[i] ? "bg-emerald-500" : "bg-slate-700"
                      )}
                    >
                      <div className={cn("absolute top-0.5 size-4 rounded-full bg-white transition-all", flags[i] ? "left-[18px]" : "left-0.5")} />
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Regras de Negócio */}
          <div className="glass rounded-2xl border border-slate-800 overflow-hidden p-5">
            <h2 className="text-sm font-bold text-slate-100 flex items-center gap-2 mb-4">
              <Zap className="size-4 text-amber-400" /> Parâmetros de Regra
            </h2>
            <div className="space-y-4">
              {[
                { label: "Tolerância de Consumo", valor: "8", unidade: "%", ajuda: "Avisar se o km/l cair mais que isso." },
                { label: "Limite s/ Aprovação", valor: "5000", unidade: "R$", ajuda: "OS acima disso exigem gestor." },
                { label: "Antecedência de Alerta", valor: "45", unidade: "dias", ajuda: "Aviso de vencimento de docs." },
              ].map((r) => (
                <div key={r.label} className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-xs font-medium text-slate-200">{r.label}</p>
                    <p className="text-[10px] text-slate-500 leading-tight">{r.ajuda}</p>
                  </div>
                  <div className="flex items-center gap-1 bg-slate-900 border border-slate-700 rounded-md px-2 py-1">
                    <input type="text" defaultValue={r.valor} className="w-12 bg-transparent text-right font-mono text-xs text-slate-100 outline-none" />
                    <span className="text-[10px] text-slate-500">{r.unidade}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'''

with open(path, "w", encoding="utf-8") as f:
    f.write(conteudo)
print("✅ Página Parametrizacao.tsx criada.")

# ==========================================
# 2. INJETAR ROTA NO APP.TSX
# ==========================================
app_path = os.path.join(os.getcwd(), "frontend", "src", "App.tsx")
with open(app_path, "r", encoding="utf-8") as f:
    app_c = f.read()

if "Parametrizacao" not in app_c:
    app_c = app_c.replace(
        'import VeiculoDetalhe from "@/pages/VeiculoDetalhe";',
        'import VeiculoDetalhe from "@/pages/VeiculoDetalhe";\nimport Parametrizacao from "@/pages/Parametrizacao";'
    )
    # Coloca a rota logo após a rota de segurança ou base
    app_c = app_c.replace(
        '<Route path="/admin/seguranca"',
        '<Route path="/admin/parametrizacao" element={<Parametrizacao />} />\n          <Route path="/admin/seguranca"'
    )
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(app_c)
    print("✅ Rota /admin/parametrizacao injetada no App.tsx.")

# ==========================================
# 3. INJETAR LINK NO SIDEBAR (MENU ADMINISTRAÇÃO)
# ==========================================
sidebar_path = os.path.join(os.getcwd(), "frontend", "src", "components", "layout", "Sidebar.tsx")
with open(sidebar_path, "r", encoding="utf-8") as f:
    side_c = f.read()

if "/admin/parametrizacao" not in side_c:
    # Encontra o link existente de Parametrização
    padrao = r'\{ label: "Parametrização".*?\},'
    if re.search(padrao, side_c):
        side_c = re.sub(padrao, '{ label: "Parametrização", icon: Settings, path: "/admin/parametrizacao" },', side_c)
        print("✅ Link de Parametrização atualizado para a nova rota.")
    else:
        # Se não existir, injeta após "Base (Limpeza)"
        ancora = '{ label: "Base (Limpeza)", icon: FileText, path: "/admin/base" },'
        novo_link = ancora + '\n      { label: "Parametrização", icon: Settings, path: "/admin/parametrizacao" },'
        side_c = side_c.replace(ancora, novo_link)
        print("✅ Link de Parametrização injetado no menu Administração.")

    with open(sidebar_path, "w", encoding="utf-8") as f:
        f.write(side_c)
else:
    print("ℹ️ O link já existia.")
    