import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORNECEDOR_LAYOUT_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/models/fornecedores.py",
        "frontend/src/pages/Fornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

# ==========================================
# BACKEND: Adicionar empresa_id no Model
# ==========================================
def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'empresa_id' not in c:
        c = c.replace(
            'tipo_fornecedor_id: str | None = None',
            'tipo_fornecedor_id: str | None = None\n    empresa_id: str | None = None'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend Fornecedores: campo 'empresa_id' adicionado.")

# ==========================================
# FRONTEND: Reestruturar Modal
# ==========================================
def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a query de empresas
    if 'queryKey: ["empresas"]' not in c:
        c = c.replace(
            'const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });',
            'const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });\n  const { data: empresas = [] } = useQuery({ queryKey: ["empresas"], queryFn: () => apiGet<any[]>("/empresa") });'
        )

    # 2. Adicionar empresa_id no estado do form
    c = c.replace(
        'tipo_fornecedor_id: "", documento: ""',
        'tipo_fornecedor_id: "", empresa_id: "", documento: ""'
    )
    c = c.replace(
        'tipo_fornecedor_id: r.tipo_fornecedor_id || "",',
        'tipo_fornecedor_id: r.tipo_fornecedor_id || "", empresa_id: r.empresa_id || "",'
    )

    # 3. Substituir o bloco do Modal inteiro pelo layout customizado
    padrao_modal = re.compile(r'<Dialog open=\{open\} onOpenChange=\{setOpen\}>[\s\S]*?</Dialog>')
    
    novo_modal = '''
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl w-full max-w-4xl flex flex-col max-h-[90vh]">
            
            {/* Cabeçalho */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
              <h2 className="text-lg font-bold text-slate-100">{editingId ? "Editar Fornecedor" : "Novo Fornecedor"}</h2>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-white transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              </button>
            </div>

            {/* Corpo com Scroll */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="flex flex-col lg:flex-row gap-6">
                
                {/* COLUNA ESQUERDA: Avaliação e Ativo */}
                <div className="w-full lg:w-[180px] shrink-0 flex flex-col gap-6 border-r border-slate-800 pr-6">
                  <div className="flex flex-col gap-2">
                    <Label className="text-xs text-slate-400 font-semibold uppercase">Avaliação</Label>
                    <div className="flex gap-1 items-center">
                      {[1, 2, 3, 4, 5].map(star => (
                        <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110 transition-transform">
                          <Star className={`size-6 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                        </button>
                      ))}
                    </div>
                    <span className="text-[10px] text-slate-500">{form.avaliacao === 0 ? "Sem avaliação" : `${form.avaliacao} de 5`}</span>
                  </div>

                  <div className="flex items-center gap-2 mt-auto pt-4 border-t border-slate-800">
                    <input type="checkbox" checked={form.ativo} onChange={(e) => setForm(s => ({ ...s, ativo: e.target.checked }))} className="size-4 accent-sky-500" id="ativo-forn" />
                    <Label htmlFor="ativo-forn" className="text-sm font-medium text-slate-200 cursor-pointer">Fornecedor Ativo</Label>
                  </div>
                </div>

                {/* COLUNA DIREITA: Formulário */}
                <div className="flex-1 flex flex-col gap-4">
                  
                  {/* Linha 1: Tipo e Empresa */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Tipo de Fornecedor *</Label>
                      <FieldSelect value={form.tipo_fornecedor_id} onChange={(v) => setForm(s => ({ ...s, tipo_fornecedor_id: v }))} options={tipos.filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))} placeholder="Selecione o tipo..." />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Empresa / Unidade</Label>
                      <FieldSelect value={form.empresa_id} onChange={(v) => setForm(s => ({ ...s, empresa_id: v }))} options={empresas.map((e: any) => ({ value: e.id, label: e.nome_fantasia || e.razao_social }))} placeholder="Vincular a uma empresa..." />
                    </div>
                  </div>

                  {/* Linha 2: Nome e Documento */}
                  <div className="grid grid-cols-3 gap-4">
                    <div className="col-span-2 flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Nome / Razão Social *</Label>
                      <Input value={form.nome} onChange={(e) => setForm(s => ({ ...s, nome: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" required />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Documento / CNPJ</Label>
                      <Input value={form.documento} onChange={(e) => setForm(s => ({ ...s, documento: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 3: Tipo Pessoa, Telefone, Email */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Tipo Pessoa</Label>
                      <FieldSelect value={form.tipo_pessoa} onChange={(v) => setForm(s => ({ ...s, tipo_pessoa: v }))} options={[{ value: "PJ", label: "PJ" }, { value: "PF", label: "PF" }]} />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Telefone</Label>
                      <Input value={form.telefone} onChange={(e) => setForm(s => ({ ...s, telefone: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="col-span-2 flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">E-mail</Label>
                      <Input type="email" value={form.email} onChange={(e) => setForm(s => ({ ...s, email: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 4: Contato e WhatsApp */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Contato</Label>
                      <Input value={form.contato} onChange={(e) => setForm(s => ({ ...s, contato: e.target.value }))} placeholder="Nome do contato" className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400 flex items-center gap-1"><MessageCircle className="size-3 text-emerald-500" /> WhatsApp</Label>
                      <Input value={form.whatsapp} onChange={(e) => setForm(s => ({ ...s, whatsapp: e.target.value }))} placeholder="(00) 00000-0000" className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                  </div>

                  {/* Linha 5: Endereço */}
                  <div className="flex flex-col gap-1.5">
                    <Label className="text-xs text-slate-400">Endereço</Label>
                    <Input value={form.endereco} onChange={(e) => setForm(s => ({ ...s, endereco: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                  </div>

                  {/* Linha 6: Bairro, Cidade, UF */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Bairro</Label>
                      <Input value={form.bairro} onChange={(e) => setForm(s => ({ ...s, bairro: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="col-span-2 flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">Cidade</Label>
                      <Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} className="h-9 bg-slate-950 border-slate-700" />
                    </div>
                    <div className="flex flex-col gap-1.5">
                      <Label className="text-xs text-slate-400">UF</Label>
                      <Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="h-9 bg-slate-950 border-slate-700 uppercase" />
                    </div>
                  </div>

                </div>
              </div>
            </div>

            {/* Rodapé */}
            <div className="flex items-center justify-end px-6 py-4 border-t border-slate-800 gap-3 bg-slate-900/50">
              <Button variant="outline" onClick={() => setOpen(false)} className="h-9">Cancelar</Button>
              <Button onClick={() => salvar.mutate()} disabled={salvar.isPending || !form.nome || !form.tipo_fornecedor_id} className="h-9 bg-sky-600 hover:bg-sky-500 font-semibold">
                {salvar.isPending ? "Salvando..." : (editingId ? "Salvar Alterações" : "Cadastrar Fornecedor")}
              </Button>
            </div>
          </div>
        </div>
      )}
'''
    
    if padrao_modal.search(c):
        c = padrao_modal.sub(novo_modal, c)
        print("✅ Layout do Modal refeito no padrão Empresa.")
    else:
        print("⚠️ Não foi possível encontrar o bloco do Dialog no código.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Todos os scripts aplicados! Faça o git push.")