import os
import re

def fix_edenred(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir o nome do botão "Enderend" para "Edenred"
    c = c.replace("Enderend", "Edenred")
    c = c.replace("Importar Enderend", "Importar Edenred")
    
    # 2. Substituir a função handleImportEdenred inteira
    padrao_edenred = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
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

      // Mapeamento exato das colunas da planilha Edenred
      const idxData = findIdx("DATA TRANSACAO");
      const idxPlaca = findIdx("PLACA");
      const idxMotorista = findIdx("NOME MOTORISTA");
      const idxProduto = findIdx("TIPO COMBUSTIVEL");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("VL/LITRO");
      const idxKm = findIdx("HODOMETRO");
      const idxKmRodados = findIdx("KM RODADOS");
      const idxMedia = findIdx("KM/LITRO");
      const idxPosto = findIdx("NOME ESTABELECIMENTO");
      const idxValor = findIdx("VALOR EMISSAO");
      const idxCnpj = findIdx("CNPJ");
      const idxCidade = findIdx("CIDADE");
      const idxEstado = findIdx("UF");

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        const dataStr = String(row[idxData]).trim();
        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = Number(String(row[idxKm] || "0").replace(/[^\\d]/g, ""));
        
        // Lendo valores exatos, sem conversões malucas
        const litrosNum = Number(String(row[idxLitros] || "0").replace(",", "."));
        const precoNum = Number(String(row[idxPreco] || "0").replace(",", "."));
        const valorNum = idxValor !== -1 ? Number(String(row[idxValor] || "0").replace(",", ".")) : (litrosNum * precoNum);
        
        const kmRodadosNum = idxKmRodados !== -1 ? Number(String(row[idxKmRodados] || "0").replace(",", ".")) : null;
        const mediaNum = idxMedia !== -1 ? Number(String(row[idxMedia] || "0").replace(",", ".")) : null;

        // Tratamento do motorista
        const motoristaNome = idxMotorista !== -1 ? String(row[idxMotorista] || "").trim() : "";
        let motoristaId = NENHUM;
        if (motoristaNome && motoristas.data) {
          const mot = motoristas.data.find((m: any) => m.nome.toUpperCase() === motoristaNome.toUpperCase());
          if (mot) motoristaId = mot.id;
        }

        // CNPJ (pode vir como número ou string)
        let cnpjRaw = idxCnpj !== -1 ? String(row[idxCnpj] || "").replace(/\\D/g, "") : "";
        let cnpjFormatado = cnpjRaw.length === 14 ? formatCnpj(cnpjRaw) : "";

        const payload = {
          data: dataFinal,
          placa: String(row[idxPlaca] || "").toUpperCase().trim(),
          km: kmNum,
          motorista_id: motoristaId,
          fornecedor: String(row[idxPosto] || "").trim(),
          cnpj: cnpjFormatado,
          cidade: idxCidade !== -1 ? String(row[idxCidade] || "").trim() : "",
          estado: idxEstado !== -1 ? String(row[idxEstado] || "").trim() : "",
          litros: litrosNum,
          preco_litro: precoNum,
          valor_total: valorNum,
          km_rodados: kmRodadosNum,
          media_km_l: mediaNum,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          hora: horaFinal, numero_nf: null, chave_nfe: null, origem: "excel"
        };

        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: payload.placa, erro: err.message || "Erro" }); 
        }
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
        c = padrao_edenred.sub(lambda m: nova_funcao, c)
        print("✅ Função handleImportEdenred reescrita com mapeamento exato de colunas.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportEdenred.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    fix_edenred(os.getcwd())