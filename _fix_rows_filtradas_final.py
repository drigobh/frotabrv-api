import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ROWS_FILTRADAS_{agora}.zip")
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

    # 1. Encontra o bloco rowsFiltradas e substitui inteiro
    padrao = re.compile(r'const rowsFiltradas = useMemo\(\(\) => \{[\s\S]*?\}, \[[^\]]*\]\);', re.DOTALL)
    
    novo_bloco = '''const rowsFiltradas = useMemo(() => {
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
  }, [rowsOrdenadas, filtroVeiculo, filtroMotorista, filtroPosto, filtroNF, filtroProduto]);'''

    if padrao.search(c):
        c = padrao.sub(novo_bloco, c)
        print("✅ Bloco rowsFiltradas reescrito com sucesso (com todos os filtros).")
    else:
        print("⚠️ Bloco rowsFiltradas não encontrado.")

    # 2. Garantir que o estado filtroProduto existe
    if 'const [filtroProduto, setFiltroProduto] = useState(TODOS);' not in c:
        c = c.replace(
            'const [filtroPosto, setFiltroPosto] = useState("");',
            'const [filtroPosto, setFiltroPosto] = useState("");\n  const [filtroProduto, setFiltroProduto] = useState(TODOS);'
        )
        print("✅ Estado filtroProduto adicionado.")

    # 3. Garantir que o campo visual do Produto está no JSX
    if '<Label>Produto</Label>' not in c:
        if '<Label>Posto</Label>' in c:
            c = c.replace(
                '<div className="grid w-48 gap-1.5"><Label>Posto</Label>',
                '''<div className="grid w-48 gap-1.5"><Label>Produto</Label><FieldSelect value={filtroProduto} onChange={setFiltroProduto} options={produtoOpts} placeholder="Todos" /></div>
        <div className="grid w-48 gap-1.5"><Label>Posto</Label>'''
            )
            print("✅ Campo visual de Produto adicionado.")

    # 4. Garantir que o produtoOpts existe
    if 'const produtoOpts = ' not in c:
        idx_return = c.find('  return (')
        if idx_return != -1:
            c = c[:idx_return] + '''  const produtoOpts = useMemo(() => {
    const unicos = Array.from(new Set(rows.map(r => r.produto).filter(Boolean)));
    return [{ value: TODOS, label: "Todos" }, ...unicos.map(p => ({ value: p, label: p }))];
  }, [rows]);

''' + c[idx_return:]
            print("✅ produtoOpts adicionado.")

    # 5. Atualizar o botão "Limpar Filtros" para resetar Produto
    c = c.replace(
        'setFiltroPosto(""); setFiltroNF(TODOS);',
        'setFiltroPosto(""); setFiltroProduto(TODOS); setFiltroNF(TODOS);'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)