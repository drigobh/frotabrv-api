import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adiciona a aba "sucata" no tipo do useState
c = c.replace(
    'useState<"cadastrados" | "movimentacao" | "estoque" | "dashboard" | "manutencao">("cadastrados")',
    'useState<"cadastrados" | "movimentacao" | "estoque" | "dashboard" | "manutencao" | "sucata">("cadastrados")'
)

# 2. Atualiza os botões de navegação (Abas)
botoes_abas = '''
      <div className="flex gap-2 mb-4 border-b border-slate-800 pb-2 overflow-x-auto">
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'cadastrados' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('cadastrados')}>
          <Disc className="size-4 inline mr-2" /> Pneus Cadastrados
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'movimentacao' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('movimentacao')}>
          <ArrowRightLeft className="size-4 inline mr-2" /> Movimentação (Chassi)
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'estoque' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('estoque')}>
          <RefreshCw className="size-4 inline mr-2" /> Estoque
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'manutencao' ? 'bg-slate-800 text-amber-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('manutencao')}>
          <Wrench className="size-4 inline mr-2" /> Manutenção
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'sucata' ? 'bg-slate-800 text-rose-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('sucata')}>
          <Trash2 className="size-4 inline mr-2" /> Sucata
        </button>
        <button className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${abaAtiva === 'dashboard' ? 'bg-slate-800 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => setAbaAtiva('dashboard')}>
          <BarChart3 className="size-4 inline mr-2" /> Indicadores
        </button>
      </div>
'''
# Substitui o bloco de abas antigo pelo novo
c = re.sub(r'<div className="flex gap-2 mb-4 border-b border-slate-800 pb-2">[\s\S]*?</div>\n\n      \{abaAtiva === "cadastrados"', botoes_abas + '\n      {abaAtiva === "cadastrados"', c)


# 3. REESCREVENDO A ABA ESTOQUE (Limpa, só manda pra manutenção)
aba_estoque = '''
      {abaAtiva === "estoque" && (
        <div>
          <div className="glass p-6 rounded-2xl">
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <RefreshCw className="size-5 text-sky-400" /> Pneus em Estoque (Prontos)
            </h3>
            
            {pneus.filter((p: any) => p.status === "Estoque").length === 0 ? (
              <div className="text-center py-8 text-slate-500">Nenhum pneu em estoque no momento.</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pneus.filter((p: any) => p.status === "Estoque").map((p: any) => (
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
                      <Button size="sm" variant="outline" className="flex-1 text-xs border-amber-500/40 text-amber-400 hover:bg-amber-500/10" onClick={() => { setPneuChecklist(p); setFormChecklist({ tipo: "RECAPAGEM", avaliacao_carcaca: "APROVADA", borracheiro: "", motivo: "", observacoes: "", km_manutencao: "" }); setChecklistOpen(true); }}>
                        <Wrench className="size-3 mr-1" /> Enviar p/ Manutenção
                      </Button>
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
              <Wrench className="size-5 text-amber-400" /> Oficina / Manutenção
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
                        <CheckCircle2 className="size-3 mr-1" /> Retornar ao Estoque
                      </Button>
                      <Button size="sm" variant="outline" className="w-full text-xs border-rose-500/40 text-rose-400 hover:bg-rose-500/10" onClick={() => {
                        setPneuChecklist(p);
                        setFormChecklist({ tipo: "DESCARTE", avaliacao_carcaca: "REPROVADA", borracheiro: "", motivo: "", observacoes: "", km_manutencao: "" });
                        setChecklistOpen(true);
                      }}>
                        <Trash2 className="size-3 mr-1" /> Reprovar (Sucatear)
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {abaAtiva === "sucata" && (
        <div>
          <div className="glass p-6 rounded-2xl border border-rose-500/30">
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <Trash2 className="size-5 text-rose-400" /> Pneus Sucateados
            </h3>
            <div className="text-center py-8 text-slate-500 text-sm">
              Os pneus que são reprovados na manutenção ou descartados aparecerão aqui com o histórico completo.
            </div>
          </div>
        </div>
      )}
'''

