import os
import re
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_xls_inteligente_{agora}.zip"
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
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, "text/html");
      const table = doc.querySelector("table");
      
      if (!table) {
        toast.error("Tabela não encontrada no arquivo HTML.");
        return;
      }

      const rows = Array.from(table.querySelectorAll("tr"));
      let startRow = -1;

      // Procura a linha de cabeçalho verificando o texto da linha inteira
      for (let i = 0; i < rows.length; i++) {
        const rowText = rows[i].textContent?.toLowerCase() || "";
        if (rowText.includes("data") && rowText.includes("placa") && rowText.includes("litros")) {
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado. Verifique se a planilha tem as colunas 'Data', 'Placa' e 'Litros'.");
        return;
      }

      // Mapeia as colunas com base na linha de cabeçalho
      const headerCells = Array.from(rows[startRow - 1].querySelectorAll("td, th"));
      const findIdx = (term: string) => headerCells.findIndex(c => c.textContent?.toLowerCase().includes(term) || false);

      const idxData = findIdx("data");
      const idxPlaca = findIdx("placa");
      const idxKm = findIdx("leitura");
      const idxPosto = findIdx("posto");
      const idxLitros = findIdx("litros");
      const idxPreco = findIdx("v. litro");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas (Data, Placa, Litros, V. Litro).");
        return;
      }

      let importados = 0;

      for (let i = startRow; i < rows.length; i++) {
        const cells = Array.from(rows[i].querySelectorAll("td, th"));
        if (cells.length === 0 || !cells[idxData]?.textContent?.trim() || cells[idxData].textContent?.toLowerCase().includes("total")) continue;

        let dataStr = cells[idxData].textContent?.trim() || "";
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = cells[idxPlaca]?.textContent?.trim() || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const litrosStr = cells[idxLitros]?.textContent?.trim() || "0";
        const precoStr = cells[idxPreco]?.textContent?.trim() || "0";
        
        const litrosRaw = Number(litrosStr.replace(/\\./g, "").replace(",", ".")) / 1000;
        const valorLitroRaw = Number(precoStr.replace(/\\./g, "").replace(",", ".")) / 100;
        const kmStr = cells[idxKm]?.textContent?.trim() || "0";
        const postoStr = cells[idxPosto]?.textContent?.trim() || "";
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(kmStr.replace(/\\./g, "").replace(",", ".")),
          fornecedor: postoStr,
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
        print("✅ Função handleImportXLS substituída com a versão inteligente (textContent).")
    else:
        print("❌ A função handleImportXLS não foi encontrada. Verifique se o arquivo tem o nome correto.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção da Planilha (XLS)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    substituir_funcao(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e teste a importação.")

if __name__ == "__main__":
    executar()