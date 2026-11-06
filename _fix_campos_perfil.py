import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Perfis.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Encontrar a seção onde ficam os campos Nome e Descrição
# e adicionar os novos campos logo abaixo.
padrao_campos = r'(<div className="grid grid-cols-1 md:grid-cols-2 gap-4">[\s\S]*?</div>\s*</div>)'

novos_campos = '''<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Nome do Perfil *</Label>
                    <Input value={form.nome} onChange={(e) => setForm((s: any) => ({ ...s, nome: e.target.value }))} placeholder="Ex: Gestor de Frota" />
                  </div>
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Descrição</Label>
                    <Input value={form.descricao} onChange={(e) => setForm((s: any) => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Acesso total ao módulo de frotas" />
                  </div>
                </div>
                
                {/* Segurança */}
                <div>
                  <h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">
                    <Lock className="size-4 text-amber-400" /> Segurança
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  </div>
                </div>'''

# Substituir o bloco de campos antigo pelo novo
c = re.sub(padrao_campos, novos_campos, c, count=1)

# 2. Garantir que o ícone Lock está importado
if "Lock" not in c.split("from \"lucide-react\"")[0]:
    c = c.replace("import {", "import { Lock,")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Perfis.tsx: Campos de Timeout e Tentativas adicionados corretamente.")