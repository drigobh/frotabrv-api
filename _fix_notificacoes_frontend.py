import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adicionar o estado de notificações no form
if "notificacoes" not in c.split("setForm")[0]:
    c = c.replace(
        'const [form, setForm] = useState<any>({ \n    nome: "", email: "", perfil_id: "", setor: "", cargo: "", telefone: "", whatsapp: "", foto_url: "", senha: "" \n  });',
        'const [form, setForm] = useState<any>({ \n    nome: "", email: "", perfil_id: "", setor: "", cargo: "", telefone: "", whatsapp: "", foto_url: "", senha: "", notificacoes: { manutencao: true, documentos: true, pneus: true, resumo_semanal: false } \n  });'
    )

# 2. Atualizar abrirNovo e abrirEdicao para incluir notificações
c = c.replace(
    'setForm({ nome: "", email: "", perfil_id: "", setor: "", cargo: "", telefone: "", whatsapp: "", foto_url: "", senha: "" });',
    'setForm({ nome: "", email: "", perfil_id: "", setor: "", cargo: "", telefone: "", whatsapp: "", foto_url: "", senha: "", notificacoes: { manutencao: true, documentos: true, pneus: true, resumo_semanal: false } });'
)
c = c.replace(
    'foto_url: u.foto_url || "", \n      senha: ""',
    'foto_url: u.foto_url || "", \n      senha: "",\n      notificacoes: u.notificacoes || { manutencao: true, documentos: true, pneus: true, resumo_semanal: false }'
)

# 3. Injetar a seção de notificações dentro do modal (após a seção Segurança)
padrao_seguranca = r'(<h3 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2 border-b border-slate-800 pb-2">\s*<Lock className="size-4 text-amber-400" /> Segurança e Acesso\s*</h3>[\s\S]*?)(?=</div>\s*</div>\s*<div className="flex justify-end gap-3)'
if "notificacoes" not in c.split("Notificações")[0]:
    c = re.sub(padrao_seguranca, r'\1', c)  # Apenas garantir que a regex existe
    # Adiciona a seção de notificações após a seção de Segurança
    c = c.replace(
        '</div>\n\n            <div className="flex justify-end gap-3 border-t border-slate-800 px-6 py-4">',
        '''</div>

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
                    <label key={n.key} className="flex items-center justify-between p-3 rounded-lg border border-slate-800 bg-slate-900/30">
                      <div>
                        <p className="text-sm font-medium text-slate-200">{n.label}</p>
                        <p className="text-xs text-slate-500">{n.desc}</p>
                      </div>
                      <input 
                        type="checkbox" 
                        checked={form.notificacoes?.[n.key] || false} 
                        onChange={(e) => setForm((s: any) => ({ 
                          ...s, 
                          notificacoes: { ...s.notificacoes, [n.key]: e.target.checked } 
                        }))}
                        className="size-4 rounded border-slate-600 text-sky-500 focus:ring-sky-500/20"
                      />
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 border-t border-slate-800 px-6 py-4">'''
    )

# 4. Garantir que o ícone Bell está importado
if "Bell" not in c.split("from \"lucide-react\"")[0]:
    c = c.replace("import {", "import { Bell,")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Frontend: Aba de notificações injetada no modal de usuário.")