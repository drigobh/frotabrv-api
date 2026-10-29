import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_EMPRESA_CNPJ_{agora}.zip")
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

    # 1. Adicionar o estado de carregamento da busca (isSearching)
    if 'isSearching' not in c:
        c = c.replace(
            'const [form, setForm] = useState<any>({',
            'const [isSearching, setIsSearching] = useState(false);\n  const [form, setForm] = useState<any>({'
        )

    # 2. Adicionar a função de buscar CNPJ
    if 'const buscarCNPJ =' not in c:
        funcao_busca = '''
  const buscarCNPJ = async () => {
    const cnpjLimpo = form.cnpj.replace(/\\D/g, '');
    if (cnpjLimpo.length !== 14) {
      return toast.error("Digite um CNPJ válido com 14 dígitos.");
    }
    
    setIsSearching(true);
    try {
      const res = await fetch(`https://brasilapi.com.br/api/cnpj/v1/${cnpjLimpo}`);
      if (!res.ok) throw new Error("CNPJ não encontrado na base da Receita.");
      const data = await res.json();
      
      setForm((s: any) => ({
        ...s,
        razao_social: data.razao_social || s.razao_social,
        nome_fantasia: data.nome_fantasia || s.nome_fantasia,
        cep: data.cep || s.cep,
        endereco: data.logradouro ? `${data.logradouro}, ${data.numero}` : s.endereco,
        bairro: data.bairro || s.bairro,
        cidade: data.municipio || s.cidade,
        estado: data.uf || s.estado,
        telefone: data.ddd_telefone_1 || s.telefone,
        email: data.email || s.email
      }));
      toast.success("Dados preenchidos com sucesso!");
    } catch (err: any) {
      toast.error(err.message || "Erro ao buscar o CNPJ.");
    } finally {
      setIsSearching(false);
    }
  };
'''
        idx = c.find('  const salvar =')
        if idx != -1:
            c = c[:idx] + funcao_busca + c[idx:]

    # 3. Injetar o botão de busca ao lado do input de CNPJ
    # Substitui a div do CNPJ para incluir um flex-row com o input e o botão
    if 'onClick={buscarCNPJ}' not in c:
        alvo = '<div className="grid gap-1.5"><Label className="text-xs">CNPJ *</Label><Input value={form.cnpj} onChange={e => setForm((s: any) => ({ ...s, cnpj: e.target.value }))} className="h-9" required /></div>'
        
        novo = '''<div className="grid gap-1.5">
              <Label className="text-xs">CNPJ *</Label>
              <div className="flex gap-2">
                <Input 
                  value={form.cnpj} 
                  onChange={e => setForm((s: any) => ({ ...s, cnpj: e.target.value }))} 
                  placeholder="00.000.000/0000-00"
                  className="h-9 flex-1" 
                  required 
                />
                <Button 
                  type="button" 
                  onClick={buscarCNPJ} 
                  disabled={isSearching} 
                  className="h-9 px-3 bg-sky-600 hover:bg-sky-500"
                >
                  <Search className="size-4" />
                </Button>
              </div>
            </div>'''
        
        if alvo in c:
            c = c.replace(alvo, novo)
            print("✅ Botão de buscar CNPJ adicionado.")
        else:
            print("⚠️ Não encontrei o campo CNPJ exato. Verifique a estrutura.")

    # 4. Adicionar as opções no FieldSelect do Tipo de Unidade
    if '"Ponto de Apoio"' not in c:
        c = c.replace(
            'options={[{ value: "Matriz", label: "Matriz" }, { value: "Filial", label: "Filial" }]}',
            'options={[{ value: "Matriz", label: "Matriz" }, { value: "Filial", label: "Filial" }, { value: "Ponto de Apoio", label: "Ponto de Apoio" }, { value: "Parceiro", label: "Parceiro" }]}'
        )
        print("✅ Novas opções de unidade adicionadas (Ponto de Apoio, Parceiro).")

    # 5. Importar o ícone Search se não existir
    if 'Search' not in c.split('lucide-react')[0]:
        c = c.replace('import { Building,', 'import { Search, Building,')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)