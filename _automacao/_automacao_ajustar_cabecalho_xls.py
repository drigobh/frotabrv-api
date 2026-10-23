import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_ajustar_xls_{agora}.zip"
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

def ajustar_cabecalho_xls(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui a função handleImportXLS inteira por uma versão com busca flexível
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
      
      // Procura a linha que contenha "Data" e "Placa" (flexível)
      let startRow = -1;
      for (let i = 0; i < data.length; i++) {
        const rowStr = JSON.stringify(data[i] || []);
        if (rowStr.includes("Data") && rowStr.includes("Placa")) {
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado. Verifique se as colunas 'Data' e 'Placa' estão na planilha.");
        return;
      }

      let importados = 0;

      for (let i = startRow; i < data.length; i++) {
        const row = data[i];
        if (!row || !row[0] || String(row[0]).includes("Totais") || String(row[0]).includes("Bsoft")) continue;

        // Formata a data (YYYY-MM-DD)
        let dataStr = String(row[0]).trim();
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        // Formata a placa (remove /MG e traço)
        const placaRaw = String(row[1] || "").trim();
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        // Formata os números (Litros e Valor)
        const litrosRaw = Number(row[8] || 0) / 1000;
        const valorLitroRaw = Number(row[10] || 0) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number(row[4] || 0), // Leitura
          fornecedor: String(row[6] || "").trim(), // Posto
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
        print("⚙️ Função handleImportXLS substituída com busca flexível no cabeçalho.")

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
    ajustar_cabecalho_xls(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()