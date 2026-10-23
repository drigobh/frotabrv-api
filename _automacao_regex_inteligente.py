import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_regex_inteligente_{agora}.zip"
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

def corrigir_regex(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    inicio = conteudo.find("const handleImportPDF = async")
    fim = conteudo.find("};", inicio) + 2
    
    if inicio != -1 and fim != -1:
        funcao_nova = '''const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
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

      // --- REGEX INTELIGENTE ---

      // 1. Placa (Procura "PLACA:" e pega 7 caracteres alfanuméricos)
      const placaMatch = text.match(/PLACA[:\\s]*([A-Z]{3}[0-9][A-Z0-9][0-9]{2})/i) || text.match(/PLACA[:\\s]*([A-Z0-9]{7})/i);
      
      // 2. KM (Procura "KM:" seguido de números)
      const kmMatch = text.match(/KM[:\\s]*(\\d+)/i);
      
      // 3. Litros e Preço (Busca os números pela posição na tabela de produtos)
      // O padrão é: ... L   QUANTIDADE   VALOR_UNITARIO   VALOR_TOTAL ...
      // Ex: L 264,5700 6,990000 1.849,34  ou  L 297,350 6,840 2.033,87
      const litrosMatch = text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)\\s+([\\d.,]+)/i) 
                       || text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)/i); // Fallback

      // 4. Nº NF
      const nfMatch = text.match(/Nº\\s*(\\d+)/);
      
      // 5. Chave NF-e
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/i);
      
      // 6. CNPJ (Procura o CNPJ do emitente, que fica antes do destinatário)
      const cnpjMatch = text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/i);
      
      // 7. Fornecedor
      const fornecedorMatch = text.match(/RECEBEMOS DE\\s*(.*?)\\s*OS PRODUTOS/i);

      // Limpeza dos números (remove pontos de milhar e troca vírgula por ponto)
      const parseNum = (val: string) => Number(val.replace(/\\./g, "").replace(",", "."));

      const payload = {
        data: new Date().toISOString().split('T')[0],
        hora: null,
        numero_nf: nfMatch ? nfMatch[1] : null,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\\s/g, "") : null,
        cnpj: cnpjMatch ? cnpjMatch[1] : null,
        fornecedor: fornecedorMatch ? fornecedorMatch[1].trim() : null,
        placa: placaMatch ? placaMatch[1].toUpperCase() : null,
        litros: litrosMatch ? parseNum(litrosMatch[1]) : 0,
        preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0,
        km: kmMatch ? Number(kmMatch[1]) : 0,
      };

      console.log("Dados extraídos:", payload);

      await apiPost("/abastecimentos/importar", payload);
      
      toast.success("Nota Fiscal importada e registrada com sucesso!");
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao importar o PDF. Verifique se o veículo está cadastrado.");
    }
  }'''
        
        conteudo = conteudo[:inicio] + funcao_nova + conteudo[fim:]
        print("⚙️ Função handleImportPDF substituída com Regex posicional (à prova de variações).")

        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
    else:
        print("⚠️ Função handleImportPDF não encontrada no arquivo.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Regex Inteligente...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_regex(raiz)

    print("\n🚀 Automação concluída! Faça o commit e push para o Render:")
    print("git add .")
    print("git commit -m 'fix: regex posicional para litros e preco no pdf'")
    print("git push")

if __name__ == "__main__":
    executar()