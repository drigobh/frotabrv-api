import os

caminho = os.path.join(os.getcwd(), "frontend", "src", "pages", "Abastecimentos.tsx")

conteudo = '''
  return (
    <div>
      <PageHeader
        eyebrow="Operação"
        title="Abastecimentos"
        description="Registro detalhado com cálculo automático de KM rodados e média KM/L a partir do hodômetro."
        actions={
          <div className="flex gap-2">
            <input type="file" accept=".xls,.xlsx" ref={xlsInputRef} onChange={handleImportXLS} className="hidden" />
            <Button variant="outline" onClick={() => xlsInputRef.current?.click()}>
              <Upload className="size-4 mr-2" /> Importar XLS
            </Button>
            <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />
            <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
              <FileText className="size-4 mr-2" /> Importar NF
            </Button>
            <Button onClick={abrirNovo}>
              <Plus className="size-4" /> Novo abastecimento
            </Button>
          </div>
        }
      />

      <div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {cards.map((c) => (
          <div key={c.label} className="glass lift relative overflow-hidden rounded-xl transition-all hover:scale-[1.02]" style={{ padding: '12px 16px', height: '90px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '28px', height: '28px', borderRadius: '8px', backgroundColor: `${c.color}20`, color: c.color }}>
                <c.icon size={16} />
              </div>
              <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            </div>
            <div>
              <p style={{ fontSize: '20px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '10px', color: '#64748b', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.sub}</p>}
            </div>
          </div>
        ))}
      </div>

      <div className="mb-5 glass rounded-xl p-4">
        <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
          <TrendingUp className="size-4 text-emerald-400" />
          Termômetro de Eficiência (Top 5 KM/L)
        </h3>
        <div className="space-y-2 w-full">
          {ranking.length === 0 ? (
            <p className="text-sm text-slate-500">Sem dados suficientes para calcular o ranking.</p>
          ) : (
            ranking.map((r, i) => {
              const placa = r.label.split(" ")[0];
              const percent = Math.min((r.media / 5) * 100, 100);
              const isGood = r.media >= 2.5;
              return (
                <div key={r.label} className="flex items-center gap-3 w-full">
                  <span className="w-6 text-xs text-slate-500 font-mono">{i + 1}º</span>
                  <span className="w-20 text-sm font-medium text-slate-300 font-mono" title={r.label}>{placa}</span>
                  <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${isGood ? 'bg-emerald-500' : 'bg-red-500'}`} 
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-sm font-bold text-slate-200">{num(r.media, 2)}</span>
                </div>
              );
            })
          )}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div className="grid w-64 gap-1.5">
          <Label>Veículo</Label>
          <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} testId="abastecimento-filtro-veiculo" />
        </div>
        <div className="grid gap-1.5">
          <Label htmlFor="filtro-mes">Mês</Label>
          <Input id="filtro-mes" type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="w-44" />
        </div>
        {(mes || filtroVeiculo !== TODOS) && (
          <Button variant="ghost" onClick={() => { setMes(""); setFiltroVeiculo(TODOS); }}>Limpar filtros</Button>
        )}
      </div>

      <div className="glass overflow-hidden rounded-2xl">
        <Table className="text-xs">
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 whitespace-nowrap px-2 text-left">Data</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-center px-2">Origem</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-2 text-left">Veículo</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-2 text-left">Motorista</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Litros</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">R$/L</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Total</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 px-2 text-left">Posto</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">KM</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Rodados</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-right px-2">Média</TableHead>
              <TableHead className="text-[10px] uppercase tracking-wider text-slate-500 text-center px-2">Ações</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 && (
              <TableRow><TableCell colSpan={12} className="py-10 text-center text-slate-500">{q.isPending ? "Carregando…" : "Nenhum abastecimento encontrado."}</TableCell></TableRow>
            )}
            {rows.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{dataBR(r.data)}</TableCell>
                <TableCell className="text-center px-2">
                  {r.origem === "pdf" ? (
                    <span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>
                  ) : (
                    <span className="inline-flex items-center justify-center rounded bg-slate-500/20 px-2 py-0.5 text-xs font-bold text-slate-400" title="Inserido Manualmente">M</span>
                  )}
                </TableCell>
                <TableCell className="font-mono text-xs whitespace-nowrap px-2 text-left">{r.veiculo_label.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300 text-xs whitespace-nowrap px-2 truncate max-w-[150px] text-left">{r.motorista_label ?? "—"}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.litros, 1)}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.preco_litro, 2)}</TableCell>
                <TableCell className="tabular-nums font-medium text-xs whitespace-nowrap px-2 text-right">{brl(r.valor_total)}</TableCell>
                <TableCell className="text-xs whitespace-nowrap px-2 truncate max-w-[100px] text-slate-400 text-left">{r.posto}</TableCell>
                <TableCell className="font-mono tabular-nums text-xs whitespace-nowrap px-2 text-right">{num(r.km)}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                <TableCell className="tabular-nums text-xs whitespace-nowrap px-2 text-right text-sky-300">{r.media_km_l != null ? `${num(r.media_km_l, 2)}` : "—"}</TableCell>
                <TableCell className="text-center px-2">
                  <div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)} aria-label="Editar">
                      <Pencil className="size-4 text-sky-400" />
                    </Button>
                    {me?.perfil === "admin" && (
                      <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirId(r.id)} aria-label="Excluir">
                        <Trash2 className="size-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={open} onOpenChange={(o) => { setOpen(o); if(!o) setEditingId(null); }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Fuel className="size-5 text-sky-400" /> 
              {editingId ? "Editar abastecimento" : "Novo abastecimento"}
            </DialogTitle>
          </DialogHeader>
          <form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-data">Data *</Label>
              <Input id="ab-data" type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-km">Hodômetro (KM) *</Label>
              <Input id="ab-km" type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} required />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Veículo *</Label>
              <FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo" testId="abastecimento-form-veiculo" />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Motorista</Label>
              <FieldSelect
                value={form.motorista_id}
                onChange={set("motorista_id")}
                options={[{ value: NENHUM, label: "— Não informado —" }, ...(motoristas.data ?? []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))]}
                testId="abastecimento-form-motorista"
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-litros">Litros *</Label>
              <Input id="ab-litros" inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="ab-preco">Preço por litro (R$) *</Label>
              <Input id="ab-preco" inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} required />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label htmlFor="ab-posto">Posto *</Label>
              <Input id="ab-posto" value={form.posto} onChange={(e) => set("posto")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label>Nº NF</Label>
              <Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} placeholder="12550" />
            </div>
            <div className="grid gap-1.5">
              <Label>Hora</Label>
              <Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} />
            </div>
            <div className="col-span-2 grid gap-1.5">
              <Label>Chave NF-e</Label>
              <Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} placeholder="3126 1020..." />
            </div>
            <div className="grid gap-1.5">
              <Label>CNPJ Emitente</Label>
              <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: e.target.value }))} placeholder="00.000.000/0000-00" />
            </div>
            <div className="grid gap-1.5">
              <Label>Fornecedor</Label>
              <Input value={form.fornecedor} onChange={(e) => setForm(s => ({ ...s, fornecedor: e.target.value }))} placeholder="Posto..." />
            </div>
            <p className="col-span-2 rounded-lg bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
              Valor total: <span className="font-semibold text-slate-50">{Number.isFinite(total) ? brl(total) : "—"}</span>
            </p>
            <DialogFooter className="col-span-2">
              <Button type="submit" disabled={salvar.isPending || !form.veiculo_id}>{editingId ? "Salvar Alterações" : "Registrar"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={excluirId !== null}
        onOpenChange={(o) => !o && setExcluirId(null)}
        title="Excluir abastecimento?"
        description="Esta ação é registrada na auditoria e não pode ser desfeita."
        confirmLabel="Excluir"
        destructive
        pending={excluir.isPending}
        onConfirm={() => excluirId && excluir.mutate(excluirId)}
        testId="abastecimento-excluir"
      />
    </div>
  );
}
'''

with open(caminho, 'a', encoding='utf-8') as f:
    f.write(conteudo)

print("Parte 3 concluida com sucesso!")
print("Arquivo restaurado completamente!")