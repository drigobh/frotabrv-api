import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_xls_cab_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def ajustar_cabecalho(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui a função handleImportXLS inteira
    inicio = conteudo.find("const handleImportXLS = async")
    fim = conteudo.find("};", inicio) + 2
    
    if inicio != -1 and fim != -1:
        funcao_nova = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const arrayBuffer = await file.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const data = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as any[][];
      
      // Procura a linha de cabeçalho, verificando célula por célula (ignorando espaços)
      let startRow = -1;
      let headerRow: any[] = [];
      for (let i = 0; i < data.length; i++) {
        const row = data[i] || [];
        // Normaliza as células (remove espaços e caracteres invisíveis)
        const normalizedCells = row.map(c => String(c || "").trim().toLowerCase());
        if (normalizedCells.includes("data") && normalizedCells.includes("placa") && normalizedCells.includes("litros")) {
          startRow = i + 1;
          headerRow = normalizedCells;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado. Verifique se a planilha tem as colunas 'Data', 'Placa' e 'Litros'.");
        return;
      }

      // Mapeia a posição de cada coluna baseado no nome normalizado
      const colIndex = (name: string) => headerRow.findIndex((h: string) => h === name.toLowerCase());
      
      const idxData = colIndex("Data");
      const idxPlaca = colIndex("Placa");
      const idxKm = colIndex("Leitura");
      const idxPosto = colIndex("Posto");
      const idxLitros = colIndex("Litros");
      const idxPreco = colIndex("V. Litro");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas (Data, Placa, Litros, V. Litro).");
        return;
      }

      let importados = 0;

      for (let i = startRow; i < data.length; i++) {
        const row = data[i];
        if (!row || !row[idxData] || String(row[idxData]).toLowerCase().includes("total") || String(row[idxData]).includes("Bsoft")) continue;

        // Formata a data (YYYY-MM-DD)
        let dataStr = String(row[idxData]).trim();
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        // Formata a placa (remove /MG e traço)
        const placaRaw = String(row[idxPlaca] || "").trim();
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        // Formata os números (Litros e Valor)
        const litrosRaw = Number(String(row[idxLitros] || 0).replace(",", ".")) / 1000;
        const valorLitroRaw = Number(String(row[idxPreco] || 0).replace(",", ".")) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(row[idxKm] || 0),
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
        } catch (err) {
          console.error(`Erro na linha ${i + 1}:`, err);
        }
      }

      toast.success(`${importados} abastecimentos importados com sucesso!`);
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler a planilha.");
    }
  };'''
        
        conteudo = conteudo[:inicio] + funcao_nova + conteudo[fim:]
        print("⚙️ Função handleImportXLS substituída com sucesso.")

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
    else:
        print("⚠️ Função handleImportXLS não encontrada no arquivo.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Ajuste do Cabeçalho XLS...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_cabecalho(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()