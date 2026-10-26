import os
import re

def fix_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir que fornecedores seja um array
    if 'const { data: fornecedores = [], refetch: refetchFornecedores }' not in c:
        c = c.replace(
            'const [fornecedorPendente, setFornecedorPendente] = useState<{nome: string, cnpj: string, cidade: string, estado: string} | null>(null);',
            'const [fornecedorPendente, setFornecedorPendente] = useState<{nome: string, cnpj: string, cidade: string, estado: string, endereco?: string, bairro?: string} | null>(null);\n  const { data: fornecedores = [], refetch: refetchFornecedores } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });'
        )

    # 2. Atualizar a função buscarCnpj para incluir endereço e bairro
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
      const res = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpjLimpo}`);
      if (!res.ok) throw new Error("Erro na API");
      const data = await res.json();
      setFornecedorPendente({ 
        nome: data.razao_social, 
        cnpj: formatCnpj(cnpjLimpo), 
        cidade: data.municipio, 
        estado: data.uf,
        endereco: `${data.logradouro || ''}, ${data.numero || ''}`.trim(),
        bairro: data.bairro || ''
      });
    } catch (err) {
      toast.error("Erro ao buscar CNPJ.");
    } finally {
      setCnpjLoading(false);
    }
  };'''
    if padrao_busca.search(c):
        c = padrao_busca.sub(lambda m: nova_busca, c)

    # 3. Atualizar a função confirmarCadastroFornecedor para enviar todos os campos
    padrao_confirmar = re.compile(r'const confirmarCadastroFornecedor = async \(\) => \{[\s\S]*?\};', re.DOTALL)
    nova_confirmar = '''const confirmarCadastroFornecedor = async () => {
    if (!fornecedorPendente) return;
    try {
      await apiPost("/fornecedores", { 
        nome: fornecedorPendente.nome, 
        cnpj: fornecedorPendente.cnpj, 
        cidade: fornecedorPendente.cidade, 
        estado: fornecedorPendente.estado,
        endereco: fornecedorPendente.endereco,
        bairro: fornecedorPendente.bairro,
        ativo: true 
      });
      toast.success("Fornecedor cadastrado automaticamente!");
      await refetchFornecedores();
      setForm(s => ({ ...s, fornecedor: fornecedorPendente.nome, cidade: fornecedorPendente.cidade, estado: fornecedorPendente.estado }));
      setFornecedorPendente(null);
    } catch (err) {
      toast.error("Erro ao cadastrar fornecedor.");
    }
  };'''
    if padrao_confirmar.search(c):
        c = padrao_confirmar.sub(lambda m: nova_confirmar, c)

    # 4. Garantir que o FieldSelect de fornecedor use 'fornecedores' como array e tenha um "Nenhum" se vazio
    c = c.replace(
        'options={(fornecedores ?? []).map((f: any) => ({ value: f.nome, label: f.nome }))}',
        'options={fornecedores.length > 0 ? fornecedores.map((f: any) => ({ value: f.nome, label: f.nome })) : [{ value: "", label: "Nenhum fornecedor cadastrado" }]}'
    )
    
    # 5. Garantir que motoristas.data seja um array
    c = c.replace(
        '...(motoristas.data ?? []).filter((m: any) => m.ativo)',
        '...(motoristas.data || []).filter((m: any) => m.ativo)'
    )

    # 6. Adicionar campos de endereço e bairro no Dialog de confirmação (opcional, mas bom mostrar)
    c = c.replace(
        '<p className="text-sm text-slate-300"><strong>Cidade/UF:</strong> {fornecedorPendente?.cidade} / {fornecedorPendente?.estado}</p>',
        '''<p className="text-sm text-slate-300"><strong>Endereço:</strong> {fornecedorPendente?.endereco}</p>
            <p className="text-sm text-slate-300"><strong>Bairro:</strong> {fornecedorPendente?.bairro}</p>
            <p className="text-sm text-slate-300"><strong>Cidade/UF:</strong> {fornecedorPendente?.cidade} / {fornecedorPendente?.estado}</p>'''
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Abastecimentos.tsx corrigido com arrays seguros e CNPJ/Endereço.")

if __name__ == "__main__":
    fix_abastecimentos(os.getcwd())