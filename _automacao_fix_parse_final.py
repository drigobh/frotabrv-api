import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui a função handleImportXLS inteira
    padrao = re.compile(r'const handleImportXLS = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
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
          cellText = cellText.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
          cells.push(cellText);
        }
        if (cells.length > 0) rows.push(cells);
      }

      if (rows.length === 0) { toast.error("Nenhuma linha encontrada."); return; }

      let headerRow: string[] = [];
      let startRow = -1;
      
      // Procura a linha de cabeçalho em qualquer lugar do arquivo
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].join(" ").toUpperCase();
        // Verifica se a linha tem as três palavras-chave (ignorando acentos e maiúsculas)
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerRow = rows[i].map(c => c.toUpperCase().trim());
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) { 
        toast.error("Cabeçalho não encontrado. Verifique se a planilha tem as colunas Data, Placa e Litros.");
        return; 
      }

      // Mapeia as colunas pelo nome
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
        
        if (!row || !row[idxData] || row[idxData].toUpperCase().includes("TOTAIS") || row[idxData].includes("Bsoft")) {
          setImportProgress(prev => prev ? { ...prev, current: prev.current + 1 } : null);
          continue;
        }

        let dataStr = row[idxData];
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = row[idxPlaca] || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        // FUNÇÃO DE LIMPEZA: Remove tudo que não for número antes de converter
        const parseNum = (val: string) => Number(String(val).replace(/[^0-9]/g, ""));
        
        const litrosRaw = parseNum(row[idxLitros]) / 1000;
        const valorLitroRaw = parseNum(row[idxPreco]) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number((row[idxKm] || "0").replace(/\\./g, "").replace(",", ".")),
          fornecedor: row[idxPosto] || "",
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
  };'''

    if padrao.search(conteudo):
        conteudo = padrao.sub(nova_funcao, conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Função handleImportXLS reescrita com busca por nome de coluna e limpeza de números.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportXLS.")

if __name__ == "__main__":
    corrigir(os.getcwd())