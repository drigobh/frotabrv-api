import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MODAL_CUSTOM_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Empresa.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Empresa.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Empresa.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. REMOVER o Dialog do Shadcn e substituir pelo Modal Customizado
    padrao_modal = re.compile(r'<Dialog open=\{open\} onOpenChange=\{setOpen\}>[\s\S]*?</Dialog>')
    
    novo_modal = '''
      {/* MODAL CUSTOMIZADO - CONTROLE TOTAL */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-5xl flex flex-col max-h-[90vh]">
            
            {/* Cabeçalho */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h2 className="text-lg font-bold text-slate-100">{editingId ? "Editar Unidade" : "Nova Unidade"}</h2>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>

            {/* Corpo com Scroll */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex flex-col lg:flex-row gap-8">
                
                {/* COLUNA ESQUERDA: LOGO E TIPO */}
                <div className="w-full lg:w-[220px] shrink-0 flex flex-col gap-6">
                  <div className="flex flex-col items-center">
                    <div className="w-40 h-40 rounded-2xl border-2 border-dashed border-slate-700 bg-slate-950 flex items-center justify-center mb-4 overflow-hidden">
                      {form.logo_base64 ? (
                        <img src={form.logo_base64} className="w-full h-full object-contain p-2" />
                      ) : (
                        <Building className="size-14 text-slate-600" />
                      )}
                    </div>
                    <label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 w-full">
                      <Upload className="size-4" /> Alterar Logo
                      <input type="file" accept="image/*" className="hidden" onChange={handleLogo} />
                    </label>
                  </div>

                  <div className="flex flex-col gap-2">
                    <Label className="text-xs font-semibold text-slate-400 uppercase">Tipo de Unidade</Label>
                    <FieldSelect 
                      value={form.tipo_unidade} 
                      onChange={(v) => setForm((s: any) => ({ ...s, tipo_unidade: v }))} 
                      options={[
                        { value: "Matriz", label: "Matriz" }, 
                        { value: "Filial", label: "Filial" }, 
                        { value: "Ponto de Apoio", label: "Ponto de Apoio" }, 
                        { value: "Parceiro", label: "Parceiro" }
                      ]} 
                    />
                  </div>
                </div>

                {/* COLUNA DIREITA: FORMULÁRIO */}
                <div className="flex-1 flex flex-col gap-5">
                  
                  {/* Linha 1: Razão e Fantasia */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Razão Social *</Label>
                      <Input value={form.razao_social} onChange={e => setForm((s: any) => ({ ...s, razao_social: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" required />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Nome Fantasia</Label>
                      <Input value={form.nome_fantasia} onChange={e => setForm((s: any) => ({ ...s, nome_fantasia: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 2: CNPJ, IE, IM */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
                    <div className="md:col-span-2 flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">CNPJ *</Label>
                      <div className="flex gap-2">
                        <Input value={form.cnpj} onChange={e => setForm((s: any) => ({ ...s, cnpj: e.target.value }))} className="h-11 bg-slate-950 border-slate-700 flex-1" required />
                        <Button type="button" onClick={buscarCNPJ} disabled={isSearching} className="h-11 w-14 bg-sky-600 hover:bg-sky-500 shrink-0"><Search className="size-5" /></Button>
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">I.E.</Label>
                      <Input value={form.ie} onChange={e => setForm((s: any) => ({ ...s, ie: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">I.M.</Label>
                      <Input value={form.im} onChange={e => setForm((s: any) => ({ ...s, im: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 3: Endereço e CEP */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
                    <div className="md:col-span-3 flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Endereço</Label>
                      <Input value={form.endereco} onChange={e => setForm((s: any) => ({ ...s, endereco: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">CEP</Label>
                      <Input value={form.cep} onChange={e => setForm((s: any) => ({ ...s, cep: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 4: Bairro, Cidade, UF */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Bairro</Label>
                      <Input value={form.bairro} onChange={e => setForm((s: any) => ({ ...s, bairro: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="md:col-span-2 flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Cidade</Label>
                      <Input value={form.cidade} onChange={e => setForm((s: any) => ({ ...s, cidade: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">UF</Label>
                      <Input value={form.estado} onChange={e => setForm((s: any) => ({ ...s, estado: e.target.value }))} maxLength={2} className="h-11 bg-slate-950 border-slate-700 uppercase" />
                    </div>
                  </div>

                  {/* Linha 5: Telefone, Email, Maps */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">Telefone</Label>
                      <div className="flex gap-2">
                        <Input value={form.telefone} onChange={e => setForm((s: any) => ({ ...s, telefone: e.target.value }))} className="h-11 bg-slate-950 border-slate-700 flex-1" />
                        {form.endereco && form.cidade && (
                          <Button 
                            type="button" 
                            onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${form.endereco}, ${form.bairro}, ${form.cidade} - ${form.estado}`)}`, "_blank")} 
                            className="h-11 px-4 bg-slate-800 hover:bg-slate-700 text-sky-400 border border-slate-700 shrink-0"
                            title="Abrir no Google Maps"
                          >
                            <MapPin className="size-5" />
                          </Button>
                        )}
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <Label className="text-xs text-slate-400">E-mail</Label>
                      <Input value={form.email} onChange={e => setForm((s: any) => ({ ...s, email: e.target.value }))} className="h-11 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                </div>
              </div>
            </div>

            {/* Rodapé */}
            <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900/50">
              <Button variant="outline" onClick={() => setOpen(false)} className="h-11">Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending} className="h-11 bg-sky-600 hover:bg-sky-500 font-semibold">
                {salvar.isPending ? "Salvando..." : "Salvar Unidade"}
              </Button>
            </div>
          </div>
        </div>
      )}
'''

    if padrao_modal.search(c):
        c = padrao_modal.sub(novo_modal, c)
        print("✅ Layout reconstruído com modal customizado (fora do Dialog do Shadcn).")
    else:
        print("⚠️ Não foi possível encontrar o bloco do Dialog no código.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)