$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# 1. Corrigir o cálculo no Frontend (usar o hodometro do veículo como base se for o primeiro)
$oldCalc = 'if \(i > 0\) \{[\s\S]*?\}\s*rowsFinais\.push\(atual\);'
$newCalc = @'
if (i > 0) {
          const anterior = lista[i - 1];
          if (atual.km > anterior.km) {
            atual.km_rodados = atual.km - anterior.km;
            if (atual.litros > 0) {
              atual.media_km_l = atual.km_rodados / atual.litros;
            }
          }
        } else {
          // Primeiro abastecimento: usa o Hodômetro Inicial do Veículo
          const veiculo = veiculos.data?.find(v => v.id === atual.veiculo_id);
          if (veiculo && veiculo.hodometro_km && atual.km > veiculo.hodometro_km) {
            atual.km_rodados = atual.km - veiculo.hodometro_km;
            if (atual.litros > 0) {
              atual.media_km_l = atual.km_rodados / atual.litros;
            }
          }
        }
        rowsFinais.push(atual);
'@

$content = $content -replace $oldCalc, $newCalc

# 2. Ajustar a exibição de litros (sem arredondar)
$content = $content -replace 'num\(r\.litros, 1\)', 'num(r.litros, 3)'

# 3. Ajustar a exibição de preço (com R$)
$content = $content -replace 'num\(r\.preco_litro, 2\)', 'brl(r.preco_litro)'

# 4. Corrigir a origem para excel
$content = $content -replace 'origem: "manual",', 'origem: "excel",'

Set-Content -Path $file -Value $content -Encoding UTF8
Write-Host "✅ Frontend: Cálculo com Hodômetro Inicial e exibição corrigidos." -ForegroundColor Green