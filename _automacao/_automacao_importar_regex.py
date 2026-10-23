import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_regex_{agora}.zip"
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

def substituir_funcao(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo Abastecimentos.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Encontra a função handleImportXLS e tudo dentro dela até o fechamento "  };"
    padrao = re.compile(r"const handleImportXLS = async.*?\n  \};", re.DOTALL)
    
    funcao_nova = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      
      // O arquivo é um HTML malformado. Vamos usar Regex para extrair as linhas da tabela.
      // Procura por todas as tags <tr>...</tr>
      const rowRegex = /<tr[^>]*>([\\s\\S]*?)<\\/tr>/gi;
      const cellRegex = /<td[^>]*>([\\s\\S]*?)<\\/td>/gi;
      
      const rows = [];
      let rowMatch;
      
      while ((rowMatch = rowRegex.exec(text)) !== null) {
        const rowHtml = rowMatch[1];
        const cells = [];
        let cellMatch;
        
        // Extrai o texto de cada célula <td>...</td>, removendo tags HTML internas
        while ((cellMatch = cellRegex.exec(rowHtml)) !== null) {
          let cellText = cellMatch[1];
          // Remove todas as tags HTML (como <b>, <span>, etc) e espaços extras
          cellText = cellText.replace(/<[^>]+>/g, "").trim();
          // Decodifica entidades HTML comuns
          cellText = cellText.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
          cells.push(cellText);
        }
        
        if (cells.length > 0) {
          rows.push(cells);
        }
      }

      if (rows.length === 0) {
        toast.error("Nenhuma linha encontrada no arquivo HTML.");
        return;
      }

      // Procura a linha de cabeçalho
      let startRow = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].join(" ").toLowerCase();
        if (rowStr.includes("data") && rowStr.includes("placa") && rowStr.includes("litros")) {
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado. Verifique se as colunas 'Data', 'Placa' e 'Litros' estão na planilha.");
        return;
      }

      const headerRow = rows[startRow - 1];
      const colIndex = (name: string) => headerRow.findIndex(h => h.toLowerCase().includes(name.toLowerCase()));

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
        const row = rows[i];
        if (!row || !row[idxData] || row[idxData].toLowerCase().includes("total") || row[idxData].includes("Bsoft")) continue;

        let dataStr = row[idxData];
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = row[idxPlaca] || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const litrosRaw = Number(row[idxLitros].replace(/\\./g, "").replace(",", ".")) / 1000;
        const valorLitroRaw = Number(row[idxPreco].replace(/\\./g, "").replace(",", ".")) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(row[idxKm]?.replace(/\\./g, "").replace(",", ".") || 0),
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

    if padrao.search(conteudo):
        conteudo = padrao.sub(funcao_nova, conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Função handleImportXLS substituída com a versão Regex (à prova de HTML malformado).")
    else:
        print("❌ A função handleImportXLS não foi encontrada.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção da Planilha (XLS via Regex)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    substituir_funcao(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e teste a importação.")

if __name__ == "__main__":
    executar()