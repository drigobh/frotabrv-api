$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# 1. Corrigir a exibição de litros (sem arredondar)
$content = $content -replace 'num\(r\.litros, 1\)', 'num(r.litros, 3)'

# 2. Corrigir a exibição de preço (com R$)
$content = $content -replace 'num\(r\.preco_litro, 2\)', 'brl(r.preco_litro)'

# 3. Corrigir a origem para excel
$content = $content -replace 'origem: "manual",', 'origem: "excel",'

# 4. Corrigir o ícone de Excel
$content = $content -replace 'r\.origem === "pdf" \? \(', 'r.origem === "pdf" ? ('
$content = $content -replace 'r\.origem === "pdf" \? \(', 'r.origem === "pdf" ? ('
$content = $content -replace 'r\.origem === "pdf" \? \(', 'r.origem === "pdf" ? ('

Set-Content -Path $file -Value $content -Encoding UTF8
Write-Host "✅ Frontend: Exibição de litros, preço e origem corrigidos." -ForegroundColor Green