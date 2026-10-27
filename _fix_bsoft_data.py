import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BSOFT_DATA_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substitui APENAS a função handleImportXLS
    padrao_bsoft = re.compile(r'const handleImportXLS = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      let headerIdx = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].map((c: any) => String(c).toUpperCase()).join(" ");
        if (rowStr.includes("DATA") && rowStr.includes("PLACA") && rowStr.includes("LITROS")) {
          headerIdx = i;
          break;
        }
      }

      if (headerIdx === -1) { toast.error("Cabeçalho do BSOFT não encontrado."); return; }

      const header = rows[headerIdx].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => header.findIndex(h => h.includes(name));

      const idxData = findIdx("DATA");
      const idxPlaca = findIdx("PLACA");
      const idxKm = findIdx("LEITURA");
      const idxPosto = findIdx("POSTO");
      const idxLitros = findIdx("LITROS");
      const idxValor = findIdx("VALOR");
      const idxPreco = findIdx("V. LITRO");
      const idxProduto = findIdx("PRODUTO");

      const totalLinhas = rows.length - headerIdx - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) {
            if (str.lastIndexOf(',') > str.lastIndexOf('.')) str = str.replace(/\\./g, '').replace(',', '.');
            else str = str.replace(/,/g, '');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str) || 0;
      };

      for (let i = headerIdx + 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAIS")) continue;

        // CONVERSÃO DA DATA PARA PADRÃO BRASILEIRO (dd/mm/yyyy)
        let dataStr = String(row[idxData]).trim().split(" ")[0]; // Pega só a data (2026-06-02)
        if (dataStr.includes("-")) {
           const parts = dataStr.split("-");
           if (parts.length === 3) {
               dataStr = `${parts[2]}/${parts[1]}/${parts[0]}`; // Vira 02/06/2026
           }
        }

        let placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.replace("-", "").split("/")[0].toUpperCase();

        if (!placa || placa.length < 7 || placa.includes("BSOFT")) continue;

        const litros = parseNum(row[idxLitros]);
        const preco_litro = parseNum(row[idxPreco]);
        const valor_total = parseNum(row[idxValor]);
        const km = parseNum(row[idxKm]);

        const payload = {
          data: dataStr,
          placa: placa,
          km: km,
          fornecedor: String(row[idxPosto] || "").trim(),
          litros: litros,
          preco_litro: preco_litro,
          valor_total: valor_total,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          origem: "bsoft"
        };

        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(r => setTimeout(r, 150)); 
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: placa, erro: err.message || "Erro" }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} registros BSOFT importados!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler o arquivo BSOFT."); setImportProgress(null);
    }
  };'''

    if padrao_bsoft.search(c):
        c = padrao_bsoft.sub(lambda m: nova_funcao, c)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Função BSOFT atualizada para converter a data para dd/mm/yyyy.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportXLS.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)