import os
import shutil
import datetime
import zipfile
import subprocess

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_import_xls_{agora}.zip"
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

def instalar_xlsx(raiz):
    pasta_front = os.path.join(raiz, "frontend")
    print("📦 Instalando xlsx (SheetJS)...")
    try:
        subprocess.run(["npm", "install", "xlsx"], cwd=pasta_front, check=True, shell=True)
        print("✅ xlsx instalado.")
    except Exception as e:
        print(f"❌ Erro ao instalar xlsx: {e}")

def reescrever_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar imports do XLSX e do ícone de upload
    if "import * as XLSX" not in conteudo:
        conteudo = conteudo.replace(
            'import { FileText } from "lucide-react";',
            'import { FileText, Upload } from "lucide-react";\nimport * as XLSX from "xlsx";'
        )
        # Se não achar o FileText, adiciona no import geral
        if "Upload" not in conteudo:
             conteudo = conteudo.replace(
                'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText } from "lucide-react";',
                'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText, Upload } from "lucide-react";'
            )

    # 2. Adicionar a função handleImportXLS
    funcao_xls = '''
  const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const arrayBuffer = await file.arrayBuffer();
      const workbook = XLSX.read(arrayBuffer, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      
      // Converte para JSON
      const data = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as any[][];
      
      // Encontra a linha de cabeçalho (onde tem "Data" e "Placa")
      let startRow = -1;
      for (let i = 0; i < data.length; i++) {
        if (data[i] && data[i].includes("Data") && data[i].includes("Placa")) {
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado.");
        return;
      }

      let importados = 0;
      const importadosComSucesso = [];

      for (let i = startRow; i < data.length; i++) {
        const row = data[i];
        // Pula linhas vazias ou totais
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
          importadosComSucesso.push(placa);
        } catch (err) {
          console.error(`Erro na linha ${i + 1} (${placa}):`, err);
        }
      }

      toast.success(`${importados} abastecimentos importados com sucesso!`);
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler a planilha.");
    }
  };
'''
    if "handleImportXLS" not in conteudo:
        conteudo = conteudo.replace("  const abrirNovo = () => {", funcao_xls + "\n  const abrirNovo = () => {")

    # 3. Adicionar o input de XLS e o botão
    botoes_xls = '''
            <input type="file" accept=".xls,.xlsx" onChange={handleImportXLS} className="hidden" id="xls-input" />
            <Button variant="outline" onClick={() => document.getElementById('xls-input')?.click()}>
              <Upload className="size-4 mr-2" /> Importar XLS
            </Button>'''
    
    alvo_botao = '''<input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />'''
    if "Importar XLS" not in conteudo:
        conteudo = conteudo.replace(alvo_botao, botoes_xls + "\n" + alvo_botao)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Frontend: Lógica de importação de XLS adicionada.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Importação de XLS...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    instalar_xlsx(raiz)
    reescrever_abastecimentos(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'feat: importacao de planilha xls de abastecimentos'")
    print("git push")

if __name__ == "__main__":
    executar()