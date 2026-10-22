import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_forcar_import_{agora}.zip"
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

def forcar_importacao(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Corrigir o import do worker do PDF (garantir que está lá)
    if "pdfjs-dist" not in conteudo:
        conteudo = conteudo.replace(
            'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil } from "lucide-react";',
            'import { Fuel, Plus, Trash2, ArrowUpRight, ArrowDownRight, DollarSign, Droplets, Target, TrendingUp, List, Pencil, FileText } from "lucide-react";\nimport * as pdfjsLib from "pdfjs-dist";\nimport pdfWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";'
        )
        conteudo = conteudo.replace(
            'const TODOS = "__all__";',
            'pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;\n\nconst TODOS = "__all__";'
        )

    # 2. Adicionar useRef (se não existir)
    if "fileInputRef" not in conteudo:
        conteudo = conteudo.replace(
            '  const [excluirId, setExcluirId] = useState<string | null>(null);',
            '  const [excluirId, setExcluirId] = useState<string | null>(null);\n  const fileInputRef = useRef<HTMLInputElement>(null);'
        )
        conteudo = conteudo.replace('import { useMemo, useState } from "react";', 'import { useMemo, useState, useRef } from "react";')

    # 3. Adicionar a função handleImportPDF correta
    funcao_correta = '''
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

      // Regex para extrair os dados
      const nfMatch = text.match(/Nº\\s*(\\d+)/);
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/);
      const cnpjMatch = text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/);
      const fornecedorMatch = text.match(/RECEBEMOS DE\\s*(.*?)\\s*OS PRODUTOS/);
      const litrosMatch = text.match(/DIESEL S 10.*?(\\d+,\\d+)\\s*\\d+,\\d+\\s*([\\d\\.]+,\\d+)/);
      const kmMatch = text.match(/KM\\s*(\\d+)/);
      const placaMatch = text.match(/PLACA DO VEÍCULO\\s*([A-Z0-9]+)/);
      const horaMatch = text.match(/(\\d{2}:\\d{2}:\\d{2})/);

      // Monta o payload para enviar ao backend
      const payload = {
        data: new Date().toISOString().split('T')[0],
        hora: horaMatch ? horaMatch[1] : null,
        numero_nf: nfMatch ? nfMatch[1] : null,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\\s/g, "") : null,
        cnpj: cnpjMatch ? cnpjMatch[1] : null,
        fornecedor: fornecedorMatch ? fornecedorMatch[1].trim() : null,
        placa: placaMatch ? placaMatch[1] : null,
        litros: litrosMatch ? Number(litrosMatch[1].replace(",", ".")) : 0,
        preco_litro: litrosMatch ? Number(litrosMatch[2].replace(".", "").replace(",", ".")) : 0,
        km: kmMatch ? Number(kmMatch[1]) : 0,
      };

      await apiPost("/abastecimentos/importar", payload);
      
      toast.success("Nota Fiscal importada e registrada com sucesso!");
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao importar o PDF. Verifique se o veículo está cadastrado.");
    }
  };
'''

    # Verifica se a função antiga existe e substitui
    if "handleImportPDF" in conteudo:
        # Encontra a função antiga (pode ter sido alterada) e substitui pela correta
        import re
        padrao = re.compile(r"const handleImportPDF = async \(.*?\n  \};", re.DOTALL)
        if padrao.search(conteudo):
            conteudo = padrao.sub(funcao_correta, conteudo)
            print("⚙️ Função handleImportPDF substituída pela versão correta.")
        else:
            print("⚠️ Não foi possível encontrar a função para substituir.")
    else:
        # Se não existe, insere antes do abrirNovo
        conteudo = conteudo.replace("  const abrirNovo = () => {", funcao_correta + "\n  const abrirNovo = () => {")
        print("⚙️ Função handleImportPDF inserida.")

    # 4. Garantir que o botão "Importar NF" existe
    if "Importar NF" not in conteudo:
        botoes = '''
          <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleImportPDF} className="hidden" />
          <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
            <FileText className="size-4 mr-2" /> Importar NF
          </Button>
          <Button onClick={abrirNovo}>
            <Plus className="size-4" /> Novo abastecimento
          </Button>'''
        alvo = '''<Button onClick={abrirNovo}>
            <Plus className="size-4" /> Novo abastecimento
          </Button>'''
        if alvo in conteudo:
            conteudo = conteudo.replace(alvo, botoes)
            print("⚙️ Botão 'Importar NF' adicionado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Arquivo Abastecimentos.tsx atualizado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Forçar Importação...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    forcar_importacao(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'feat: corrigindo importacao de PDF'")
    print("git push")

if __name__ == "__main__":
    executar()