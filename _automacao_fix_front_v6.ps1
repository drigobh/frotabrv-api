$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# 1. Corrigir a exibição de litros (sem arredondar, usando 3 casas)
$content = $content -replace 'num\(r\.litros, 1\)', 'num(r.litros, 3)'

# 2. Corrigir a exibição de preço (com R$)
$content = $content -replace 'num\(r\.preco_litro, 2\)', 'brl(r.preco_litro)'

# 3. Corrigir a origem para excel
$content = $content -replace 'origem: "manual",', 'origem: "excel",'

# 4. Corrigir o ícone (adicionar excel)
$content = $content -replace 'r\.origem === "pdf" \? \(\s*<span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>\s*\) : \(', 'r.origem === "pdf" ? (\n                    <span className="inline-flex items-center justify-center rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold text-red-400" title="Importado via PDF">PDF</span>\n                  ) : r.origem === "excel" ? (\n                    <span className="inline-flex items-center justify-center rounded bg-emerald-500/20 px-2 py-0.5 text-xs font-bold text-emerald-400" title="Importado via Excel">XLS</span>\n                  ) : ('

Set-Content -Path $file -Value $content -Encoding UTF8
Write-Host "✅ Frontend: Litros, Preço, Origem e Ícone corrigidos." -ForegroundColor Green