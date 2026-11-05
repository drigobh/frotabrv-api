import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Adiciona os estados do checklist
if "const [checklistOpen" not in c:
    c = c.replace(
        "const [open, setOpen] = useState(false);",
        "const [open, setOpen] = useState(false);\n  const [checklistOpen, setChecklistOpen] = useState(false);\n  const [pneuChecklist, setPneuChecklist] = useState<any>(null);\n  const [formChecklist, setFormChecklist] = useState({ tipo: 'RECAPAGEM', avaliacao_carcaca: 'APROVADA', borracheiro: '', motivo: '', observacoes: '', km_manutencao: '' });"
    )
    print("✅ Estados do checklist adicionados.")

# 2. Atualiza a mutation de movimentar para enviar os dados do checklist
if "avaliacao_carcaca" not in c:
    c = c.replace(
        'return apiPost("/pneu-movimentacoes", {\n        pneu_id,\n        tipo,\n        motivo: tipo === "DESCARTE" ? "Descarte via Estoque" : null,\n      });',
        'return apiPost("/pneu-movimentacoes", { pneu_id, tipo, ...formChecklist });'
    )
    print("✅ Mutation de movimentar atualizada.")

# 3. Altera o botão de Manutenção no Estoque para abrir o Modal
c = c.replace(
    'onClick={() => movimentar.mutate({ pneu_id: p.id, tipo: "RECAPAGEM" })}',
    'onClick={() => { setPneuChecklist(p); setFormChecklist({ tipo: "RECAPAGEM", avaliacao_carcaca: "APROVADA", borracheiro: "", motivo: "", observacoes: "", km_manutencao: "" }); setChecklistOpen(true); }}'
)
c = c.replace(
    'onClick={() => { if (confirm("Descartar este pneu como sucata?")) movimentar.mutate({ pneu_id: p.id, tipo: "DESCARTE" }); }}',
    'onClick={() => { setPneuChecklist(p); setFormChecklist({ tipo: "DESCARTE", avaliacao_carcaca: "REPROVADA", borracheiro: "", motivo: "", observacoes: "", km_manutencao: "" }); setChecklistOpen(true); }}'
)

# 4. Adiciona o Modal do Checklist antes do fechamento final do componente
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
                <Label className="text-xs text-slate-400">Tipo de Serviço</Label>
                <select value={formChecklist.tipo} onChange={(e) => setFormChecklist(s => ({ ...s, tipo: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                  <option value="RECAPAGEM">Recapagem</option>
                  <option value="CONSERTO">Conserto</option>
                  <option value="DESCARTE">Descarte / Sucata</option>
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
                <Label className="text-xs text-slate-400">Nome do Borracheiro / Responsável</Label>
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
              <Button onClick={() => { movimentar.mutate({ pneu_id: pneuChecklist.id, tipo: formChecklist.tipo }); setChecklistOpen(false); }} disabled={movimentar.isPending || !formChecklist.borracheiro} className="bg-amber-600 hover:bg-amber-500 text-white">
                Confirmar Checklist
              </Button>
            </div>
          </div>
        </div>
      )}
'''

if "Checklist Borracheiro" not in c:
    # Insere antes do último </div> do return
    c = c.rsplit("</div>\n  );", 1)[0] + modal_jsx + "\n</div>\n  );" + c.rsplit("</div>\n  );", 1)[1]
    print("✅ Modal de Checklist Borracheiro adicionado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)