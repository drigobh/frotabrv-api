$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# Substitui a função resumo
$oldResumoPattern = 'const resumo = useMemo\(\(\) => \{[\s\S]*?\}, \[rows\]\);'

$newResumo = @'
  // Calcula os KM Rodados e a Média no Frontend, com base nos dados da tabela
  const rowsComCalculo = useMemo(() => {
    // Agrupa por veículo
    const porVeiculo: Record<string, any[]> = {};
    rows.forEach(r => {
      if (!porVeiculo[r.veiculo_id]) porVeiculo[r.veiculo_id] = [];
      porVeiculo[r.veiculo_id].push(r);
    });

    // Ordena cada grupo por data e KM para calcular a diferença
    const rowsFinais: any[] = [];
    Object.values(porVeiculo).forEach(lista => {
      lista.sort((a, b) => a.data.localeCompare(b.data) || a.km - b.km);
      
      for (let i = 0; i < lista.length; i++) {
        const atual = { ...lista[i] };
        if (i > 0) {
          const anterior = lista[i - 1];
          if (atual.km > anterior.km) {
            atual.km_rodados = atual.km - anterior.km;
            if (atual.litros > 0) {
              atual.media_km_l = atual.km_rodados / atual.litros;
            }
          }
        }
        rowsFinais.push(atual);
      }
    });

    return rowsFinais.sort((a, b) => b.data.localeCompare(a.data));
  }, [rows]);

  const resumo = useMemo(() => {
    const litros = rowsComCalculo.reduce((s, r) => s + r.litros, 0);
    const valor = rowsComCalculo.reduce((s, r) => s + r.valor_total, 0);
    const comKm = rowsComCalculo.filter((r) => r.km_rodados != null);
    const km = comKm.reduce((s, r) => s + (r.km_rodados ?? 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + r.litros, 0);
    
    const maior = rowsComCalculo.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rowsComCalculo.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rowsComCalculo.length ? valor / rowsComCalculo.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;
    const custoPorKm = km > 0 ? valor / km : 0;

    return { litros, valor, km, media: litrosKm ? km / litrosKm : 0, preco: litros ? valor / litros : 0, total: rowsComCalculo.length, maior, menor, mediaValor, mediaKm, custoPorKm };
  }, [rowsComCalculo]);

  const ranking = useMemo(() => {
    const porVeiculo: Record<string, { label: string, litros: number, km: number }> = {};
    rowsComCalculo.forEach(r => {
      if (r.km_rodados != null) {
        if (!porVeiculo[r.veiculo_id]) porVeiculo[r.veiculo_id] = { label: r.veiculo_label.split(" · ")[0], litros: 0, km: 0 };
        porVeiculo[r.veiculo_id].litros += r.litros;
        porVeiculo[r.veiculo_id].km += r.km_rodados;
      }
    });
    return Object.values(porVeiculo).map(v => ({ label: v.label, media: v.litros > 0 ? v.km / v.litros : 0 })).sort((a, b) => b.media - a.media).slice(0, 5);
  }, [rowsComCalculo]);
'@

$newContent = $content -replace $oldResumoPattern, $newResumo

# Substitui 'rows' por 'rowsComCalculo' no JSX da tabela
$newContent = $newContent -replace 'rows\.map\(\(r\)', 'rowsComCalculo.map((r)'
$newContent = $newContent -replace 'rows\.length === 0', 'rowsComCalculo.length === 0'

Set-Content -Path $file -Value $newContent -Encoding UTF8

Write-Host "✅ Cálculo de KM Rodados e Média movido para o Frontend." -ForegroundColor Green