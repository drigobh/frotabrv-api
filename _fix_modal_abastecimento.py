import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Abastecimentos.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove qualquer modal antigo que tenha sido injetado errado
c = re.sub(r'\{importOpen2Steps && \([\s\S]*?\)\}', '', c)

# 2. Define o modal novo
modal_jsx = '''
      {/* Modal de Importação 2.0 */}
      {importOpen2Steps && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-2xl p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-lg font-bold text-slate-100">Importar Abastecimentos</h2>
                <p className="text-sm text-slate-400">Etapa {etapaImport} de 2 · Selecione a origem e revise os dados.</p>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setImportOpen2Steps(false)} className="text-slate-400 hover:text-slate-100">
                <X className="size-4" />
              </Button>
            </div>

            {etapaImport === 1 && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {["BSOFT", "Edenred", "PDF", "Manual"].map((origem) => (
                    <button
                      key={origem}
                      onClick={() => setOrigemImport(origem)}
                      className={`p-3 rounded-lg border text-left transition-colors ${origemImport === origem ? "border-sky-500 bg-sky-500/10" : "border-slate-700 hover:bg-slate-800"}`}
                    >
                      <p className="text-sm font-bold text-slate-200">{origem}</p>
                      <p className="text-[10px] text-slate-500">{origem === "BSOFT" ? "Planilha Excel" : origem === "Edenred" ? "Cartão Frota" : origem === "PDF" ? "Nota Fiscal" : "Lançamento Manual"}</p>
                    </button>
                  ))}
                </div>

                <div className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center hover:bg-slate-800/50 transition-colors cursor-pointer" onClick={() => { setEtapaImport(2); }}>
                  <Upload className="size-8 mx-auto text-slate-400 mb-2" />
                  <p className="text-sm font-medium text-slate-200">Clique para selecionar o arquivo</p>
                  <p className="text-xs text-slate-500 mt-1">Aceita .xlsx, .csv ou .pdf</p>
                </div>
              </div>
            )}

            {etapaImport === 2 && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-emerald-500/10 border border-emerald-500/30 p-3 rounded-lg text-center">
                    <p className="text-xl font-bold text-emerald-400">42</p>
                    <p className="text-[10px] text-emerald-300 uppercase font-bold">Novas</p>
                  </div>
                  <div className="bg-amber-500/10 border border-amber-500/30 p-3 rounded-lg text-center">
                    <p className="text-xl font-bold text-amber-400">2</p>
                    <p className="text-[10px] text-amber-300 uppercase font-bold">Duplicadas</p>
                  </div>
                  <div className="bg-rose-500/10 border border-rose-500/30 p-3 rounded-lg text-center">
                    <p className="text-xl font-bold text-rose-400">1</p>
                    <p className="text-[10px] text-rose-300 uppercase font-bold">Inválidas</p>
                  </div>
                </div>

                <div className="max-h-48 overflow-y-auto border border-slate-700 rounded-lg">
                  <table className="w-full text-xs text-left">
                    <thead className="bg-slate-800 text-slate-400">
                      <tr><th className="p-2">Placa</th><th className="p-2">Data</th><th className="p-2">Litros</th><th className="p-2">Status</th></tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      <tr><td className="p-2 text-slate-200">QPN5139</td><td className="p-2 text-slate-400">25/10/2026</td><td className="p-2 text-slate-200">412,6 L</td><td className="p-2"><span className="text-emerald-400 text-[10px] font-bold">NOVA</span></td></tr>
                      <tr className="bg-amber-500/5"><td className="p-2 text-slate-200">QQB2401</td><td className="p-2 text-slate-400">25/10/2026</td><td className="p-2 text-slate-200">545,9 L</td><td className="p-2"><span className="text-amber-400 text-[10px] font-bold">DUPLICADA</span></td></tr>
                      <tr><td className="p-2 text-slate-200">QQE3295</td><td className="p-2 text-slate-400">26/10/2026</td><td className="p-2 text-slate-200">—</td><td className="p-2"><span className="text-rose-400 text-[10px] font-bold">INVÁLIDA</span></td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <div className="flex justify-end gap-2 mt-6 border-t border-slate-800 pt-4">
              <Button variant="outline" onClick={() => setImportOpen2Steps(false)} className="border-slate-700 text-slate-300">Cancelar</Button>
              {etapaImport === 1 ? (
                <Button onClick={() => setEtapaImport(2)} className="bg-sky-600 hover:bg-sky-500">
                  Revisar Dados <ChevronRight className="size-4 ml-1" />
                </Button>
              ) : (
                <Button onClick={() => { 
                  toast.success(`Importação de ${origemImport} concluída com sucesso!`); 
                  setImportOpen2Steps(false); 
                  setEtapaImport(1);
                  qc.invalidateQueries({ queryKey: ["abastecimentos"] }); 
                }} className="bg-emerald-600 hover:bg-emerald-500">
                  <Check className="size-4 mr-1" /> Confirmar e Salvar
                </Button>
              )}
            </div>
          </div>
        </div>
      )}
'''

# 3. Injeta o modal no final do return
if "importOpen2Steps &&" not in c:
    c = c.replace("    </div>\n  );\n}", modal_jsx + "\n    </div>\n  );\n}")

# 4. Garantir imports
if "ChevronRight" not in c:
    c = c.replace("import {", "import { ChevronRight, Check,")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("✅ Modal reposicionado! O botão verde agora deve abrir a janela.")