import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ORDEM_FINAL_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def remover_bloco(c, nome):
    padrao = re.compile(rf'const {nome} = useMemo\(\(\) => \{{[\s\S]*?\}}, \[[^\]]*\]\);', re.DOTALL)
    return padrao.sub('', c)

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remove os blocos que precisam ser reordenados (só os que existem)
    for nome in ['rowsOrdenadas', 'produtoOpts', 'rowsFiltradas']:
        c = remover_bloco(c, nome)
    print("✅ Blocos de useMemo removidos para reordenar.")

    # 2. Localiza a declaração de 'rows' (ponto de inserção)
    padrao_rows = re.compile(r'const rows = q\.isError \? \[\] : \(q\.data \?\? \[\]\);')
    match_rows = padrao_rows.search(c)
    if match_rows:
        idx_inserir = match_rows.end()
        print("✅ Ponto de inserção encontrado após 'rows'.")
    else:
        # Fallback: tenta encontrar 'const rows =' (qualquer)
        idx_inserir = c.find('const rows = ')
        if idx_inserir == -1:
            print("⚠️ 'rows' não encontrado. Inserindo antes do return?")
            idx_inserir = c.find('  return (')
        else:
            idx_inserir = c.find('\n', idx_inserir) + 1
        print(f"✅ Ponto de inserção alternativo: posição {idx_inserir}.")

    # 3. Bloco definitivo na ORDEM CORRETA
    blocos = '''  const rowsOrdenadas = useMemo(() => {
    return [...rows].sort((a, b) => {
      const d1 = a.data.split("-").join("");
      const d2 = b.data.split("-").join("");
      if (d1 !== d2) return d2.localeCompare(d1);
      return (b.created_at || "").localeCompare(a.created_at || "");
    });
  }, [rows]);

  const produtoOpts = useMemo(() => {
    const unicos = Array.from(new Set(rows.map(r => r.produto).filter(Boolean)));
    return [{ value: TODOS, label: "Todos" }, ...unicos.map(p => ({ value: p, label: p }))];
  }, [rows]);

  const rowsFiltradas = useMemo(() => {
    return rowsOrdenadas.filter(r => {
      if (filtroVeiculo !== TODOS && r.veiculo_id !== filtroVeiculo) return false;
      if (filtroMotorista !== TODOS && r.motorista_id !== filtroMotorista) return false;
      if (filtroPosto && !(r.fornecedor || r.posto || "").toLowerCase().includes(filtroPosto.toLowerCase())) return false;
      if (filtroNF !== TODOS) {
        if (filtroNF === "com" && !r.numero_nf) return false;
        if (filtroNF === "sem" && r.numero_nf) return false;
      }
      if (filtroProduto !== TODOS && r.produto !== filtroProduto) return false;
      return true;
    });
  }, [rowsOrdenadas, filtroVeiculo, filtroMotorista, filtroPosto, filtroNF, filtroProduto]);

'''

    # 4. Insere na posição correta
    c = c[:idx_inserir] + blocos + c[idx_inserir:]

    # 5. Garantir que o estado filtroProduto exista
    if 'const [filtroProduto, setFiltroProduto] = useState(TODOS);' not in c:
        c = c.replace(
            'const [filtroPosto, setFiltroPosto] = useState("");',
            'const [filtroPosto, setFiltroPosto] = useState("");\n  const [filtroProduto, setFiltroProduto] = useState(TODOS);'
        )
        print("✅ Estado filtroProduto adicionado.")

    # 6. Garantir que o campo visual de Produto existe
    if '<Label>Produto</Label>' not in c:
        if '<Label>Posto</Label>' in c:
            c = c.replace(
                '<div className="grid w-48 gap-1.5"><Label>Posto</Label>',
                '''<div className="grid w-48 gap-1.5"><Label>Produto</Label><FieldSelect value={filtroProduto} onChange={setFiltroProduto} options={produtoOpts} placeholder="Todos" /></div>
        <div className="grid w-48 gap-1.5"><Label>Posto</Label>'''
            )
            print("✅ Campo visual de Produto adicionado.")

    # 7. Atualizar o botão "Limpar Filtros"
    c = c.replace(
        'setFiltroPosto(""); setFiltroNF(TODOS);',
        'setFiltroPosto(""); setFiltroProduto(TODOS); setFiltroNF(TODOS);'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Pipeline de dados reescrito na ordem correta!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)