import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PDF_BOTAO_TRAVA_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir o botão do PDF (remover a lógica de trava)
    c = c.replace(
        '''onClick={() => { 
              if (isImportingPDFRef.current || importandoPDF) { 
                toast.info("A importação já está em andamento."); 
                return; 
              } 
              isImportingPDFRef.current = true; 
              setImportandoPDF(true);
              fileInputRef.current?.click(); 
            }}''',
        'onClick={() => fileInputRef.current?.click()}'
    )

    # 2. Corrigir o input (remover disabled se existir)
    c = c.replace(
        'ref={fileInputRef} onChange={handleImportPDF} className="hidden" disabled={importandoPDF}',
        'ref={fileInputRef} onChange={handleImportPDF} className="hidden"'
    )

    # 3. Corrigir a função handleImportPDF (garantir que a trava seja ativada corretamente)
    padrao = re.compile(r'const handleImportPDF = async \(e: React\.ChangeEvent<HTMLInputElement>\) => \{[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      setImportandoPDF(false);
      isImportingPDFRef.current = false;
      return;
    }

    if (isImportingPDFRef.current) {
      toast.info("A importação já está em andamento.");
      return;
    }

    isImportingPDFRef.current = true;
    setImportandoPDF(true);

    try {
      const arrayBuffer = await file.arrayBuffer();
      
      const pdf = await Promise.race([
        pdfjsLib.getDocument({ data: arrayBuffer }).promise,
        new Promise((_, reject) => setTimeout(() => reject(new Error("Tempo esgotado ao carregar o PDF (10s)")), 10000))
      ]) as any;

      let text = "";
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        text += content.items.map((item: any) => item.str).join(" ") + "\\n";
      }

      text = text.replace(/\\n/g, " ").replace(/\\s+/g, " ");

      const placaMatch = text.match(/PLACA[:\\s]*([A-Z0-9]{7})/i);
      const placa = placaMatch ? placaMatch[1].toUpperCase() : "";
      
      const veiculo = veiculos.data?.find((v: any) => v.placa.replace("-", "").toUpperCase() === placa.replace("-", "").toUpperCase());
      if (!veiculo) { 
        toast.error(`Veículo com placa ${placa} não encontrado.`); 
        return; 
      }

      const kmMatch = text.match(/KM[:\\s]*(\\d+)/i);
      const km = kmMatch ? Number(kmMatch[1]) : 0;
      
      const dateMatch = text.match(/DATA DA EMISS[ÃA]O.*?(\\d{2}\\/\\d{2}\\/\\d{4})/i);
      let dataStr = new Date().toISOString().split("T")[0];
      if (dateMatch) {
        const [d, m, y] = dateMatch[1].split("/");
        dataStr = `${y}-${m}-${d}`;
      }

      const timeMatch = text.match(/HORA DA SA[ÍI]DA.*?(\\d{2}:\\d{2})/i);
      const nfMatch = text.match(/N[º°]\\s*(\\d+)/i);
      const chaveMatch = text.match(/CHAVE DE ACESSO DA NF-E\\s*([\\d\\s]+)/i);
      const cnpjMatch = text.match(/C\\.N\\.P\\.J\\.\\s*\\/\\s*C\\.P\\.F\\.\\s*([\\d\\.\\/\\-]+)/i) || text.match(/C\\.N\\.P\\.J\\.\\s*([\\d\\.\\/\\-]+)/i);
      const fornMatch = text.match(/RECEBEMOS DE\\s+([^,]+?)(?:\\s*\\(|,)/i);
      const litrosMatch = text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)\\s+([\\d.,]+)/i);
      
      const parseNum = (val: string) => {
        if (!val) return 0;
        let str = String(val).replace(/[^\\d.,]/g, "");
        if (str.includes('.') && str.includes(',')) str = str.replace(/\\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        return Number(str);
      };

      const cnpjLimpo = cnpjMatch ? cnpjMatch[1].replace(/\\D/g, '') : "";
      const fornecedorNome = fornMatch ? fornMatch[1].trim() : "";
      
      const payload = {
        data: dataStr, placa, km,
        fornecedor: fornecedorNome,
        cnpj: cnpjLimpo ? formatCnpj(cnpjLimpo) : "",
        litros: litrosMatch ? parseNum(litrosMatch[1]) : 0,
        preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0,
        valor_total: litrosMatch ? parseNum(litrosMatch[3]) : 0,
        produto: "DIESEL",
        numero_nf: nfMatch ? nfMatch[1] : null,
        chave_nfe: chaveMatch ? chaveMatch[1].replace(/\\s/g, "") : null,
        hora: timeMatch ? timeMatch[1] : null,
        origem: "pdf"
      };

      if (fornecedorNome) {
        const existingForn = fornecedores.find((f: any) => f.nome.toUpperCase() === fornecedorNome.toUpperCase());
        if (!existingForn) {
          try {
            await apiPost("/fornecedores", {
              nome: fornecedorNome, documento: payload.cnpj, ativo: true, avaliacao: 0
            });
            await refetchFornecedores();
          } catch (err) {}
        }
      }

      await apiPost("/abastecimentos/importar", payload);
      toast.success("Nota Fiscal importada com sucesso!");
      invalidate();
    } catch (error: any) {
      console.error("ERRO PDF:", error);
      toast.error("Erro ao importar PDF: " + (error.message || "Erro desconhecido"));
    } finally {
      setImportandoPDF(false);
      isImportingPDFRef.current = false;
      e.target.value = "";
    }
  };'''

    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
        print("✅ Função handleImportPDF reescrita.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportPDF.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)