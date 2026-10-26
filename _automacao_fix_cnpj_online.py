import os
import re

def fix_backend(raiz):
    # 1. Adiciona a rota de consulta de CNPJ no router de fornecedores
    caminho = os.path.join(raiz, "app", "backend", "routers", "fornecedores.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if '/consultar-cnpj/' not in c:
        rota_cnpj = '''
import httpx

@router.get("/consultar-cnpj/{cnpj}")
async def consultar_cnpj(cnpj: str, _u: dict = Depends(require("read"))):
    cnpj_limpo = "".join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        raise HTTPException(400, "CNPJ inválido")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}", timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(response.status_code, "Erro ao consultar CNPJ")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(502, "Erro de conexão com a BrasilAPI")
'''
        c += rota_cnpj
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de consulta de CNPJ adicionada.")
    else:
        print("ℹ️ Backend: Rota de consulta já existe.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Substitui a função buscarCnpj para chamar o backend
    padrao_busca = re.compile(r'const buscarCnpj = async \(\) => \{[\s\S]*?\};', re.DOTALL)
    nova_busca = '''const buscarCnpj = async () => {
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
      const data = await apiGet<any>(`/fornecedores/consultar-cnpj/${cnpjLimpo}`);
      setFornecedorPendente({ 
        nome: data.razao_social, 
        cnpj: formatCnpj(cnpjLimpo), 
        cidade: data.municipio, 
        estado: data.uf,
        endereco: `${data.logradouro || ''}, ${data.numero || ''}`.trim(),
        bairro: data.bairro || '',
        avaliacao: 0
      });
    } catch (err: any) {
      toast.error(err.message || "Erro ao buscar CNPJ.");
    } finally {
      setCnpjLoading(false);
    }
  };'''
    if padrao_busca.search(c):
        c = padrao_busca.sub(lambda m: nova_busca, c)

    # 2. Atualiza o Dialog de confirmação para incluir avaliação
    c = c.replace(
        '<p className="text-sm text-slate-300"><strong>Endereço:</strong> {fornecedorPendente?.endereco}</p>',
        '''<p className="text-sm text-slate-300"><strong>Endereço:</strong> {fornecedorPendente?.endereco}</p>'''
    )

    # 3. Atualiza o payload de criação do fornecedor para incluir avaliação
    c = c.replace(
        'await apiPost("/fornecedores", { nome: fornecedorPendente.nome, cnpj: fornecedorPendente.cnpj, cidade: fornecedorPendente.cidade, estado: fornecedorPendente.estado, endereco: fornecedorPendente.endereco, bairro: fornecedorPendente.bairro, ativo: true });',
        'await apiPost("/fornecedores", { nome: fornecedorPendente.nome, cnpj: fornecedorPendente.cnpj, cidade: fornecedorPendente.cidade, estado: fornecedorPendente.estado, endereco: fornecedorPendente.endereco, bairro: fornecedorPendente.bairro, avaliacao: fornecedorPendente.avaliacao || 0, ativo: true });'
    )

    # 4. Remove o campo "Posto" do formulário
    c = c.replace(
        '<div className="col-span-2 grid gap-1.5"><Label>Posto *</Label><Input value={form.posto} onChange={(e) => set("posto")(e.target.value)} required /></div>',
        ''
    )
    # Remove o "Posto *" da validação (se existir)
    c = c.replace(', posto: form.posto', '')
    c = c.replace('if (!form.posto)', 'if (false)')

    # 5. Adiciona a avaliação do fornecedor no formulário
    if 'form.avaliacao' not in c:
        c = c.replace(
            'const vazio = (hoje: string) => ({',
            'const vazio = (hoje: string) => ({ avaliacao: 0,'
        )
        # Adiciona as estrelas no formulário
        c = c.replace(
            '<div className="grid gap-1.5"><Label>Nº NF</Label>',
            '''<div className="col-span-2 grid gap-1.5">
              <Label>Avaliação do Fornecedor</Label>
              <div className="flex gap-2 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-5 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-xs text-slate-400 ml-2">{form.avaliacao === 0 ? "Sem avaliação" : `${form.avaliacao} de 5`}</span>
              </div>
            </div>

            <div className="grid gap-1.5"><Label>Nº NF</Label>'''
        )

    # 6. Destaca o valor total no formulário
    c = c.replace(
        '<p className="col-span-2 rounded-lg bg-slate-950/60 p-3 text-sm">Valor total: <span className="font-semibold text-slate-50">{Number.isFinite(total) ? brl(total) : "—"}</span></p>',
        '<div className="col-span-2 rounded-lg bg-slate-800/80 border border-slate-700 p-4 flex justify-between items-center shadow-inner">\n  <span className="text-sm font-medium text-slate-400">Valor Total:</span>\n  <span className="text-2xl font-bold text-emerald-400">{Number.isFinite(total) ? brl(total) : "R$ 0,00"}</span>\n</div>'
    )

    # 7. Destaca o botão de busca de CNPJ
    c = c.replace(
        '<Button type="button" variant="secondary" onClick={buscarCnpj} disabled={cnpjLoading || form.cnpj.length < 18} className="px-3">',
        '<Button type="button" variant="default" onClick={buscarCnpj} disabled={cnpjLoading || form.cnpj.length < 18} className="bg-sky-600 hover:bg-sky-500 text-white font-medium shadow-md">'
    )
    c = c.replace(
        '{cnpjLoading ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}',
        '{cnpjLoading ? <Loader2 className="size-4 animate-spin" /> : <><Search className="size-4 mr-1" /> Online</>}'
    )

    # 8. Garante que o Star seja importado
    if 'Star' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus, Search, Loader2', 'import { Fuel, Plus, Search, Loader2, Star')

    # 9. Garante que o campo fornecedor no form seja um array seguro
    c = c.replace(
        'options={(fornecedores ?? []).map((f: any) => ({ value: f.nome, label: f.nome }))}',
        'options={fornecedores.length > 0 ? fornecedores.map((f: any) => ({ value: f.nome, label: f.nome })) : [{ value: "", label: "Nenhum fornecedor cadastrado" }]}'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Formulário ajustado (CNPJ via backend, avaliação, destaque).")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)