# Substitui os blocos antigos de estoque e manutenção pelo novo bloco integrado
c = re.sub(r'\{abaAtiva === "manutencao" && \([\s\S]*?\{abaAtiva === "estoque" && \([\s\S]*?\{abaAtiva === "dashboard"', aba_estoque + '\n\n      {abaAtiva === "dashboard"', c)


# 4. Ajusta o Modal do Checklist para lidar com "RETORNO"
modal_jsx = '''
      {/* Modal de Checklist Borracheiro */}
      {checklistOpen && pneuChecklist && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-md p-6">
            <h2 className="text-lg font-bold text-slate-100 mb-1 flex items-center gap-2">
              <Wrench className="size-5 text-amber-400" /> Checklist Borracheiro
            </h2>
            <p className="text-sm text-slate-400 mb-4">Pneu Nº Fogo: <strong className="text-amber-400">{pneuChecklist.numero_fogo}</strong></p>
            
            <div className="space-y-4">
              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Ação</Label>
                <select value={formChecklist.tipo} onChange={(e) => setFormChecklist(s => ({ ...s, tipo: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  {pneuChecklist.status === "Estoque" ? (
                    <>
                      <option value="RECAPAGEM">Enviar para Recapagem</option>
                      <option value="CONSERTO">Enviar para Conserto</option>
                    </>
                  ) : (
                    <>
                      <option value="RETORNO">Retornar ao Estoque (Aprovado)</option>
                      <option value="DESCARTE">Sucatear (Reprovado)</option>
                    </>
                  )}
                </select>
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Avaliação da Carcaça</Label>
                <select value={formChecklist.avaliacao_carcaca} onChange={(e) => setFormChecklist(s => ({ ...s, avaliacao_carcaca: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  <option value="APROVADA">Aprovada (Boa para uso)</option>
                  <option value="REPROVADA">Reprovada (Inviável)</option>
                  <option value="RECUSADA">Recusada pelo Fornecedor</option>
                </select>
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Nome do Borracheiro / Responsável *</Label>
                <Input value={formChecklist.borracheiro} onChange={(e) => setFormChecklist(s => ({ ...s, borracheiro: e.target.value }))} placeholder="Ex: João da Silva" />
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">KM Atual do Veículo (Opcional)</Label>
                <Input type="number" value={formChecklist.km_manutencao} onChange={(e) => setFormChecklist(s => ({ ...s, km_manutencao: e.target.value }))} placeholder="Ex: 150000" />
              </div>

              <div className="grid gap-1.5">
                <Label className="text-xs text-slate-400">Observações Técnicas</Label>
                <Input value={formChecklist.observacoes} onChange={(e) => setFormChecklist(s => ({ ...s, observacoes: e.target.value }))} placeholder="Ex: Furo no ombro, carcaça íntegra." />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Button variant="outline" onClick={() => setChecklistOpen(false)}>Cancelar</Button>
              <Button onClick={() => { 
                if (formChecklist.tipo === "RETORNO") {
                   apiPut(`/pneus/${pneuChecklist.id}`, { ...pneuChecklist, status: "Estoque" }).then(() => {
                     toast.success("Pneu retornou ao estoque!");
                     qc.invalidateQueries({ queryKey: ["pneus"] });
                     setChecklistOpen(false);
                   });
                } else {
                   movimentar.mutate({ pneu_id: pneuChecklist.id, tipo: formChecklist.tipo }); 
                   setChecklistOpen(false); 
                }
              }} disabled={movimentar.isPending || !formChecklist.borracheiro} className="bg-amber-600 hover:bg-amber-500 text-white">
                Confirmar Checklist
              </Button>
            </div>
          </div>
        </div>
      )}
'''

# Remove o modal antigo se existir e insere o novo
c = re.sub(r'\{/\* Modal de Checklist Borracheiro \*/\}[\s\S]*?\{checklistOpen && pneuChecklist && \([\s\S]*?</div>\n        </div>\n      \)\}', lambda m: modal_jsx, c)


with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Arquitetura das abas refatorada com sucesso!")
print("✅ Aba Manutenção agora é a oficina (Checklist).")
print("✅ Aba Estoque está limpa.")
print("✅ Aba Sucata isolada.")