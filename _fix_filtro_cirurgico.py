import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FILTRO_CIRURGICO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar o estado do filtro de Produto (se não existir)
    if 'const [filtroProduto, setFiltroProduto] = useState(TODOS);' not in c:
        c = c.replace(
            'const [filtroPosto, setFiltroPosto] = useState("");',
            'const [filtroPosto, setFiltroPosto] = useState("");\n  const [filtroProduto, setFiltroProduto] = useState(TODOS);'
        )
        print("✅ Estado filtroProduto adicionado.")

    # 2. Adicionar a condição de filtro dentro do rowsFiltradas (cirúrgico)
    # Procura a linha que filtra por posto e insere a condição de produto após ela
    if 'if (filtroProduto !== TODOS && r.produto !== filtroProduto) return false;' not in c:
        c = c.replace(
            'if (filtroPosto && !r.fornecedor?.toLowerCase().includes(filtroPosto.toLowerCase())) return false;',
            '''if (filtroPosto && !r.fornecedor?.toLowerCase().includes(filtroPosto.toLowerCase())) return false;
      if (filtroProduto !== TODOS && r.produto !== filtroProduto) return false;'''
        )
        print("✅ Condição de filtro de Produto adicionada ao rowsFiltradas.")

    # 3. Adicionar 'filtroProduto' na array de dependências do rowsFiltradas
    # Procura o final do useMemo do rowsFiltradas e adiciona a dependência
    padrao_deps = re.compile(
        r'(const rowsFiltradas = useMemo\(\(\) => \{[\s\S]*?\}, \[)([^\]]*)(\]\);)',
        re.DOTALL
    )
    if padrao_deps.search(c) and 'filtroProduto' not in c.split('const rowsFiltradas = useMemo')[1][:2000]:
        def fix_deps(match):
            deps = match.group(2)
            if 'filtroProduto' not in deps:
                if deps.strip() and not deps.strip().endswith(','):
                    deps += ', '
                deps += 'filtroProduto'
            return match.group(1) + deps + match.group(3)
        c = padrao_deps.sub(fix_deps, c)
        print("✅ Dependência filtroProduto adicionada ao useMemo do rowsFiltradas.")

    # 4. Garantir que o produtoOpts exista (se não existir, adiciona antes do return)
    if 'const produtoOpts = ' not in c:
        idx_return = c.find('  return (')
        if idx_return != -1:
            c = c[:idx_return] + '''  const produtoOpts = useMemo(() => {
    const unicos = Array.from(new Set(rows.map(r => r.produto).filter(Boolean)));
    return [{ value: TODOS, label: "Todos" }, ...unicos.map(p => ({ value: p, label: p }))];
  }, [rows]);

''' + c[idx_return:]
            print("✅ produtoOpts adicionado.")

    # 5. Adicionar o campo visual de Produto (ao lado do Posto)
    if '<Label>Produto</Label>' not in c:
        if '<Label>Posto</Label>' in c:
            c = c.replace(
                '<div className="grid w-48 gap-1.5"><Label>Posto</Label>',
                '''<div className="grid w-48 gap-1.5"><Label>Produto</Label><FieldSelect value={filtroProduto} onChange={setFiltroProduto} options={produtoOpts} placeholder="Todos" /></div>
        <div className="grid w-48 gap-1.5"><Label>Posto</Label>'''
            )
            print("✅ Campo visual de Produto adicionado.")

    # 6. Garantir que o botão "Limpar Filtros" resete o Produto
    c = c.replace(
        'setFiltroPosto(""); setFiltroNF(TODOS);',
        'setFiltroPosto(""); setFiltroProduto(TODOS); setFiltroNF(TODOS);'
    )

    # 7. Adicionar trava ARLA nos Cards (resumo)
    if '!r.produto?.toUpperCase().includes("ARLA")' not in c:
        c = c.replace(
            'const comMedia = rowsFiltradas.filter(r => r.media_km_l != null && r.media_km_l > 0);',
            'const comMedia = rowsFiltradas.filter(r => r.media_km_l != null && r.media_km_l > 0 && !r.produto?.toUpperCase().includes("ARLA"));'
        )
        print("✅ Trava ARLA adicionada aos Cards.")

    # 8. Adicionar trava ARLA no Termômetro (ranking)
    # Procura o bloco do ranking e adiciona o filtro
    padrao_ranking = re.compile(
        r'(const ranking = useMemo\(\(\) => \{[\s\S]*?for \(const r of rowsFiltradas\) \{)([\s\S]*?)(if \(!porVeiculo\[r\.veiculo_id\]\))',
        re.DOTALL
    )
    if padrao_ranking.search(c) and 'r.produto?.toUpperCase().includes("ARLA")' not in c:
        c = padrao_ranking.sub(
            r'\1\n      if (r.produto?.toUpperCase().includes("ARLA")) continue;\2\3',
            c
        )
        print("✅ Trava ARLA adicionada ao Termômetro.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)