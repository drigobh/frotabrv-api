import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "CadastrosFinanceiros.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Substitui a tabela de Categorias inteira pela versão com cores vibrantes e padrão bancos
padrao_tabela = r'\{/\* ABA CATEGORIAS \*/\}[\s\S]*?(?=\{/\* MODAL BANCO \*/\})'

nova_tabela = '''
      {/* ABA CATEGORIAS */}
      {abaAtiva === "Categorias" && (
        <div>
          <div className="flex gap-2 justify-between items-center mb-4">
            <div className="flex gap-2">
              <div className="relative w-72">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-slate-400" />
                <Input placeholder="Buscar categoria..." value={buscaCat} onChange={(e) => setBuscaCat(e.target.value)} className="pl-9 h-9" />
              </div>
              <select value={filtroCat} onChange={(e) => setFiltroCat(e.target.value)} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-3">
                <option value="Todos">Todos os Tipos</option>
                <option value="Pagar">Pagar</option>
                <option value="Receber">Receber</option>
                <option value="Ambos">Ambos</option>
              </select>
            </div>
            <Button onClick={abrirNovaCat} className="bg-sky-600 hover:bg-sky-500 h-9"><Plus className="size-4 mr-2" /> Nova Categoria</Button>
          </div>

          <div className="glass rounded-2xl overflow-hidden border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50">
                <tr className="text-[11px] uppercase tracking-wider text-slate-400">
                  <th className="px-5 py-3 font-medium text-slate-200">Nome</th>
                  <th className="px-3 py-3 font-medium text-slate-200">Tipo</th>
                  <th className="px-3 py-3 text-right font-medium text-slate-200">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {categoriasFiltradas.length === 0 ? (
                  <tr><td colSpan={3} className="p-8 text-center text-slate-300">Nenhuma categoria encontrada.</td></tr>
                ) : (
                  categoriasFiltradas.map((c: any) => (
                    <tr key={c.id} className={cn("hover:bg-slate-800/30 transition-colors", !c.ativo && "opacity-50")}>
                      <td className="px-5 py-3 text-slate-200 font-medium">{c.nome}</td>
                      <td className="px-3 py-3">
                        <span className={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wide",
                          c.tipo === "Pagar" ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" :
                          c.tipo === "Receber" ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" :
                          "bg-sky-500/20 text-sky-400 border border-sky-500/30"
                        )}>
                          {c.tipo === "Pagar" && <ArrowUpCircle className="size-3.5" />}
                          {c.tipo === "Receber" && <ArrowDownCircle className="size-3.5" />}
                          {c.tipo === "Ambos" && <CircleDot className="size-3.5" />}
                          {c.tipo}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right flex justify-end gap-1">
                        <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicaoCat(c)}><Pencil className="size-4 text-sky-400" /></Button>
                        <Button size="icon-sm" variant="ghost" onClick={() => alternarStatusCat.mutate({ id: c.id, ativo: !c.ativo })} className={c.ativo ? "text-amber-400" : "text-emerald-400"}>
                          <Power className="size-4" />
                        </Button>
                        <Button size="icon-sm" variant="ghost" onClick={() => { if (confirm("Excluir categoria?")) excluirCat.mutate(c.id); }}><Trash2 className="size-4 text-rose-400" /></Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

'''

if re.search(padrao_tabela, c):
    c = re.sub(padrao_tabela, nova_tabela.strip(), c)
    print("✅ Tabela de Categorias atualizada com cores vibrantes e padrão Bancos.")
else:
    print("⚠️ Bloco da tabela de Categorias não encontrado. Verifique o arquivo.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)