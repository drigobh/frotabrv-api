import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_EDENRED_FIX_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
        zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Vamos encontrar a função handleImportEdenred do início ao fim
    padrao = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    
    if not padrao.search(c):
        print("⚠️ Não encontrei a função handleImportEdenred. Ela foi renomeada?")
        return

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

      const idxCod = findIdx("CODIGO TRANSACAO");
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

      // Função de conversão super robusta
      const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).trim();
        if (str.includes('.') && str.includes(',')) {
            str = str.replace(/\\./g, '').replace(',', '.');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        const num = Number(str);
        return isNaN(num) ? 0 : num;
      };

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        const dataStr = String(row[idxData]).trim();
        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = parseNum(row[idxKm]);
        const litrosNum = parseNum(row[idxLitros]);
        const precoNum = parseNum(row[idxPreco]);
        const valorNum = idxValor !== -1 ? parseNum(row[idxValor]) : (litrosNum * precoNum);
        
        const kmRodadosNum = idxKmRodados !== -1 ? parseNum(row[idxKmRodados]) : null;
        const mediaNum = idxMedia !== -1 ? parseNum(row[idxMedia]) : null;

        const motoristaNome = idxMotorista !== -1 ? String(row[idxMotorista] || "").trim() : "";
        let motoristaId = NENHUM;
        if (motoristaNome && motoristas.data) {
          const mot = motoristas.data.find((m: any) => m.nome.toUpperCase() === motoristaNome.toUpperCase());
          if (mot) motoristaId = mot.id;
        }

        let cnpjRaw = idxCnpj !== -1 ? String(row[idxCnpj] || "").replace(/\\D/g, "") : "";
        let cnpjFormatado = cnpjRaw.length === 14 ? formatCnpj(cnpjRaw) : "";

        const fornecedorNome = String(row[idxPosto] || "").trim();
        const cidade = idxCidade !== -1 ? String(row[idxCidade] || "").trim() : "";
        const estado = idxEstado !== -1 ? String(row[idxEstado] || "").trim() : "";

        const payload = {
          data: dataFinal,
          placa: String(row[idxPlaca] || "").toUpperCase().trim(),
          km: kmNum,
          motorista_id: motoristaId,
          fornecedor: fornecedorNome,
          cnpj: cnpjFormatado,
          cidade: cidade,
          estado: estado,
          litros: litrosNum,
          preco_litro: precoNum,
          valor_total: valorNum,
          km_rodados: kmRodadosNum,
          media_km_l: mediaNum,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          codigo_transacao: String(row[idxCod] || "").trim(),
          hora: horaFinal, numero_nf: null, chave_nfe: null, origem: "excel"
        };

        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(resolve => setTimeout(resolve, 200));
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

    c = padrao.sub(lambda m: nova_funcao, c)
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Função handleImportEdenred substituída por versão com parseNum corrigido.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)