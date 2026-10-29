import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_LAYOUT_PLANOS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "PlanosManutencao.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/PlanosManutencao.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "PlanosManutencao.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Encontrar o bloco do modal (do {open && ( até o fechamento )}
    # Vamos substituir o modal inteiro pela versão de layout expandido
    padrao_modal = re.compile(r'\{open && \([\s\S]*?\)\}\s*\{excluirId &&', re.DOTALL)
    
    novo_modal = '''
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-5xl flex flex-col max-h-[90vh]">
            
            {/* Cabeçalho */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900 rounded-t-2xl">
              <h2 className="text-lg font-bold text-slate-100">{editingId ? "Editar Plano" : "Novo Plano"}</h2>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white">
                <X className="size-5" />
              </button>
            </div>

            {/* Corpo (Split View) */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex flex-col lg:flex-row gap-8">
                
                {/* COLUNA ESQUERDA: Resumo e Guia */}
                <div className="w-full lg:w-[300px] shrink-0 flex flex-col gap-4 border-r border-slate-800 pr-6">
                  
                  {/* Hodômetro Atual */}
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-slate-400 text-xs font-semibold uppercase mb-2">
                      <Gauge className="size-4" /> Hodômetro Atual
                    </div>
                    <p className="text-3xl font-bold text-sky-400 font-mono">
                      {hodometroAtual !== null ? `${hodometroAtual.toLocaleString('pt-BR')} km` : "—"}
                    </p>
                  </div>

                  {/* Guia de Componentes */}
                  <div className="bg-sky-950/30 border border-sky-900/50 rounded-xl p-4">
                    <div className="flex items-start gap-2">
                      <Info className="size-4 text-sky-400 mt-0.5 shrink-0" />
                      <div>
                        <strong className="text-sky-300 text-xs uppercase block mb-1">Itens cobertos:</strong>
                        <p className="text-xs text-sky-200/80 leading-relaxed">
                          {familiaSelecionada?.itens}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Usuário Responsável */}
                  <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-3 flex items-center gap-2 mt-auto">
                    <User className="size-4 text-slate-500" />
                    <span className="text-xs text-slate-400">Registrado por: <strong className="text-slate-300">{me?.nome || "Usuário"}</strong></span>
                  </div>
                </div>

                {/* COLUNA DIREITA: Formulário */}
                <div className="flex-1 flex flex-col gap-4">
                  
                  {/* Flag Tipo de Ativo */}
                  <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-700">
                    <button className={`flex-1 py-2 text-sm rounded-md font-medium ${tipoAtivo === 'cavalo' ? 'bg-sky-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('cavalo'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); setHodometroAtual(null); }}>Cavalo Mecânico</button>
                    <button className={`flex-1 py-2 text-sm rounded-md font-medium ${tipoAtivo === 'carreta' ? 'bg-sky-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}`} onClick={() => { setTipoAtivo('carreta'); setForm(s => ({ ...s, veiculo_id: '', carreta_id: '' })); setHodometroAtual(null); }}>Carreta / Semi</button>
                  </div>

                  {/* Ativo e Família */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">{tipoAtivo === 'cavalo' ? 'Cavalo Mecânico' : 'Carreta'}</Label>
                      {tipoAtivo === 'cavalo' ? (
                        <FieldSelect value={form.veiculo_id} onChange={(v) => { setForm(s => ({ ...s, veiculo_id: v })); buscarHodometro(v, 'cavalo'); }} options={(veiculos.data ?? []).map((v: any) => ({ value: v.id, label: `${v.placa} - ${v.modelo}` }))} placeholder="Selecione..." />
                      ) : (
                        <FieldSelect value={form.carreta_id} onChange={(v) => { setForm(s => ({ ...s, carreta_id: v })); buscarHodometro(v, 'carreta'); }} options={carretas.map((c: any) => ({ value: c.id, label: `${c.codigo} - ${c.tipo}` }))} placeholder="Selecione..." />
                      )}
                    </div>
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Família de Componentes</Label>
                      <select value={form.familia} onChange={(e) => setForm(s => ({ ...s, familia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                        {FAMILIAS.map(f => <option key={f.nome} value={f.nome}>{f.nome}</option>)}
                      </select>
                    </div>
                  </div>

                  {/* Descrição */}
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400">Descrição do Serviço</Label>
                    <Input value={form.descricao} onChange={(e) => setForm(s => ({ ...s, descricao: e.target.value }))} placeholder="Ex: Revisão Periódica de 40.000 km" className="h-9" />
                  </div>

                  {/* Gatilho e Recorrência */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1">
                        Tipo de Gatilho
                        <div className="group relative"><HelpCircle className="size-3 text-slate-500 cursor-help" /><div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50"><p className="font-bold text-sky-400 mb-1">Base da Manutenção</p><p><strong>KM:</strong> Para motores e rodagem.</p><p><strong>Horas:</strong> Para equipamentos com PTO.</p><p><strong>Tempo:</strong> Para itens que degradam com o tempo.</p></div></div>
                      </Label>
                      <select value={form.tipo_gatilho} onChange={(e) => setForm(s => ({ ...s, tipo_gatilho: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                        {TIPOS_GATILHO.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                      </select>
                    </div>
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1">
                        Recorrência
                        <div className="group relative"><HelpCircle className="size-3 text-slate-500 cursor-help" /><div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50"><p className="font-bold text-sky-400 mb-1">Periodicidade</p><p><strong>Periódico:</strong> Repete a cada intervalo.</p><p><strong>Vitalício:</strong> Feito uma única vez.</p></div></div>
                      </Label>
                      <select value={form.tipo_recorrencia} onChange={(e) => setForm(s => ({ ...s, tipo_recorrencia: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                        <option value="periodico">Periódico (Repete)</option>
                        <option value="vitalicio">Vitalício (Única vez)</option>
                      </select>
                    </div>
                  </div>

                  {/* Intervalo e Unidade de Tempo */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1">
                        Intervalo
                        <div className="group relative"><HelpCircle className="size-3 text-slate-500 cursor-help" /><div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50">Digite a frequência (ex: 20000 km, 500 horas, 6 meses).</div></div>
                      </Label>
                      <Input type="number" value={form.intervalo} onChange={(e) => setForm(s => ({ ...s, intervalo: e.target.value }))} placeholder={form.tipo_gatilho === 'km' ? "Ex: 20000" : "Ex: 180"} className="h-9" />
                    </div>
                    {form.tipo_gatilho === 'dias' && (
                      <div className="grid gap-1.5">
                        <Label className="text-xs text-slate-400 flex items-center gap-1">
                          Unidade de Tempo
                          <div className="group relative"><HelpCircle className="size-3 text-slate-500 cursor-help" /><div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-64 bg-slate-800 border border-slate-700 text-slate-200 text-xs p-3 rounded-lg shadow-xl z-50">Escolha a unidade (dias, meses ou anos).</div></div>
                        </Label>
                        <select value={form.unidade_tempo} onChange={(e) => setForm(s => ({ ...s, unidade_tempo: e.target.value }))} className="h-9 bg-slate-950 border border-slate-700 rounded-md text-sm text-slate-300 px-2">
                          {UNIDADES_TEMPO.map(u => <option key={u.value} value={u.value}>{u.label}</option>)}
                        </select>
                      </div>
                    )}
                  </div>

                  {/* Última Execução (KM) */}
                  {form.tipo_gatilho === 'km' && (
                    <div className="grid gap-1.5">
                      <Label className="text-xs text-slate-400">Última Execução (KM)</Label>
                      <Input type="number" value={form.ultima_execucao_km} onChange={(e) => setForm(s => ({ ...s, ultima_execucao_km: e.target.value }))} className="h-9" />
                    </div>
                  )}

                  {/* Data de Abertura (Read-Only) */}
                  <div className="grid gap-1.5">
                    <Label className="text-xs text-slate-400 flex items-center gap-1"><Calendar className="size-3" /> Data de Abertura do Plano</Label>
                    <Input value={form.data_abertura ? form.data_abertura.split("-").reverse().join("/") : ""} disabled className="bg-slate-800/50 text-slate-400 cursor-not-allowed border-slate-700 h-9" />
                  </div>

                </div>
              </div>
            </div>

            {/* Rodapé */}
            <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900 rounded-b-2xl">
              <Button variant="outline" onClick={() => setOpen(false)} className="h-9">Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="h-9 bg-sky-600 hover:bg-sky-500">
                {salvar.isPending ? "Salvando..." : "Salvar Plano"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Restante do código para exclusão */}
      {excluirId && (
'''

    if padrao_modal.search(c):
        c = padrao_modal.sub(novo_modal, c, count=1)
        print("✅ Layout do modal reformulado para o padrão expandido.")
    else:
        print("⚠️ Não foi possível encontrar o bloco do modal.")

    # Importar o ícone X (se não estiver) e HelpCircle
    if 'HelpCircle' not in c.split('lucide-react')[0]:
        c = c.replace(
            'import { Wrench, Plus, Pencil, Trash2, Info, User, Gauge, Calendar }',
            'import { Wrench, Plus, Pencil, Trash2, Info, User, Gauge, Calendar, HelpCircle, X }'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso! Faça o git push.")