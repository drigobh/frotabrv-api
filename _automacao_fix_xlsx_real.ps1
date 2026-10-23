$file = "frontend\src\pages\Abastecimentos.tsx"
$content = Get-Content $file -Raw

# Adiciona o import do xlsx se não existir
if ($content -notmatch 'import \* as XLSX from "xlsx";') {
    $content = $content -replace 'import \{ toast \} from "sonner";', "import * as XLSX from `"xlsx`";`nimport { toast } from `"sonner`";"
}

$oldFunctionPattern = 'const handleImportXLS = async[\s\S]*?\n  \};'

$newFunction = @'
  const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length === 0) { toast.error("Nenhuma linha encontrada."); return; }

      let headerRow: string[] = [];
      let startRow = -1;
      
      for (let i = 0; i < rows.length; i++) {
        const row = rows[i] || [];
        const rowStr = row.join(" ").toUpperCase();
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerRow = row.map((c: any) => String(c).toUpperCase().trim());
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) { 
        toast.error("Cabeçalho não encontrado. Verifique se a planilha tem as colunas Data, Placa e Litros.");
        return; 
      }

      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name.toUpperCase()));
      
      const idxData = findIdx("DATA");
      const idxPlaca = findIdx("PLACA");
      const idxKm = findIdx("LEITURA");
      const idxPosto = findIdx("POSTO");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("V. LITRO");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas no cabeçalho.");
        return;
      }

      const totalLinhas = rows.length - startRow;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      
      let importados = 0;
      const erros: any[] = [];

      for (let i = startRow; i < rows.length; i++) {
        const row = rows[i];
        
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS") || String(row[idxData]).includes("Bsoft")) {
          setImportProgress(prev => prev ? { ...prev, current: prev.current + 1 } : null);
          continue;
        }

        let dataStr = String(row[idxData]).trim();
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const parseNum = (val: any) => Number(String(val).replace(/[^0-9]/g, ""));
        
        // Se o Excel já retornou como número, usamos direto. Se for string, limpamos.
        const litrosNum = typeof row[idxLitros] === 'number' ? row[idxLitros] : parseNum(row[idxLitros]);
        const precoNum = typeof row[idxPreco] === 'number' ? row[idxPreco] : parseNum(row[idxPreco]);
        
        const litrosRaw = litrosNum / 1000;
        const valorLitroRaw = precoNum / 100;
        
        const kmStr = String(row[idxKm] || "0");
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(kmStr.replace(/\./g, "").replace(",", ".")),
          fornecedor: String(row[idxPosto] || "").trim(),
          litros: litrosRaw,
          preco_litro: valorLitroRaw,
          hora: null,
          numero_nf: null,
          chave_nfe: null,
          cnpj: null
        };

        try {
          await apiPost("/abastecimentos/importar", payload);
          importados++;
        } catch (err: any) {
          erros.push({
            linha: i + 1,
            placa: placa || "N/A",
            erro: err.response?.data?.detail || err.message || "Erro"
          });
        }

        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      
      if (erros.length === 0) {
        toast.success(`${importados} abastecimentos importados com sucesso!`);
      }
      
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler o arquivo.");
      setImportProgress(null);
    }
  };
'@

$newContent = $content -replace $oldFunctionPattern, $newFunction

Set-Content -Path $file -Value $newContent -Encoding UTF8

Write-Host "✅ Função handleImportXLS substituída para usar XLSX." -ForegroundColor Green