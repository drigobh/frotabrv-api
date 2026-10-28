import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PIPELINE_{agora}.zip")
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

    # 1. Localizar o bloco entre "const rows = " e "  return ("
    # Vamos substituir TODO o pipeline de dados de uma vez
    idx_inicio = c.find('const rows = ')
    idx_fim = c.find('  return (')
    
    if idx_inicio == -1 or idx_fim == -1:
        print("⚠️ Blocos não encontrados.")
        return

    # Manter o começo do arquivo e o final (do return para baixo)
    antes = c[:idx_inicio]
    depois = c[idx_fim:]

    # Bloco limpo e correto
    bloco_limpo = '''const rows = q.isError ? [] : (q.data ?? []);

  const produtoOpts = useMemo(() => {
    const unicos = Array.from(new Set(rows.map(r => r.produto).filter(Boolean)));
    return [{ value: TODOS, label: "Todos" }, ...unicos.map(p => ({ value: p, label: p }))];
  }, [rows]);

  const rowsOrdenadas = useMemo(() => {
    return [...rows].sort((a, b) => {
      const d1 = a.data.split("-").join("");
      const d2 = b.data.split("-").join("");
      if (d1 !== d2) return d2.localeCompare(d1);
      return (b.created_at || "").localeCompare(a.created_at || "");
    });
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

  const resumo = useMemo(() => {
    const litros = rowsFiltradas.reduce((s, r) => s + (Number(r.litros) || 0), 0);
    const valor = rowsFiltradas.reduce((s, r) => s + (Number(r.valor_total) || 0), 0);
    const km = rowsFiltradas.reduce((s, r) => s + (Number(r.km_rodados) || 0), 0);
    const comMedia = rowsFiltradas.filter(r => r.media_km_l != null && r.media_km_l > 0 && !r.produto?.toUpperCase().includes("ARLA"));
    const mediaGeral = comMedia.length > 0 ? comMedia.reduce((s, r) => s + Number(r.media_km_l), 0) / comMedia.length : 0;
    const preco = litros > 0 ? valor / litros : 0;
    const maior = rowsFiltradas.reduce((max, r) => (Number(r.valor_total) || 0) > (Number(max?.valor_total) || 0) ? r : max, null as any);
    const menor = rowsFiltradas.reduce((min, r) => (Number(r.valor_total) || 0) < (Number(min?.valor_total) || Infinity) ? r : min, null as any);
    return { 
      litros, valor, km, 
      media: litros > 0 ? km / litros : 0, 
      preco, 
      total: rowsFiltradas.length, 
      maior, 
      menor, 
      mediaValor: rowsFiltradas.length > 0 ? valor / rowsFiltradas.length : 0, 
      mediaKm: rowsFiltradas.length > 0 ? km / rowsFiltradas.length : 0, 
      custoPorKm: km > 0 ? valor / km : 0, 
      comNF: rowsFiltradas.filter(r => r.numero_nf).length, 
      semNF: rowsFiltradas.filter(r => !r.numero_nf).length,
      mediaGeral
    };
  }, [rowsFiltradas]);

  const veicOpts = (veiculos?.data || []).map((v: any) => ({ value: v.id, label: `${v.placa} · ${v.modelo}` }));

  const ranking = useMemo(() => {
    const porVeiculo: Record<string, { label: string, litros: number, km: number }> = {};
    for (const r of rowsFiltradas) {
      if (r.produto?.toUpperCase().includes("ARLA")) continue;
      if (!porVeiculo[r.veiculo_id]) {
        porVeiculo[r.veiculo_id] = { label: r.veiculo_label?.split(" · ")[0] || "—", litros: 0, km: 0 };
      }
      porVeiculo[r.veiculo_id].litros += (Number(r.litros) || 0);
      porVeiculo[r.veiculo_id].km += (Number(r.km_rodados) || 0);
    }
    return Object.values(porVeiculo)
      .map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 }))
      .filter(v => v.media > 0)
      .sort((a, b) => b.media - a.media)
      .slice(0, 5);
  }, [rowsFiltradas]);

'''

    # Montar o novo arquivo
    c = antes + bloco_limpo + depois

    # 2. Garantir que o estado filtroProduto exista
    if 'const [filtroProduto, setFiltroProduto] = useState(TODOS);' not in c:
        c = c.replace(
            'const [filtroPosto, setFiltroPosto] = useState("");',
            'const [filtroPosto, setFiltroPosto] = useState("");\n  const [filtroProduto, setFiltroProduto] = useState(TODOS);'
        )
        print("✅ Estado filtroProduto adicionado.")

    # 3. Garantir que o campo visual de Produto está no JSX
    if '<Label>Produto</Label>' not in c:
        # Insere ao lado do filtro de Posto
        if '<Label>Posto</Label>' in c:
            c = c.replace(
                '<div className="grid w-48 gap-1.5"><Label>Posto</Label>',
                '''<div className="grid w-48 gap-1.5"><Label>Produto</Label><FieldSelect value={filtroProduto} onChange={setFiltroProduto} options={produtoOpts} placeholder="Todos" /></div>
        <div className="grid w-48 gap-1.5"><Label>Posto</Label>'''
            )
            print("✅ Campo visual de Produto adicionado.")

    # 4. Atualizar o botão "Limpar Filtros" para resetar Produto
    c = c.replace(
        'setFiltroPosto(""); setFiltroNF(TODOS);',
        'setFiltroPosto(""); setFiltroProduto(TODOS); setFiltroNF(TODOS);'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Pipeline de dados reescrito com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)