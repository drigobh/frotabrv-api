import os
import re

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a ref do input file
    if "edenredInputRef" not in c:
        c = c.replace(
            'const xlsInputRef = useRef<HTMLInputElement>(null);',
            'const xlsInputRef = useRef<HTMLInputElement>(null);\n  const edenredInputRef = useRef<HTMLInputElement>(null);'
        )

    # 2. Adicionar a função handleImportEdenred antes do salvar
    if "handleImportEdenred" not in c:
        funcao_edenred = '''const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { toast.error("Planilha vazia ou inválida."); return; }

      const headerRow = rows[0].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => headerRow.findIndex(h => h.includes(name));

      const idxData = findIdx("DATA TRANSACAO");
      const idxPlaca = findIdx("PLACA");
      const idxProduto = findIdx("TIPO COMBUSTIVEL");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("VL/LITRO");
      const idxKm = findIdx("HODOMETRO");
      const idxPosto = findIdx("NOME ESTABELECIMENTO");
      const idxValor = findIdx("VALOR EMISSAO");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1) {
        toast.error("Colunas essenciais do Edenred não encontradas."); return;
      }

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0;
      const erros: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL") || String(row[idxPlaca]).toUpperCase().includes("TOTAL")) {
          setImportProgress(prev => prev ? { ...prev, current: prev.current + 1 } : null);
          continue;
        }

        let dataStr = String(row[idxData]).trim();
        let dataFinal = dataStr.split(" ")[0];
        let horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmStr = String(row[idxKm] || "0");
        const kmNum = Number(kmStr.replace(/[^\\d]/g, ""));

        const litrosNum = Number(String(row[idxLitros] || "0").replace(",", "."));
        const precoNum = Number(String(row[idxPreco] || "0").replace(",", "."));
        const valorNum = Number(String(row[idxValor] || "0").replace(",", "."));
        const produtoStr = String(row[idxProduto] || "DIESEL").toUpperCase();

        const payload = {
          data: dataFinal,
          placa: String(row[idxPlaca]).toUpperCase().trim(),
          km: kmNum,
          fornecedor: String(row[idxPosto] || "").trim(),
          litros: litrosNum,
          preco_litro: precoNum,
          valor_total: valorNum,
          produto: produtoStr,
          hora: horaFinal,
          numero_nf: null,
          chave_nfe: null,
          cnpj: null,
          origem: "excel"
        };

        try {
          await apiPost("/abastecimentos/importar", payload);
          importados++;
        } catch (err: any) {
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.response?.data?.detail || err.message || "Erro" });
        }

        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} abastecimentos Edenred importados!`);
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler a planilha do Edenred.");
      setImportProgress(null);
    }
  };

  const salvar = useMutation({'''
        
        c = c.replace('const salvar = useMutation({', funcao_edenred)

    # 3. Adicionar o Input e o Botão na tela
    if 'Importar Edenred' not in c:
        novo_botao = '''<input type="file" accept=".xls,.xlsx" ref={xlsInputRef} onChange={handleImportXLS} className="hidden" />
          <Button variant="outline" onClick={() => xlsInputRef.current?.click()}><Upload className="size-4 mr-2" /> Importar XLS</Button>
          
          <input type="file" accept=".xlsx" ref={edenredInputRef} onChange={handleImportEdenred} className="hidden" />
          <Button variant="outline" onClick={() => edenredInputRef.current?.click()}><Upload className="size-4 mr-2" /> Importar Edenred</Button>
          '''
        
        c = c.replace(
            '<input type="file" accept=".xls,.xlsx" ref={xlsInputRef} onChange={handleImportXLS} className="hidden" />\n          <Button variant="outline" onClick={() => xlsInputRef.current?.click()}><Upload className="size-4 mr-2" /> Importar XLS</Button>',
            novo_botao
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado com a importação do Edenred.")

if __name__ == "__main__":
    fix_frontend(os.getcwd())