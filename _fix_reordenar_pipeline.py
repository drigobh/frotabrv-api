import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_REORDENAR_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def encontrar_bloco(c, nome):
    # Encontra a declaração e retorna (inicio, fim)
    padrao = re.compile(rf'const {nome} = useMemo\(\(\) => \{{[\s\S]*?\}}, \[[^\]]*\]\);', re.DOTALL)
    match = padrao.search(c)
    if match:
        return match.start(), match.end()
    return None, None

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remover blocos existentes (para reinserir na ordem correta)
    blocos = {}
    for nome in ['produtoOpts', 'rowsOrdenadas', 'rowsFiltradas']:
        inicio, fim = encontrar_bloco(c, nome)
        if inicio is not None:
            blocos[nome] = c[inicio:fim]
            c = c[:inicio] + c[fim:]
            print(f"✅ Bloco '{nome}' extraído.")
        else:
            print(f"⚠️ Bloco '{nome}' não encontrado.")

    # 2. Localizar onde inserir (após a declaração de 'rows')
    # Procura a linha 'const rows = q.isError ? [] : (q.data ?? []);'
    padrao_rows = re.compile(r'const rows = q\.isError \? \[\] : \(q\.data \?\? \[\]\);')
    match_rows = padrao_rows.search(c)
    if match_rows:
        idx_inserir = match_rows.end()
        print("✅ Local de inserção encontrado após 'rows'.")
    else:
        # Fallback: tenta encontrar 'const rows =' (qualquer)
        idx_inserir = c.find('const rows = ')
        if idx_inserir == -1:
            print("⚠️ 'rows' não encontrado. Inserindo antes do return?")
            idx_inserir = c.find('  return (')
        else:
            # Avança para o final da linha
            idx_inserir = c.find('\n', idx_inserir) + 1
        print(f"✅ Local de inserção alternativo: posição {idx_inserir}.")

    # 3. Montar blocos na ordem correta
    ordem = ['produtoOpts', 'rowsOrdenadas', 'rowsFiltradas']
    blocos_reordenados = ""
    for nome in ordem:
        if nome in blocos:
            blocos_reordenados += blocos[nome] + "\n\n"
        else:
            print(f"⚠️ Bloco '{nome}' não disponível para reinserção.")

    # 4. Se 'rowsOrdenadas' não existir, criar do zero
    if 'rowsOrdenadas' not in blocos:
        blocos_reordenados += '''const rowsOrdenadas = useMemo(() => {
    return [...rows].sort((a, b) => {
      const d1 = a.data.split("-").join("");
      const d2 = b.data.split("-").join("");
      if (d1 !== d2) return d2.localeCompare(d1);
      return (b.created_at || "").localeCompare(a.created_at || "");
    });
  }, [rows]);

'''
        print("✅ Bloco 'rowsOrdenadas' criado do zero.")

    # 5. Inserir de volta
    c = c[:idx_inserir] + blocos_reordenados + c[idx_inserir:]

    # 6. Garantir que 'filtroProduto' esteja no estado
    if 'const [filtroProduto, setFiltroProduto] = useState(TODOS);' not in c:
        c = c.replace(
            'const [filtroPosto, setFiltroPosto] = useState("");',
            'const [filtroPosto, setFiltroPosto] = useState("");\n  const [filtroProduto, setFiltroProduto] = useState(TODOS);'
        )
        print("✅ Estado filtroProduto adicionado.")

    # 7. Garantir que o campo visual de Produto existe
    if '<Label>Produto</Label>' not in c:
        if '<Label>Posto</Label>' in c:
            c = c.replace(
                '<div className="grid w-48 gap-1.5"><Label>Posto</Label>',
                '''<div className="grid w-48 gap-1.5"><Label>Produto</Label><FieldSelect value={filtroProduto} onChange={setFiltroProduto} options={produtoOpts} placeholder="Todos" /></div>
        <div className="grid w-48 gap-1.5"><Label>Posto</Label>'''
            )
            print("✅ Campo visual de Produto adicionado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)