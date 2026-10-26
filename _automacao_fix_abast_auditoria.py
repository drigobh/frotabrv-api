import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garantir que o created_by_name seja salvo na criação manual
    if 'doc["created_by_name"]' not in c:
        c = c.replace(
            'doc["created_by"] = user.get("id", "sistema")',
            'doc["created_by"] = user.get("id", "sistema")\n    doc["created_by_name"] = user.get("nome", user.get("email", "Sistema"))'
        )
    
    # Garantir que o created_by_name seja salvo na importação
    if '"created_by_name"' not in c:
        c = c.replace(
            '"created_by": user.get("id", "sistema"),',
            '"created_by": user.get("id", "sistema"),\n        "created_by_name": user.get("nome", user.get("email", "Sistema")),'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Auditoria garantida (created_by_name).")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar estado para o modal de auditoria
    if 'auditoriaRow' not in c:
        c = c.replace(
            'const [fornecedorPendente, setFornecedorPendente] = useState',
            'const [auditoriaRow, setAuditoriaRow] = useState<any | null>(null);\n  const [fornecedorPendente, setFornecedorPendente] = useState'
        )

    # 2. Reescrever o formulário de edição/criação
    padrao_form = re.compile(r'<form className="grid grid-cols-2 gap-2"[\s\S]*?</form>', re.DOTALL)
    novo_form = r'''<form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
              <div className="col-span-2 grid gap-1.5"><Label>Veículo *</Label><FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="form-veiculo" /></div>
              <div className="col-span-2 grid gap-1.5"><Label>Motorista</Label><FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Nenhum —" }, ...(motoristas.data ?? []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))]} testId="form-motorista" /></div>
              
              <div className="grid gap-1.5"><Label>Data *</Label><Input type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required /></div>
              <div className="grid gap-1.5"><Label>Hodômetro *</Label><Input type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} required /></div>
              
              <div className="grid gap-1.5"><Label>Litros *</Label><Input inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} required /></div>
              <div className="grid gap-1.5"><Label>Preço/L *</Label><Input inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} required /></div>

              <div className="col-span-2 border-t border-slate-800 pt-2 mt-1">
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-1.5">
                    <Label>CNPJ Emitente</Label>
                    <div className="flex gap-2">
                      <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: formatCnpj(e.target.value) }))} placeholder="00.000.000/0000-00" maxLength={18} />
                      <Button type="button" variant="default" onClick={buscarCnpj} disabled={cnpjLoading || form.cnpj.length < 18} className="bg-sky-600 hover:bg-sky-500 px-3 font-medium">
                        {cnpjLoading ? <Loader2 className="size-4 animate-spin" /> : <><Search className="size-4 mr-1" /> Online</>}
                      </Button>
                    </div>
                  </div>
                  <div className="grid gap-1.5">
                    <Label>Fornecedor *</Label>
                    <FieldSelect value={form.fornecedor} onChange={(v) => {
                      const f = fornecedores.find((x:any) => x.nome === v);
                      setForm(s => ({ 
                        ...s, 
                        fornecedor: v, 
                        cnpj: f ? (f.documento || "") : s.cnpj, 
                        cidade: f ? (f.cidade || "") : s.cidade, 
                        estado: f ? (f.estado || "") : s.estado,
                        avaliacao: f ? (f.avaliacao || 0) : s.avaliacao
                      }));
                    }} options={fornecedores?.map((f: any) => ({ value: f.nome, label: f.nome })) || []} placeholder="Selecione o fornecedor" />
                  </div>
                  <div className="grid gap-1.5"><Label>Cidade</Label><Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} /></div>
                  <div className="grid gap-1.5"><Label>Estado (UF)</Label><Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="uppercase" /></div>
                </div>
              </div>

              <div className="col-span-2 flex items-center gap-3 bg-slate-900/30 p-2 rounded-lg border border-slate-800">
                <Label className="text-xs text-slate-400">Avaliação do Fornecedor:</Label>
                <div className="flex gap-1 items-center">
                  {[1, 2, 3, 4, 5].map(star => (
                    <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                      <Star className={`size-4 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                    </button>
                  ))}
                  <span className="text-[10px] text-slate-500 ml-1">{form.avaliacao === 0 ? "" : `${form.avaliacao}/5`}</span>
                </div>
              </div>

              <div className="grid gap-1.5"><Label>Nº NF</Label><Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} placeholder="Ex: 12550" /></div>
              <div className="grid gap-1.5"><Label>Hora</Label><Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} /></div>
              <div className="col-span-2 grid gap-1.5"><Label>Chave NF-e</Label><Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} placeholder="3126 1020..." /></div>

              <div className="col-span-2 rounded-xl bg-gradient-to-r from-slate-900 to-slate-800 border border-sky-500/30 p-4 flex justify-between items-center shadow-lg shadow-sky-500/10 mt-2">
                <span className="text-sm font-bold text-slate-300 uppercase tracking-wider">Valor Total</span>
                <span className="text-3xl font-bold text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]">{Number.isFinite(total) ? brl(total) : "R$ 0,00"}</span>
              </div>

              <DialogFooter className="col-span-2 mt-2"><Button type="submit" disabled={salvar.isPending || !form.veiculo_id}>{editingId ? "Salvar" : "Registrar"}</Button></DialogFooter>
            </form>'''

    if padrao_form.search(c):
        c = padrao_form.sub(lambda m: novo_form, c)

    # 3. Atualizar as ações do grid (Adicionar botão Info)
    old_actions = '''<div className="flex gap-1 justify-center">
                      <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Cadastrado por: ${(r as any).created_by_name || (r as any).created_by || 'Sistema'}`}>
                        <Info className="size-4 text-slate-400" />
                      </Button>
                      <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'''
    
    new_actions = '''<div className="flex gap-1 justify-center">
                      <Button size="icon-sm" variant="ghost" onClick={() => setAuditoriaRow(r)} title="Ver Auditoria">
                        <Info className="size-4 text-slate-400 hover:text-sky-400" />
                      </Button>
                      <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'''
    
    c = c.replace(old_actions, new_actions)

    # 4. Adicionar o Dialog de Auditoria no final do componente (antes do </div> final)
    if 'auditoriaRow !== null' not in c:
        dialog_auditoria = r'''
      <Dialog open={auditoriaRow !== null} onOpenChange={(o) => !o && setAuditoriaRow(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Info className="size-5 text-sky-400" /> Auditoria do Registro
            </DialogTitle>
          </DialogHeader>
          <div className="py-4 space-y-3">
            <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
              <p className="text-[10px] uppercase text-slate-500 font-bold mb-1">Criado por</p>
              <p className="text-sm text-slate-200 font-medium">{auditoriaRow?.created_by_name || auditoriaRow?.created_by || "Sistema"}</p>
            </div>
            <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
              <p className="text-[10px] uppercase text-slate-500 font-bold mb-1">Data/Hora da Criação</p>
              <p className="text-sm text-slate-200">{auditoriaRow?.created_at ? new Date(auditoriaRow.created_at).toLocaleString('pt-BR') : "Não informada"}</p>
            </div>
            <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
              <p className="text-[10px] uppercase text-slate-500 font-bold mb-1">Origem do Registro</p>
              <p className="text-sm text-sky-400 font-medium uppercase">{auditoriaRow?.origem || "Manual"}</p>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setAuditoriaRow(null)} variant="outline">Fechar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
'''
        c = c.replace('<ConfirmDialog open={excluirId !== null}', dialog_auditoria + '<ConfirmDialog open={excluirId !== null}')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Campos de NF/Hora/Chave restaurados e Auditoria implementada com modal.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)