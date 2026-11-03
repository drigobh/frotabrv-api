import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MAPEAMENTO_BSOFT_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Pneus.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Nova função handleImportFile com mapeamento robusto
    nova_funcao = '''
  // ==========================================
  // IMPORTAÇÃO DE PLANILHA BSOFT (Mapeamento Robusto)
  // ==========================================
  const getValor = (row: any, ...chaves: string[]) => {
    for (const chave of chaves) {
      const valor = row[chave];
      if (valor !== undefined && valor !== null && String(valor).trim() !== "") {
        return String(valor).trim();
      }
    }
    return "";
  };

  const handleImportFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (evt) => {
      try {
        const bstr = evt.target?.result;
        const wb = XLSX.read(bstr, { type: 'binary' });
        const wsname = wb.SheetNames[0];
        const ws = wb.Sheets[wsname];
        const data = XLSX.utils.sheet_to_json(ws, { defval: "" });
        
        if (data.length === 0) {
          toast.error("A planilha está vazia.");
          return;
        }

        // Log para debug: mostra os nomes das colunas da primeira linha
        console.log("Colunas encontradas na planilha:", Object.keys(data[0]));

        const payload = data.map((row: any) => {
          const numero_fogo = getValor(row, "Marca Fogo", "MarcaFogo", "Nº Fogo", "N.º Fogo", "Fogo");
          const marca = getValor(row, "Marca", "MARCA");
          const modelo = getValor(row, "Modelo", "MODELO");
          const medida = getValor(row, "Tamanho", "Medida", "TAMANHO", "MEDIDA").replace(",", ".").replace(" ", "/");
          
          if (!numero_fogo || !marca) return null;

          const data_descarte = getValor(row, "Data Descarte", "DataDescarte", "Descarte");
          const equipamento = getValor(row, "Equipamento", "EQUIPAMENTO", "Equip.", "Placa");
          
          let status = "Estoque";
          if (data_descarte) status = "Sucateado";
          else if (equipamento) status = "Aplicado";

          const tipo_raw = getValor(row, "Tipo", "TIPO").toUpperCase();
          let tipo = "Misto";
          if (tipo_raw === "LISO" || tipo_raw === "BORRACHUDO") tipo = "Misto";
          else if (tipo_raw === "DIRECIONAL") tipo = "Direcional";
          else if (tipo_raw === "TRACAO" || tipo_raw === "TRAÇÃO") tipo = "Tração";
          else if (tipo_raw === "BANDA") tipo = "Banda";

          return {
            numero_fogo,
            marca,
            modelo,
            medida,
            dot: getValor(row, "DOT", "Dot"),
            tipo,
            status,
            custo_aquisicao: Number(getValor(row, "Custo Total Atual", "CustoTotalAtual", "Custo", "Custo Aquisição").replace(".", "").replace(",", ".")) || 0,
            equipamento,
            posicao: getValor(row, "Posição", "Posicao", "POSIÇÃO", "Posição Pneu"),
            banda_rod: getValor(row, "Banda Rod.", "BandaRod", "Banda", "BANDA ROD."),
            estrutura: getValor(row, "Estrutura", "ESTRUTURA"),
            n_serie: getValor(row, "N.º Série", "NSerie", "N Serie", "Número de Série", "Serie"),
            n_recap: getValor(row, "N.º Recap.", "NRecap", "N Recap", "Recapagem", "Recap"),
            data_compra: getValor(row, "Data Compra", "DataCompra", "Compra"),
            data_descarte,
            custo_total_atual: Number(getValor(row, "Custo Total Atual", "CustoTotalAtual").replace(".", "").replace(",", ".")) || 0,
            profundidade_atual: Number(getValor(row, "Profundidade Atual", "ProfundidadeAtual", "Profundidade").replace(",", ".")) || 0,
            uso_atual: getValor(row, "Uso Atual", "UsoAtual", "Uso", "KM na Posição", "KM"),
            custo_por_km: Number(getValor(row, "Custo por KM", "CustoPorKM", "Custo KM", "CPK").replace(",", ".")) || 0,
            km_posicao: Number(getValor(row, "KM na Posição", "KMnaPosicao", "KM Posição", "KM").replace(".", "").replace(",", ".")) || 0,
          };
        }).filter((p): p is any => p !== null);

        if (payload.length === 0) {
          toast.error("Nenhum pneu válido encontrado. Verifique os nomes das colunas.");
          return;
        }

        console.log("Payload de importação (primeiro item):", payload[0]);

        const res = await apiPost<any>("/pneus/importar", payload);
        toast.success(`Importação concluída! ${res.inseridos} pneus adicionados.`);
        if (res.erros?.length > 0) {
          toast.warning(`${res.erros.length} pneus não foram importados (duplicidade ou erro).`);
          console.log("Erros:", res.erros);
        }
        
        qc.invalidateQueries({ queryKey: ["pneus"] });
        qc.invalidateQueries({ queryKey: ["pneus-dashboard"] });
      } catch (err) {
        console.error(err);
        toast.error("Erro ao ler a planilha. Verifique se o arquivo é um Excel válido.");
      }
    };
    reader.readAsBinaryString(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };
'''

    # Remove a função antiga e insere a nova
    padrao = re.compile(r'  // ==========================================\s*\n  // IMPORTAÇÃO DE PLANILHA BSOFT[\s\S]*?    if \(fileInputRef\.current\) fileInputRef\.current\.value = "";\s*\n  \};', re.MULTILINE)
    
    if padrao.search(c):
        c = padrao.sub(nova_funcao.strip(), c)
        print("✅ Função handleImportFile substituída com mapeamento robusto.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportFile antiga.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")