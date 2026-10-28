import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PDF_AVISO_{agora}.zip")
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

    # 1. Adicionar os estados do Modal (se não existirem)
    if 'const [pdfPendingData, setPdfPendingData] = useState<any>(null);' not in c:
        c = c.replace(
            'const [importandoPDF, setImportandoPDF] = useState(false);',
            'const [importandoPDF, setImportandoPDF] = useState(false);\n  const [pdfPendingData, setPdfPendingData] = useState<any>(null);\n  const [openPdfConfirm, setOpenPdfConfirm] = useState(false);\n  const [avaliacaoPendentePdf, setAvaliacaoPendentePdf] = useState(0);'
        )
        print("✅ Estados do Modal do PDF adicionados.")

    # 2. Substituir a função handleImportPDF para parar se o fornecedor não existir
    padrao_pdf = re.compile(r'const handleImportPDF = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao_pdf = '''const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
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

      // VALIDAÇÃO DE FORNECEDOR (AQUI ESTÁ O PULO DO GATO)
      if (fornecedorNome) {
        const existingForn = fornecedores.find((f: any) => f.nome.toUpperCase() === fornecedorNome.toUpperCase());
        if (!existingForn) {
          // Se não existe, PAUSA e abre o modal para avaliação
          setPdfPendingData(payload);
          setAvaliacaoPendentePdf(0);
          setOpenPdfConfirm(true);
          return; // <-- O return aqui impede a importação direta
        }
      }

      // Se o fornecedor já existe, importa direto
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
  };

  const confirmarFornecedorPdf = async () => {
    if (!pdfPendingData) return;
    
    const fornecedorNome = pdfPendingData.fornecedor;
    if (fornecedorNome) {
      try {
        await apiPost("/fornecedores", {
          nome: fornecedorNome,
          documento: pdfPendingData.cnpj || "",
          ativo: true,
          avaliacao: avaliacaoPendentePdf
        });
        await refetchFornecedores();
        toast.success(`Fornecedor ${fornecedorNome} cadastrado!`);
      } catch (err: any) {
        if (err.message?.includes("409")) {
          toast.warning(`Fornecedor ${fornecedorNome} já existe.`);
        }
      }
    }

    await apiPost("/abastecimentos/importar", pdfPendingData);
    toast.success("Nota Fiscal importada com sucesso!");
    invalidate();
    setOpenPdfConfirm(false);
    setPdfPendingData(null);
    setAvaliacaoPendentePdf(0);
  };'''

    if padrao_pdf.search(c):
        c = padrao_pdf.sub(lambda m: nova_funcao_pdf, c)
        print("✅ Função handleImportPDF atualizada para pausar e pedir avaliação.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportPDF.")

    # 3. Adicionar o Modal de Avaliação no JSX
    if 'Fornecedor não cadastrado (PDF)' not in c:
        modal_jsx = '''
      <Dialog open={openPdfConfirm} onOpenChange={(o) => { if (!o) { setOpenPdfConfirm(false); setPdfPendingData(null); setAvaliacaoPendentePdf(0); } }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Fornecedor não cadastrado</DialogTitle>
            <DialogDescription>
              O fornecedor "{pdfPendingData?.fornecedor}" não está cadastrado. Deseja cadastrá-lo com uma avaliação?
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4 flex flex-col items-center gap-3">
            <Label className="text-sm text-slate-400">Avaliação do Fornecedor</Label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map(star => (
                <button type="button" key={star} onClick={() => setAvaliacaoPendentePdf(star)} className="focus:outline-none hover:scale-110">
                  <Star className={`size-8 ${star <= avaliacaoPendentePdf ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                </button>
              ))}
            </div>
            <span className="text-xs text-slate-500">
              {avaliacaoPendentePdf === 0 ? "Selecione uma nota" : `${avaliacaoPendentePdf} de 5 estrelas`}
            </span>
          </div>

          <DialogFooter>
            <Button variant="ghost" onClick={() => { 
              // Se clicar em "Apenas Importar", ignora o cadastro do fornecedor e importa o abastecimento
              if (pdfPendingData) { 
                apiPost("/abastecimentos/importar", pdfPendingData).then(() => {
                  toast.success("Nota Fiscal importada sem cadastrar fornecedor.");
                  invalidate();
                  setOpenPdfConfirm(false);
                  setPdfPendingData(null);
                  setAvaliacaoPendentePdf(0);
                });
              }
            }}>Apenas Importar</Button>
            <Button 
              onClick={confirmarFornecedorPdf} 
              disabled={avaliacaoPendentePdf === 0}
            >
              Cadastrar com Avaliação e Importar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    '''
        idx_fim = c.rfind('</div>')
        if idx_fim != -1:
            c = c[:idx_fim] + modal_jsx + c[idx_fim:]
            print("✅ Modal de avaliação do PDF adicionado.")

    # 4. Garantir import do Star
    if 'Star' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus', 'import { Fuel, Plus, Star')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)