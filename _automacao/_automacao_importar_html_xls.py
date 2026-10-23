import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_import_html_{agora}.zip"
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

def ajustar_importacao(raiz):
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
      const text = await file.text();
      
      // O arquivo é um HTML disfarçado de XLS. Vamos parsear com DOMParser.
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, "text/html");
      const table = doc.querySelector("table");
      
      if (!table) {
        toast.error("Tabela não encontrada no arquivo HTML.");
        return;
      }

      const rows = Array.from(table.querySelectorAll("tr"));
      let headerRow: string[] = [];
      let startRow = -1;

      // Procura a linha de cabeçalho (que contém "Data" e "Placa")
      for (let i = 0; i < rows.length; i++) {
        const cells = Array.from(rows[i].querySelectorAll("td, th")).map(c => c.textContent?.trim() || "");
        const normalized = cells.map(c => c.toLowerCase());
        if (normalized.includes("data") && normalized.includes("placa") && normalized.includes("litros")) {
          headerRow = normalized;
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado. Verifique se a planilha tem as colunas 'Data', 'Placa' e 'Litros'.");
        return;
      }

      const colIndex = (name: string) => headerRow.findIndex(h => h === name.toLowerCase());
      
      const idxData = colIndex("data");
      const idxPlaca = colIndex("placa");
      const idxKm = colIndex("leitura");
      const idxPosto = colIndex("posto");
      const idxLitros = colIndex("litros");
      const idxPreco = colIndex("v. litro");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas (Data, Placa, Litros, V. Litro).");
        return;
      }

      let importados = 0;

      for (let i = startRow; i < rows.length; i++) {
        const cells = Array.from(rows[i].querySelectorAll("td, th")).map(c => c.textContent?.trim() || "");
        if (cells.length === 0 || !cells[idxData] || cells[idxData].toLowerCase().includes("total") || cells[idxData].includes("Bsoft")) continue;

        // Formata a data (YYYY-MM-DD)
        let dataStr = cells[idxData];
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        // Formata a placa
        const placaRaw = cells[idxPlaca] || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        // Formata os números
        const litrosRaw = Number(cells[idxLitros].replace(".", "").replace(",", ".")) / 1000;
        const valorLitroRaw = Number(cells[idxPreco].replace(".", "").replace(",", ".")) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(cells[idxKm] || 0),
          fornecedor: cells[idxPosto] || "",
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
      toast.error("Erro ao ler o arquivo.");
    }
  };'''
        
        conteudo = conteudo[:inicio] + funcao_nova + conteudo[fim:]
        print("⚙️ Função handleImportXLS substituída para ler HTML.")

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
    else:
        print("⚠️ Função handleImportXLS não encontrada no arquivo.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Importação de HTML...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_importacao(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()