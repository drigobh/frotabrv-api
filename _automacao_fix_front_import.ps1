$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# 1. Ajustar a conversão de data para DD/MM/YYYY
$oldDate = 'let dataStr = String\(row\[idxData\]\)\.trim\(\);'
$newDate = 'let dataStr = String(row[idxData]).trim();'
$content = $content -replace $oldDate, $newDate

# 2. Garantir que a data seja formatada corretamente
$content = $content -replace 'if \(dataStr\.includes\("/"\)\) \{\s*const \[d, m, y\] = dataStr\.split\("/"\);\s*dataStr = `\$\{y\}-\$\{m\}-\$\{d\}`;\s*\}', 'if (dataStr.includes("-")) { const [y, m, d] = dataStr.split(" ")[0].split("-"); dataStr = `${d}/${m}/${y}`; }'

# 3. Garantir que a origem seja 'excel' na importação
$content = $content -replace 'origem: "manual",', 'origem: "excel",'

# 4. Ajustar a leitura de litros e valor (a planilha manda como número ou string com vírgula)
$oldLitros = 'const litrosNum = typeof row\[idxLitros\] === .number. \? row\[idxLitros\] : parseNum\(row\[idxLitros\]\);'
$newLitros = 'const litrosNum = typeof row[idxLitros] === "number" ? row[idxLitros] : Number(String(row[idxLitros]).replace(",", "."));'
$content = $content -replace $oldLitros, $newLitros

$oldPreco = 'const precoNum = typeof row\[idxPreco\] === .number. \? row\[idxPreco\] : parseNum\(row\[idxPreco\]\);'
$newPreco = 'const precoNum = typeof row[idxPreco] === "number" ? row[idxPreco] : Number(String(row[idxPreco]).replace(",", "."));'
$content = $content -replace $oldPreco, $newPreco

# 5. Dividir litros por 1000 e preço por 100 apenas se necessário
$content = $content -replace 'const litrosRaw = litrosNum / 1000;', 'const litrosRaw = litrosNum;'
$content = $content -replace 'const valorLitroRaw = precoNum / 100;', 'const valorLitroRaw = precoNum;'

Set-Content -Path $file -Value $content -Encoding UTF8
Write-Host "✅ Frontend: Data, Litros, Valor e Origem corrigidos." -ForegroundColor Green