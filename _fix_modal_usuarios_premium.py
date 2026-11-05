import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

novo_modal = r'''{/* Modal de Cadastro/Edição Premium */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl flex flex-col">
            {/* Header */}
            <div className="flex justify-between items-center border-b border-slate-800 px-6 py-4">
              <div>
                <h2 className="text-lg font-bold text-slate-100">{editando ? "Editar Usuário" : "Novo Usuário"}</h2>
                <p className="text-xs text-slate-400 mt-1">Preencha as informações e defina as permissões de acesso.</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-slate-100">
                <X className="size-5" />
              </Button>
            </div>

            {/* Corpo do Modal */}
            <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
              {/* Seção 1: Dados Pessoais */}
              <div>
                <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                  <User className="size-4 text-sky-400" /> Dados Pessoais
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Nome Completo *</Label>
                    <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} placeholder="Ex: João da Silva" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">E-mail de Acesso *</Label>
                    <Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} placeholder="joao@frotabrv.com" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Telefone / WhatsApp</Label>
                    <Input placeholder="(11) 99999-9999" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Perfil de Acesso</Label>
                    <select value={form.perfil} onChange={(e) => setForm(s => ({ ...s, perfil: e.target.value }))} className="h-10 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                      <option value="Administrador">Administrador</option>
                      <option value="Gestor">Gestor</option>
                      <option value="Operador">Operador</option>
                      <option value="Manutenção">Manutenção</option>
                      <option value="Financeiro">Financeiro</option>
                      <option value="Motorista">Motorista</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Seção 2: Permissões de Módulos */}
              <div>
                <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                  <Shield className="size-4 text-amber-400" /> Permissões Granulares
                </h3>
                <p className="text-xs text-slate-500 mb-3">O que este usuário pode ver e fazer em cada módulo.</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {["Abastecimentos", "Pneus", "Manutenção", "Frota", "Financeiro", "Relatórios", "Cadastros", "Administração"].map((modulo) => (
                    <label key={modulo} className="flex items-center gap-2.5 rounded-lg border border-slate-800 p-2.5 cursor-pointer hover:bg-slate-800/30 transition-colors">
                      <input type="checkbox" defaultChecked={form.perfil === "Administrador"} className="size-4 rounded border-slate-600 text-sky-500 focus:ring-sky-500/20" />
                      <span className="text-sm text-slate-300">{modulo}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Seção 3: Segurança */}
              {!editando && (
                <div>
                  <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                    <Key className="size-4 text-emerald-400" /> Segurança
                  </h3>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Senha Inicial *</Label>
                    <Input type="password" value={form.senha} onChange={(e) => setForm(s => ({ ...s, senha: e.target.value }))} placeholder="Mínimo 8 caracteres" className="bg-slate-950 border-slate-700 h-10" />
                  </div>
                  <p className="text-[11px] text-slate-500 mt-2">O usuário será forçado a trocar a senha no primeiro acesso.</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 border-t border-slate-800 px-6 py-4 bg-slate-900/50 rounded-b-2xl">
              <Button variant="outline" onClick={() => setModalOpen(false)} className="border-slate-700 text-slate-300">Cancelar</Button>
              <Button 
                onClick={() => salvar.mutate(form)} 
                disabled={salvar.isPending || !form.nome || !form.email}
                className="bg-emerald-600 hover:bg-emerald-500 text-white px-6"
              >
                <Check className="size-4 mr-2" /> Salvar Usuário
              </Button>
            </div>
          </div>
        </div>
      )}'''

# Substituir o modal antigo pelo novo
c = re.sub(r'\{/\* Modal de Cadastro/Edição \*/\}[\s\S]*?\{modalOpen && \([\s\S]*?</div>\n    </div>\n  \)\;', novo_modal, c)

# Garantir imports dos ícones
if "User" not in c.split("from \"lucide-react\"")[0]:
    c = c.replace("import {", "import { User, Key,")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Modal de Usuários reescrito com design Premium!")