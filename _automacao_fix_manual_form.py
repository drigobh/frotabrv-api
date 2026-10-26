import os
import re

def fix_backend(raiz):
    # 1. Adiciona cidade e estado no Modelo
    caminho_model = os.path.join(raiz, "app", "backend", "models", "abastecimentos.py")
    with open(caminho_model, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'cidade' not in c:
        c = c.replace('cnpj: str | None = None', 'cnpj: str | None = None\n    cidade: str | None = None\n    estado: str | None = None')
        with open(caminho_model, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Modelo atualizado com cidade e estado.")

    # 2. Adiciona cidade e estado no Router de Importação
    caminho_router = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho_router, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if '"cidade": body.get("cidade")' not in c:
        c = c.replace(
            '"cnpj": body.get("cnpj"),',
            '"cnpj": body.get("cnpj"),\n        "cidade": body.get("cidade"),\n        "estado": body.get("estado"),'
        )
        with open(caminho_router, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Router atualizado para salvar cidade e estado.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adiciona Imports necessários se não existirem
    if 'Search' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus', 'import { Fuel, Plus, Search, Loader2')
    if 'useQuery' not in c.split('@tanstack/react-query')[0]:
        c = c.replace('import { useMutation, useQueryClient }', 'import { useMutation, useQuery, useQueryClient }')

    # 2. Adiciona o estado de CNPJ e a Query de Fornecedores
    if 'cnpjLoading' not in c:
        c = c.replace(
            'const [excluirId, setExcluirId] = useState<string | null>(null);',
            '''const [excluirId, setExcluirId] = useState<string | null>(null);
  const [cnpjLoading, setCnpjLoading] = useState(false);
  const [fornecedorPendente, setFornecedorPendente] = useState<{nome: string, cnpj: string, cidade: string, estado: string} | null>(null);
  const { data: fornecedores = [], refetch: refetchFornecedores } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });'''
        )

    # 3. Adiciona a função formatCnpj
    if 'const formatCnpj = ' not in c:
        c = c.replace(
            'const vazio = (hoje: string) =>',
            '''const formatCnpj = (val: string) => {
  return val.replace(/\\D/g, '')
    .replace(/^(\\d{2})(\\d)/, '$1.$2')
    .replace(/^(\\d{2})\\.(\\d{3})(\\d)/, '$1.$2.$3')
    .replace(/\\.(\\d{3})(\\d)/, '.$1/$2')
    .replace(/(\\d{4})(\\d)/, '$1-$2')
    .slice(0, 18);
};

const vazio = (hoje: string) =>'''
        )

    # 4. Adiciona a lógica de buscar CNPJ e cadastrar fornecedor
    if 'const buscarCnpj = ' not in c:
        c = c.replace(
            'const invalidate = () => {',
            '''const buscarCnpj = async () => {
    const cnpjLimpo = form.cnpj.replace(/\\D/g, "");
    if (cnpjLimpo.length !== 14) { toast.error("CNPJ inválido"); return; }
    setCnpjLoading(true);
    try {
      const existente = fornecedores.find((f: any) => f.cnpj && f.cnpj.replace(/\\D/g, '') === cnpjLimpo);
      if (existente) {
        setForm(s => ({ ...s, fornecedor: existente.nome, cidade: existente.cidade || "", estado: existente.estado || "" }));
        toast.success(`Fornecedor encontrado: ${existente.nome}`);
        return;
      }
      const res = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpjLimpo}`);
      if (!res.ok) throw new Error("Erro na API");
      const data = await res.json();
      setFornecedorPendente({ nome: data.razao_social, cnpj: formatCnpj(cnpjLimpo), cidade: data.municipio, estado: data.uf });
    } catch (err) {
      toast.error("Erro ao buscar CNPJ.");
    } finally {
      setCnpjLoading(false);
    }
  };

  const confirmarCadastroFornecedor = async () => {
    if (!fornecedorPendente) return;
    try {
      await apiPost("/fornecedores", { ...fornecedorPendente, ativo: true });
      toast.success("Fornecedor cadastrado automaticamente!");
      await refetchFornecedores();
      setForm(s => ({ ...s, fornecedor: fornecedorPendente.nome, cidade: fornecedorPendente.cidade, estado: fornecedorPendente.estado }));
      setFornecedorPendente(null);
    } catch (err) {
      toast.error("Erro ao cadastrar fornecedor.");
    }
  };

  const invalidate = () => {'''
        )

    # 5. Atualiza o payload de salvar para incluir cidade e estado
    c = c.replace(
        'const payload = { data: form.data, veiculo_id: form.veiculo_id,',
        'const payload = { data: form.data, veiculo_id: form.veiculo_id, cidade: form.cidade, estado: form.estado,'
    )

    # 6. Reordena o Formulário e adiciona a busca de CNPJ
    # Encontra o bloco do formulário atual
    padrao_form = re.compile(r'<form className="grid grid-cols-2 gap-3"[\s\S]*?</form>', re.DOTALL)
    
    novo_form = r'''<form className="grid grid-cols-2 gap-3" onSubmit={(e) => { e.preventDefault(); salvar.mutate(); }}>
              <div className="col-span-2 grid gap-1.5"><Label>Veículo *</Label><FieldSelect value={form.veiculo_id} onChange={handleVeiculoChange} options={veicOpts} placeholder="Selecione o veículo primeiro" testId="form-veiculo" /></div>
              <div className="col-span-2 grid gap-1.5"><Label>Motorista</Label><FieldSelect value={form.motorista_id} onChange={set("motorista_id")} options={[{ value: NENHUM, label: "— Nenhum —" }, ...(motoristas.data ?? []).filter((m: any) => m.ativo).map((m: any) => ({ value: m.id, label: m.nome }))]} testId="form-motorista" /></div>

              <div className="grid gap-1.5"><Label>Data *</Label><Input type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required /></div>
              <div className="grid gap-1.5"><Label>Hodômetro *</Label><Input type="number" value={form.km} onChange={(e) => set("km")(e.target.value)} required /></div>
              
              <div className="grid gap-1.5"><Label>Litros *</Label><Input inputMode="decimal" value={form.litros} onChange={(e) => set("litros")(e.target.value)} required /></div>
              <div className="grid gap-1.5"><Label>Preço/L *</Label><Input inputMode="decimal" value={form.preco_litro} onChange={(e) => set("preco_litro")(e.target.value)} required /></div>
              
              <div className="col-span-2 grid gap-1.5"><Label>Posto *</Label><Input value={form.posto} onChange={(e) => set("posto")(e.target.value)} required /></div>

              <div className="col-span-2 border-t border-slate-800 pt-2 mt-2">
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-1.5">
                    <Label>CNPJ Emitente</Label>
                    <div className="flex gap-2">
                      <Input value={form.cnpj} onChange={(e) => setForm(s => ({ ...s, cnpj: formatCnpj(e.target.value) }))} placeholder="00.000.000/0000-00" maxLength={18} />
                      <Button type="button" variant="secondary" onClick={buscarCnpj} disabled={cnpjLoading || form.cnpj.length < 18} className="px-3">
                        {cnpjLoading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
                      </Button>
                    </div>
                  </div>
                  <div className="grid gap-1.5">
                    <Label>Fornecedor *</Label>
                    <FieldSelect value={form.fornecedor} onChange={(v) => {
                      const f = fornecedores.find((x:any) => x.nome === v);
                      setForm(s => ({ ...s, fornecedor: v, cnpj: f ? f.cnpj : s.cnpj, cidade: f ? f.cidade || "" : s.cidade, estado: f ? f.estado || "" : s.estado }));
                    }} options={(fornecedores ?? []).map((f: any) => ({ value: f.nome, label: f.nome }))} placeholder="Selecione o fornecedor" />
                  </div>
                  <div className="grid gap-1.5"><Label>Cidade</Label><Input value={form.cidade} onChange={(e) => setForm(s => ({ ...s, cidade: e.target.value }))} /></div>
                  <div className="grid gap-1.5"><Label>Estado (UF)</Label><Input value={form.estado} onChange={(e) => setForm(s => ({ ...s, estado: e.target.value }))} maxLength={2} className="uppercase" /></div>
                </div>
              </div>

              <div className="grid gap-1.5"><Label>Nº NF</Label><Input value={form.numero_nf} onChange={(e) => setForm(s => ({ ...s, numero_nf: e.target.value }))} /></div>
              <div className="grid gap-1.5"><Label>Hora</Label><Input type="time" value={form.hora} onChange={(e) => setForm(s => ({ ...s, hora: e.target.value }))} /></div>
              <div className="col-span-2 grid gap-1.5"><Label>Chave NF-e</Label><Input value={form.chave_nfe} onChange={(e) => setForm(s => ({ ...s, chave_nfe: e.target.value }))} /></div>
              
              <p className="col-span-2 rounded-lg bg-slate-950/60 p-3 text-sm">Valor total: <span className="font-semibold text-slate-50">{Number.isFinite(total) ? brl(total) : "—"}</span></p>
              <DialogFooter className="col-span-2"><Button type="submit" disabled={salvar.isPending || !form.veiculo_id}>{editingId ? "Salvar" : "Registrar"}</Button></DialogFooter>
            </form>'''

    if padrao_form.search(c):
        c = padrao_form.sub(lambda m: novo_form, c)
    else:
        print("⚠️ Não foi possível encontrar o formulário para substituir.")

    # 7. Adiciona o Dialog de confirmação de Fornecedor
    if 'confirmarCadastroFornecedor' in c and '<Dialog open={fornecedorPendente !== null}' not in c:
        dialog_confirm = r'''
      <Dialog open={fornecedorPendente !== null} onOpenChange={(o) => !o && setFornecedorPendente(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Fornecedor não encontrado</DialogTitle>
            <DialogDescription>
              O CNPJ {fornecedorPendente?.cnpj} não está cadastrado no sistema.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-2">
            <p className="text-sm text-slate-300"><strong>Nome:</strong> {fornecedorPendente?.nome}</p>
            <p className="text-sm text-slate-300"><strong>Cidade/UF:</strong> {fornecedorPendente?.cidade} / {fornecedorPendente?.estado}</p>
            <p className="text-sm text-sky-400 font-medium mt-2">Deseja cadastrá-lo automaticamente no sistema?</p>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setFornecedorPendente(null)}>Cancelar</Button>
            <Button onClick={confirmarCadastroFornecedor}>Sim, Cadastrar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      '''
        c = c.replace('<ConfirmDialog open={excluirId !== null}', dialog_confirm + '<ConfirmDialog open={excluirId !== null}')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Formulário manual corrigido e lógica de CNPJ adicionada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)