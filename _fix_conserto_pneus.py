import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove a aba "sucata" que eu criei errado
c = c.replace('useState<"cadastrados" | "movimentacao" | "estoque" | "dashboard" | "manutencao" | "sucata">("cadastrados")', 'useState<"cadastrados" | "movimentacao" | "estoque" | "dashboard" | "manutencao">("cadastrados")')

# 2. Volta os botões de navegação para o padrão (5 abas, sem "Sucata" separada)
botoes_abas = '''
      <div className="flex gap-2 mb-4 border-b border-slate-800 pb-2 overflow-x-auto">
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'cadastrados' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('cadastrados')}>
          <Disc className="size-4 inline mr-2" /> Pneus Cadastrados
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'movimentacao' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('movimentacao')}>
          <ArrowRightLeft className="size-4 inline mr-2" /> Movimentação (Chassi)
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'estoque' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('estoque')}>
          <RefreshCw className="size-4 inline mr-2" /> Estoque / Sucata
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'manutencao' ? 'bg-slate-800 text-amber-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('manutencao')}>
          <Wrench className="size-4 inline mr-2" /> Manutenção
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'dashboard' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('dashboard')}>
          <BarChart3 className="size-4 inline mr-2" /> Indicadores
        </button>
      </div>
'''
c = re.sub(r'<div className="flex gap-2 mb-4 border-b border-slate-800 pb-2 overflow-x-auto">[\s\S]*?</div>\n\n      \{abaAtiva === "cadastrados"', botoes_abas + '\n      {abaAtiva === "cadastrados"', c)

# 3. Restaura a aba ESTOQUE / SUCATA como era (Cards de estoque + Cards de sucata)
aba_estoque_sucata = '''
      {abaAtiva === "estoque" && (
        <div className="space-y-6">
          <div className="glass p-6 rounded-2xl">
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <RefreshCw className="size-5 text-sky-400" /> Pneus em Estoque
            </h3>
            
            {stats.emEstoque.length === 0 ? (
              <div className="text-center py-8 text-slate-500">Nenhum pneu em estoque no momento.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {stats.emEstoque.map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-sky-500/30">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-bold text-sky-400">{p.numero_fogo}</p>
                        <p className="text-xs text-slate-300">{p.marca} - {p.medida}</p>
                        <p className="text-[10px] text-slate-500">DOT: {p.dot || "—"} | Sulco: {p.profundidade_atual || "—"} mm</p>
                      </div>
                      <span className="text-xs font-mono text-amber-400">{brl(p.custo_aquisicao)}</span>
                    </div>
                    <div className="mt-3 flex gap-2">
                      <Button size="sm" variant="outline" className="w-full text-xs border-amber-500/40 text-amber-400 hover:bg-amber-500/10" onClick={() => { setPneuChecklist(p); setFormChecklist({ tipo: "RECAPAGEM", avaliacao_carcaca: "APROVADA", borracheiro: "", motivo: "", observacoes: "", km_manutencao: "" }); setChecklistOpen(true); }}>
                        <Wrench className="size-3 mr-1" /> Enviar p/ Manutenção
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="glass p-6 rounded-2xl border border-rose-500/20">
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <Trash2 className="size-5 text-rose-400" /> Histórico de Sucatas
            </h3>
            {pneus.filter((p: any) => p.status === "Sucateado").length === 0 ? (
              <div className="text-center py-8 text-slate-500">Nenhum pneu sucateado.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pneus.filter((p: any) => p.status === "Sucateado").map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-rose-500/30 bg-rose-950/10 opacity-80">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-bold text-rose-400 line-through">{p.numero_fogo}</p>
                        <p className="text-xs text-slate-400">{p.marca} - {p.medida}</p>
                        <p className="text-[10px] text-slate-500">Motivo: {p.uso_atual || "Não informado"}</p>
                      </div>
                      <span className="text-xs font-mono text-slate-500">{brl(p.custo_aquisicao)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {abaAtiva === "manutencao" && (
        <div>
          <div className="glass p-6 rounded-2xl border border-amber-500/30">
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <Wrench className="size-5 text-amber-400" /> Pneus na Oficina
            </h3>
            
            {pneus.filter((p: any) => ["Recapagem", "Conserto"].includes(p.status)).length === 0 ? (
              <div className="text-center py-8 text-slate-500">Nenhum pneu em manutenção no momento.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pneus.filter((p: any) => ["Recapagem", "Conserto"].includes(p.status)).map((p: any) => (
                  <div key={p.id} className="glass p-4 rounded-xl border border-amber-500/40 bg-amber-950/20">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <p className="text-sm font-bold text-amber-400">{p.numero_fogo}</p>
                        <p className="text-xs text-slate-300">{p.marca} - {p.medida}</p>
                        <span className="inline-block mt-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-600 text-white">{p.status}</span>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Button size="sm" variant="outline" className="w-full text-xs border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10" onClick={() => {
                        setPneuChecklist(p);
                        setFormChecklist({ tipo: "RETORNO", avaliacao_carcaca: "APROVADA", borracheiro: "", motivo: "", observacoes: "", km_manutencao: "" });
                        setChecklistOpen(true);
                      }}>
                        <CheckCircle2 className="size-3 mr-1" /> Aprovar e Retornar
                      </Button>
                      <Button size="sm" variant="outline" className="w-full text-xs border-rose-500/40 text-rose-400 hover:bg-rose-500/10" onClick={() => {
                        setPneuChecklist(p);
                        setFormChecklist({ tipo: "DESCARTE", avaliacao_carcaca: "REPROVADA", borracheiro: "", motivo: "", observacoes: "", km_manutencao: "" });
                        setChecklistOpen(true);
                      }}>
                        <Trash2 className="size-3 mr-1" /> Reprovar e Sucatear
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
'''

# Substitui a aba de estoque e manutenção atuais pelo novo layout
c = re.sub(r'\{abaAtiva === "estoque" && \([\s\S]*?\{abaAtiva === "dashboard"', aba_estoque_sucata + '\n\n      {abaAtiva === "dashboard"', c)

# 4. Remove a aba "sucata" que tinha sido criada no final (se ainda existir)
c = re.sub(r'\{abaAtiva === "sucata" && \([\s\S]*?\}\n      \)', '', c)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Conserto aplicado! Aba Estoque / Sucata unificada e Manutenção preenchida.")