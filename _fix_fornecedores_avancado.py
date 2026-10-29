import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORNECEDORES_AVANCADO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/models/parametrizacao.py",
        "app/backend/routers/parametrizacao.py",
        "app/backend/models/fornecedores.py",
        "frontend/src/pages/Parametrizacao.tsx",
        "frontend/src/pages/Fornecedores.tsx",
        "frontend/src/pages/TiposFornecedores.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Parametrização (Model)
    path_model = os.path.join(raiz, "app", "backend", "models", "parametrizacao.py")
    if os.path.exists(path_model):
        with open(path_model, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'mostrar_seed_fornecedores' not in c:
            c = c.replace(
                'meta_abastecimento_valor: float = 2.5',
                'meta_abastecimento_valor: float = 2.5\n    mostrar_seed_fornecedores: bool = False'
            )
            with open(path_model, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Model Parametrização atualizado.")

    # 2. Parametrização (Router)
    path_router = os.path.join(raiz, "app", "backend", "routers", "parametrizacao.py")
    if os.path.exists(path_router):
        with open(path_router, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'mostrar_seed_fornecedores' not in c:
            c = c.replace(
                'meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5)',
                'meta_abastecimento_valor=config.get("meta_abastecimento_valor", 2.5),\n        mostrar_seed_fornecedores=config.get("mostrar_seed_fornecedores", False)'
            )
            c = c.replace(
                '"meta_abastecimento_valor": body.meta_abastecimento_valor,',
                '"meta_abastecimento_valor": body.meta_abastecimento_valor,\n            "mostrar_seed_fornecedores": body.mostrar_seed_fornecedores,'
            )
            with open(path_router, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Router Parametrização atualizado.")

    # 3. Fornecedores (Model)
    path_model_f = os.path.join(raiz, "app", "backend", "models", "fornecedores.py")
    if os.path.exists(path_model_f):
        with open(path_model_f, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'tipo_fornecedor_id' not in c:
            c = re.sub(r'(class Fornecedor.*?:\n)', r'\1    tipo_fornecedor_id: str | None = None\n', c, count=1)
            with open(path_model_f, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Model Fornecedor atualizado com tipo_fornecedor_id.")

def fix_parametrizacao_front(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "Parametrizacao.tsx")
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adicionar estado
    if 'mostrar_seed_fornecedores' not in c:
        c = c.replace(
            'const [valor, setValor] = useState("2,5");',
            'const [valor, setValor] = useState("2,5");\n  const [mostrarSeed, setMostrarSeed] = useState(false);'
        )
        c = c.replace(
            'setValor(String(config.meta_abastecimento_valor).replace(".", ","));',
            'setValor(String(config.meta_abastecimento_valor).replace(".", ","));\n      setMostrarSeed(config.mostrar_seed_fornecedores || false);'
        )
        c = c.replace(
            'meta_abastecimento_valor: Number(String(valor).replace(",", ".")),',
            'meta_abastecimento_valor: Number(String(valor).replace(",", ".")),\n      mostrar_seed_fornecedores: mostrarSeed,'
        )

    # Adicionar a linha na tabela
    if 'Botão Popular Lista Base' not in c:
        nova_linha = '''<TableRow className="border-slate-800">
              <TableCell className="font-medium text-slate-200">
                Exibir botão "Popular Lista Base" na tela de Tipos de Fornecedores
              </TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={() => setMostrarSeed(!mostrarSeed)}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold transition-all ${
                    mostrarSeed
                      ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                      : "bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  }`}
                >
                  {mostrarSeed ? <CheckCircle2 className="size-3" /> : <XCircle className="size-3" />}
                  {mostrarSeed ? "Visível" : "Oculto"}
                </button>
              </TableCell>
              <TableCell colSpan={2} className="text-xs text-slate-500 italic">Útil apenas para setup inicial do sistema.</TableCell>
            </TableRow>
            </TableBody>'''
        c = c.replace('</TableBody>', nova_linha)
        print("✅ Frontend Parametrização atualizado.")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_tipos_fornecedores_front(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "TiposFornecedores.tsx")
    if not os.path.exists(path): return
    
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar pesquisa e esconder o botão Seed baseado na config
    if 'const [searchTerm, setSearchTerm]' not in c:
        c = c.replace(
            'const [form, setForm] = useState({ nome: "", categoria_pai_id: "" });',
            'const [form, setForm] = useState({ nome: "", categoria_pai_id: "" });\n  const [searchTerm, setSearchTerm] = useState("");\n  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });'
        )
        
        # Filtro
        c = c.replace(
            'const rows = q.data || [];',
            '''const rows = q.data || [];
  const rowsFiltradas = rows.filter(r => r.nome.toLowerCase().includes(searchTerm.toLowerCase()));'''
        )

        # Esconder o botão seed
        c = c.replace(
            'actions={<div className="flex gap-2">',
            'actions={<div className="flex gap-2">\n          {config?.mostrar_seed_fornecedores && (\n            <Button variant="outline" onClick={popularLista} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10">\n              <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Lista Base"}\n            </Button>\n          )}'
        )
        
        # Remover o botão antigo duplicado (se existir)
        c = re.sub(r'<Button variant="outline" onClick=\{popularLista\}.*?Popular Lista Base.*?</Button>', '', c, count=1, flags=re.DOTALL)
        
        # Injetar a Barra de Pesquisa acima da Tabela
        c = c.replace(
            '<div className="glass overflow-hidden rounded-2xl mt-4">',
            '''<div className="mb-4 flex gap-2">
        <Input 
          placeholder="Pesquisar por categoria ou tipo..." 
          value={searchTerm} 
          onChange={e => setSearchTerm(e.target.value)} 
          className="w-72" 
        />
      </div>
      
      <div className="glass overflow-hidden rounded-2xl mt-4">'''
        )

        # Atualizar o map para usar rowsFiltradas
        c = c.replace(
            'rows.filter(r => !r.categoria_pai_id).map(cat => (',
            'rowsFiltradas.filter(r => !r.categoria_pai_id).map(cat => ('
        )
        c = c.replace(
            'rows.filter(r => r.categoria_pai_id === cat.id).map(sub => (',
            'rowsFiltradas.filter(r => r.categoria_pai_id === cat.id).map(sub => ('
        )
        print("✅ Frontend TiposFornecedores atualizado com pesquisa e controle de visibilidade.")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_fornecedores_cadastro(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    if not os.path.exists(path): return

    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Query dos tipos de fornecedores
    if 'queryKey: ["tipos-fornecedores"]' not in c:
        c = c.replace(
            'const fornecedoresQ = useQuery(',
            'const tiposQ = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });\n  const fornecedoresQ = useQuery('
        )
        # 2. Estado do formulário (tipo_fornecedor_id)
        c = c.replace(
            'nome: "", documento: "",',
            'nome: "", tipo_fornecedor_id: "", documento: "",'
        )
        # 3. Injeção do FieldSelect no Modal (antes do campo Documento/CNPJ)
        c = c.replace(
            '<Label>Documento / CNPJ</Label>',
            '''<Label>Tipo de Fornecedor</Label>
              <FieldSelect 
                value={form.tipo_fornecedor_id || ""} 
                onChange={(v) => setForm(s => ({ ...s, tipo_fornecedor_id: v }))} 
                options={(tiposQ.data || []).filter((t:any) => t.categoria_pai_id).map((t:any) => ({ value: t.id, label: t.nome }))} 
                placeholder="Selecione o tipo (Opcional)" 
              />
            </div>
            <div className="grid gap-1.5">
              <Label>Documento / CNPJ</Label>'''
        )
        print("✅ Frontend Fornecedores atualizado com campo de Tipo.")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_parametrizacao_front(raiz)
    fix_tipos_fornecedores_front(raiz)
    fix_fornecedores_cadastro(raiz)
    print("\n✅ Todos os scripts aplicados com sucesso! Faça o git push.")