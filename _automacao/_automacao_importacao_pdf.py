import os
import shutil
import datetime
import zipfile
import subprocess

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_import_pdf_{agora}.zip"
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

def atualizar_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar imports do pdfjs e do ícone FileText
    if "pdfjs-dist" not in conteudo:
        conteudo = conteudo.replace(
            'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil } from "lucide-react";',
            'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText } from "lucide-react";\nimport * as pdfjsLib from "pdfjs-dist";\nimport pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";'
        )
        conteudo = conteudo.replace(
            'const TODOS = "__all__";',
            'pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;\n\nconst TODOS = "__all__";'
        )

    # 2. Adicionar o useRef para o input de arquivo
    if "const fileInputRef" not in conteudo:
        conteudo = conteudo.replace(
            '  const [excluirId, setExcluirId] = useState<string | null>(null);',
            '  const [excluirId, setExcluirId] = useState<string | null>(null);\n  const fileInputRef = useRef<HTMLInputElement>(null);'
        )
        conteudo = conteudo.replace('import { useMemo, useState } from "react";', 'import { useMemo, useState, useRef } from "react";')

    # 3. Adicionar a função handleImportPDF
    funcao_pdf = '''
  const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let text = "";

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map((item: any) => item.str).join(" ") + "\\n";
      }

      // Regex para extrair os dados da nota
      const nfMatch = text.match(/Nº\\s*(\\d+)/);
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/);
      const cnpjMatch = text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/);
      const fornecedorMatch = text.match(/RECEBEMOS DE\\s*(.*?)\\s*OS PRODUTOS/);
      const litrosMatch = text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/);
      const kmMatch = text.match(/KM\\s*(\\d+)/);
      const placaMatch = text.match(/PLACA DO VEÍCULO\\s*([A-Z0-9]+)/);
      const horaMatch = text.match(/(\\d{2}:\\d{2}:\\d{2})/);

      // Preenche o formulário
      setForm(prev => ({
        ...prev,
        numero_nf: nfMatch ? nfMatch[1] : prev.numero_nf,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\\s/g, "") : prev.chave_nfe,
        cnpj: cnpjMatch ? cnpjMatch[1] : prev.cnpj,
        fornecedor: fornecedorMatch ? fornecedorMatch[1].trim() : prev.fornecedor,
        litros: litrosMatch ? litrosMatch[1].replace(",", ".") : prev.litros,
        preco_litro: litrosMatch ? litrosMatch[2].replace(".", "").replace(",", ".") : prev.preco_litro,
        km: kmMatch ? kmMatch[1] : prev.km,
        hora: horaMatch ? horaMatch[1] : prev.hora,
        origem: "pdf"
      }));

      toast.success("Nota Fiscal importada com sucesso!");
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler o PDF. Verifique se é uma NF-e válida.");
    }
  };
'''
    if "handleImportPDF" not in conteudo:
        conteudo = conteudo.replace("  const abrirNovo = () => {", funcao_pdf + "\n  const abrirNovo = () => {")

    # 4. Adicionar o botão "Importar NF" na barra de ações
    botoes = '''
          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />
          <Button variant="outline" onClick={() => fileInputRef.current?.click()} data-testid="abastecimento-import-pdf">
            <FileText className="size-4 mr-2" /> Importar NF
          </Button>
          <Button onClick={abrirNovo} data-testid="abastecimento-new-button">
            <Plus className="size-4" /> Novo abastecimento
          </Button>'''
    
    alvo_botao = '''          <Button onClick={abrirNovo} data-testid="abastecimento-new-button">
            <Plus className="size-4" /> Novo abastecimento
          </Button>'''
    if "Importar NF" not in conteudo:
        conteudo = conteudo.replace(alvo_botao, botoes)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ Frontend: Lógica de importação de PDF e botão adicionados.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Importação de PDF...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    atualizar_abastecimentos(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")
    print("3. Clique em 'Importar NF' e selecione o PDF.")

if __name__ == "__main__":
    executar()