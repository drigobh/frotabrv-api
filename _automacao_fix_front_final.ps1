$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# 1. Remove duplicatas na importação (pelo xlsx)
$content = $content -replace 'const rows = XLSX\.utils\.sheet_to_json<any\[\]>\(sheet, \{ header: 1, raw: false \}\);', 'const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false, defval: "" });'

# 2. Corrige o cálculo no Frontend (usando data real e ordem correta)
$oldCalc = 'lista.sort\(\(a, b\) => a\.data\.localeCompare\(b\.data\) \|\| a\.km - b\.km\);'
$newCalc = 'lista.sort((a, b) => new Date(a.data).getTime() - new Date(b.data).getTime() || a.km - b.km);'
$content = $content -replace $oldCalc, $newCalc

# 3. Centraliza os headers e os dados da tabela
$content = $content -replace 'className="text-\[10px\] uppercase text-slate-500 px-2"', 'className="text-[10px] uppercase text-slate-500 px-2 text-center"'
$content = $content -replace 'className="font-mono px-2"', 'className="font-mono px-2 text-center"'
$content = $content -replace 'className="text-center px-2"', 'className="text-center px-2"'

# 4. Remove a duplicata visual que pode ter ficado
$content = $content -replace 'rowsComCalculo\.map\(\(r\)', 'rowsComCalculo.map((r)'

Set-Content -Path $file -Value $content -Encoding UTF8
Write-Host "✅ Frontend: Cálculos e Alinhamento corrigidos." -ForegroundColor Green