import os

def fix_backend(raiz):
    # Simplifica o Backend: ele apenas salva o que o Frontend envia.
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garante que o backend não faça divisões duplas (o Frontend já divide se precisar)
    if 'litros_corrigidos = (body.get("litros") or 0) / 1000' in c:
        c = c.replace('litros_corrigidos = (body.get("litros") or 0) / 1000', 'litros_corrigidos = body.get("litros") or 0')
    if 'preco_corrigido = (body.get("preco_litro") or 0) / 100' in c:
        c = c.replace('preco_corrigido = (body.get("preco_litro") or 0) / 100', 'preco_corrigido = body.get("preco_litro") or 0')

    # Salva o valor_total exato enviado pelo Frontend, ou calcula se não vier
    if 'valor_total = body.get("valor_total")' not in c:
        c = c.replace(
            'valor_total = litros_corrigidos * preco_corrigido',
            'valor_total = body.get("valor_total") or (litros_corrigidos * preco_corrigido)'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Importação simplificada (confia nos dados do Frontend).")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Importação BSOFT (HTML disfarçado)
    import re
    padrao_bsoft = re.compile(r'const handleImportXLS = async[\s\S]*?\n  \};', re.DOTALL)
    novo_bsoft = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const rowRegex = /<tr[^>]*>([\\s\\S]*?)<\\/tr>/gi;
      const rows: string[][] = [];
      let rowMatch;

      while ((rowMatch = rowRegex.exec(text)) !== null) {
        const cells: string[] = [];
        let cellMatch;
        const cellRegexLocal = /<td[^>]*>([\\s\\S]*?)<\\/td>/gi;
        while ((cellMatch = cellRegexLocal.exec(rowMatch[1])) !== null) {
          let cellText = cellMatch[1].replace(/<[^>]+>/g, "").trim();
          cellText = cellText.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&");
          cells.push(cellText);
        }
        if (cells.length > 0) rows.push(cells);
      }

      if (rows.length === 0) { toast.error("Nenhuma linha HTML encontrada."); return; }

      let headerRow: string[] = [];
      let startRow = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].join(" ").toUpperCase();
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerRow = rows[i].map(c => c.toUpperCase().trim());
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) { toast.error("Cabeçalho não encontrado no BSOFT."); return; }

      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name));
      const idxData = findIdx("DATA"), idxPlaca = findIdx("PLACA"), idxKm = findIdx("LEITURA"), 
            idxPosto = findIdx("POSTO"), idxLitros = findIdx("LITROS"), idxPreco = findIdx("V. LITRO"), idxValor = findIdx("VALOR");

      const totalLinhas = rows.length - startRow;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      for (let i = startRow; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS") || String(row[idxData]).includes("Bsoft")) continue;

        let dataStr = String(row[idxData]).trim();
        if (dataStr.includes("-")) { const [y, m, d] = dataStr.split(" ")[0].split("-"); dataStr = `${d}/${m}/${y}`; }
        
        const placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const parseNum = (val: any) => Number(String(val).replace(/[^0-9]/g, ""));
        
        // MATEMÁTICA BSOFT: Divide litros por 1000, preço por 100. Valor já vem em decimal.
        const litrosRaw = parseNum(row[idxLitros]) / 1000;
        const valorLitroRaw = parseNum(row[idxPreco]) / 100;
        const valorTotal = idxValor !== -1 ? Number(String(row[idxValor]).replace(",", ".")) : litrosRaw * valorLitroRaw;

        const payload = {
          data: dataStr, placa: placa, km: parseNum(row[idxKm]),
          fornecedor: String(row[idxPosto] || "").trim(), litros: litrosRaw,
          preco_litro: valorLitroRaw, valor_total: valorTotal,
          hora: null, numero_nf: null, chave_nfe: null, cnpj: null, origem: "excel"
        };

        try { await apiPost("/abastecimentos/importar", payload); importados++; } 
        catch (err: any) { erros.push({ linha: i + 1, placa: placa || "N/A", erro: err.message || "Erro" }); }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} abastecimentos BSOFT importados!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler o BSOFT."); setImportProgress(null);
    }
  };'''
    
    if padrao_bsoft.search(c):
        c = padrao_bsoft.sub(novo_bsoft, c)

    # 2. Importação Edenred (Excel real)
    padrao_edenred = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    novo_edenred = '''const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { toast.error("Planilha vazia."); return; }

      const headerRow = rows[0].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name));

      const idxData = findIdx("DATA TRANSACAO"), idxPlaca = findIdx("PLACA"), idxProduto = findIdx("TIPO COMBUSTIVEL"),
            idxLitros = findIdx("LITROS"), idxPreco = findIdx("VL/LITRO"), idxKm = findIdx("HODOMETRO"),
            idxPosto = findIdx("NOME ESTABELECIMENTO"), idxValor = findIdx("VALOR EMISSAO");

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        let dataStr = String(row[idxData]).trim();
        let dataFinal = dataStr.split(" ")[0];
        let horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = Number(String(row[idxKm] || "0").replace(/[^\\d]/g, ""));
        
        // MATEMÁTICA EDENRED: Valores já em decimal, NÃO DIVIDIR!
        const litrosNum = Number(String(row[idxLitros] || "0").replace(",", "."));
        const precoNum = Number(String(row[idxPreco] || "0").replace(",", "."));
        const valorNum = idxValor !== -1 ? Number(String(row[idxValor] || "0").replace(",", ".")) : (litrosNum * precoNum);

        const payload = {
          data: dataFinal, placa: String(row[idxPlaca]).toUpperCase().trim(), km: kmNum,
          fornecedor: String(row[idxPosto] || "").trim(), litros: litrosNum,
          preco_litro: precoNum, valor_total: valorNum, produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          hora: horaFinal, numero_nf: null, chave_nfe: null, cnpj: null, origem: "excel"
        };

        try { await apiPost("/abastecimentos/importar", payload); importados++; } 
        catch (err: any) { erros.push({ linha: i + 1, placa: payload.placa, erro: err.message || "Erro" }); }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler Edenred."); setImportProgress(null);
    }
  };'''

    if padrao_edenred.search(c):
        c = padrao_edenred.sub(novo_edenred, c)

    # 3. Cálculos dos Cards e Grid
    # Garantir que as somas usem Number() para não concatenar strings
    c = c.replace(
        'const litros = rowsOrdenadas.reduce((s, r) => s + r.litros, 0);',
        'const litros = rowsOrdenadas.reduce((s, r) => s + (Number(r.litros) || 0), 0);'
    )
    c = c.replace(
        'const valor = rowsOrdenadas.reduce((s, r) => s + r.valor_total, 0);',
        'const valor = rowsOrdenadas.reduce((s, r) => s + (Number(r.valor_total) || 0), 0);'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: BSOFT, Edenred e PDF separados e Cards corrigidos.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)