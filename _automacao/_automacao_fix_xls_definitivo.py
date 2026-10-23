import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_xls_def_{agora}.zip"
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

def corrigir_importacao(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo Abastecimentos.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    inicio = conteudo.find("const handleImportXLS = async")
    if inicio == -1:
        print("❌ Função handleImportXLS não encontrada no arquivo.")
        return

    # Encontra o final da função (o primeiro "};" após o início)
    fim = conteudo.find("};", inicio) + 2

    funcao_nova = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
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

      // Função que remove TUDO que não for letra ou número (espaços, pontos, etc)
      const cleanHeader = (text: string) => text.toLowerCase().replace(/[^a-z0-9]/g, "");

      for (let i = 0; i < rows.length; i++) {
        const cells = Array.from(rows[i].querySelectorAll("td, th")).map(c => c.textContent?.trim() || "");
        const normalized = cells.map(c => cleanHeader(c));

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

      const colIndex = (name: string) => headerRow.findIndex(h => h === cleanHeader(name));
      
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

        let dataStr = cells[idxData];
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = cells[idxPlaca] || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

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

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Função handleImportXLS corrigida com sucesso (busca à prova de falhas).")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção Definitiva do XLS...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_importacao(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()