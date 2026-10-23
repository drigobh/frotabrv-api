$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# 1. Corrigir a conversão de data no handleImportXLS
$content = $content -replace 'let dataStr = String\(row\[idxData\]\)\.trim\(\);', 'let dataStr = String(row[idxData]).trim();'
$content = $content -replace 'if \(dataStr\.includes\("/"\)\) \{\s*const \[d, m, y\] = dataStr\.split\("/"\);\s*dataStr = `\$\{y\}-\$\{m\}-\$\{d\}`;\s*\}', 'if (dataStr.includes("-")) { const [y, m, d] = dataStr.split(" ")[0].split("-"); dataStr = `${d}/${m}/${y}`; }'

# 2. Ajustar a leitura de litros e preço (sem divisão)
$content = $content -replace 'const litrosNum = typeof row\[idxLitros\] === .number. \? row\[idxLitros\] : parseNum\(row\[idxLitros\]\);', 'const litrosNum = typeof row[idxLitros] === "number" ? row[idxLitros] : Number(String(row[idxLitros]).replace(",", "."));'
$content = $content -replace 'const precoNum = typeof row\[idxPreco\] === .number. \? row\[idxPreco\] : parseNum\(row\[idxPreco\]\);', 'const precoNum = typeof row[idxPreco] === "number" ? row[idxPreco] : Number(String(row[idxPreco]).replace(",", "."));'
$content = $content -replace 'const litrosRaw = litrosNum / 1000;', 'const litrosRaw = litrosNum;'
$content = $content -replace 'const valorLitroRaw = precoNum / 100;', 'const valorLitroRaw = precoNum;'

# 3. Corrigir a lógica do resumo (Matemática Exata)
$oldResumo = 'const resumo = useMemo\(\(\) => \{[\s\S]*?\}, \[rows\]\);'
$newResumo = @'
  const resumo = useMemo(() => {
    const litros = rows.reduce((s, r) => s + r.litros, 0);
    const valor = rows.reduce((s, r) => s + r.valor_total, 0);
    const comKm = rows.filter((r) => r.km_rodados != null);
    const km = comKm.reduce((s, r) => s + (r.km_rodados ?? 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + r.litros, 0);
    
    const maior = rows.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rows.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rows.length ? valor / rows.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;
    const custoPorKm = km > 0 ? valor / km : 0;

    // AQUI ESTÁ A CORREÇÃO: Cálculo exato para os cards
    return { 
      litros, 
      valor, 
      km, 
      media: litrosKm > 0 ? km / litrosKm : 0, // Média Geral (KM/L) 
      preco: litros > 0 ? valor / litros : 0, // Preço Médio (R$/L)
      total: rows.length, 
      maior, 
      menor, 
      mediaValor, 
      mediaKm, 
      custoPorKm 
    };
  }, [rows]);
'@
$content = $content -replace $oldResumo, $newResumo

# 4. Corrigir a exibição de litros e preço no Grid
$content = $content -replace 'num\(r\.litros, 1\)', 'num(r.litros, 2)'
$content = $content -replace 'num\(r\.preco_litro, 2\)', 'brl(r.preco_litro)'

# 5. Corrigir a origem (Excel)
$content = $content -replace 'origem: "manual",', 'origem: "excel",'
$content = $content -replace 'r\.origem === "pdf" \? \(\s*<span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>\s*\) : \(', 'r.origem === "pdf" ? (\n                    <span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>\n                  ) : r.origem === "excel" ? (\n                    <span className="inline-flex items-center justify-center rounded bg-emerald-500/20 px-2 py-0.5 text-xs font-bold text-emerald-400" title="Importado via Excel">XLS</span>\n                  ) : ('

# 6. Ordenar a tabela por data (mais recente primeiro)
$content = $content -replace 'return rowsFinais.sort\(\(a, b\) => b.data.localeCompare\(a.data\)\);', 'return rowsFinais.sort((a, b) => new Date(b.data).getTime() - new Date(a.data).getTime());'

Set-Content -Path $file -Value $content -Encoding UTF8
Write-Host "✅ Frontend: Cálculos, Exibição e Ordenação corrigidos." -ForegroundColor Green