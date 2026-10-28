import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_LISTA_DUPLICADOS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def remover_funcao(c, nome):
    while True:
        inicio = c.find(f'const {nome} = ')
        if inicio == -1: break
        chave = c.find('{', inicio)
        if chave == -1: break
        count = 0
        i = chave
        while i < len(c):
            if c[i] == '{': count += 1
            elif c[i] == '}':
                count -= 1
                if count == 0:
                    fim = i + 1
                    while fim < len(c) and c[fim] not in '\n;': fim += 1
                    if fim < len(c) and c[fim] == ';': fim += 1
                    break
            i += 1
        c = c[:inicio] + c[fim:]
    return c

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar estados do Modal de Erros
    if 'const [duplicateErrors, setDuplicateErrors] = useState<any[]>([]);' not in c:
        c = c.replace(
            'const [pendingEdenredRows, setPendingEdenredRows] = useState<any[]>([]);',
            'const [pendingEdenredRows, setPendingEdenredRows] = useState<any[]>([]);\n  const [duplicateErrors, setDuplicateErrors] = useState<any[]>([]);\n  const [openDuplicateModal, setOpenDuplicateModal] = useState(false);'
        )
        print("✅ Estados do modal de erros adicionados.")

    # 2. Atualizar a função executarImportacaoEdenred (que serve para Edenred e BSOFT)
    padrao_exec = re.compile(r'const executarImportacaoEdenred = async \(rowsData: any\[\]\) => \{[\s\S]*?\n  \};', re.DOTALL)
    
    nova_exec = '''const executarImportacaoEdenred = async (rowsData: any[]) => {
    if (isImportingEdenredRef.current) return;
    isImportingEdenredRef.current = true;
    setImportandoEdenred(true);
    setOpenConfirmImport(false);
    setOpenFornecedoresModal(false);
    setImportProgress({ total: rowsData.length, current: 0, errors: [] });
    
    let importados = 0; 
    const errosDetalhados: any[] = [];
    
    try {
      for (let i = 0; i < rowsData.length; i++) {
        const payload = rowsData[i];
        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(resolve => setTimeout(resolve, 150));
        } catch (err: any) { 
          const isDup = err.message && (err.message.includes("409") || err.message.toLowerCase().includes("duplicado"));
          const motivo = isDup ? (err.message.split(":").pop()?.trim() || "Registro duplicado") : (err.message || "Erro de validação");
          
          let identificador = `Data: ${payload.data} | Placa: ${payload.placa}`;
          if (payload.numero_nf) identificador = `NF: ${payload.numero_nf} | ` + identificador;
          if (payload.codigo_transacao) identificador = `Cód: ${payload.codigo_transacao} | ` + identificador;

          errosDetalhados.push({ identificador, motivo });
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1 } : null);
      }
      
      if (errosDetalhados.length === 0) {
        toast.success(`${importados} registros importados com sucesso!`);
      } else if (importados > 0) {
        setDuplicateErrors(errosDetalhados);
        setOpenDuplicateModal(true);
        toast.warning(`${importados} importados, mas ${errosDetalhados.length} foram bloqueados.`);
      } else {
        setDuplicateErrors(errosDetalhados);
        setOpenDuplicateModal(true);
        toast.error("Nenhum registro importado. Verifique os bloqueios.");
      }
      
      invalidate();
    } finally {
      isImportingEdenredRef.current = false;
      setImportandoEdenred(false);
      setPendingEdenredRows([]);
      setImportProgress(null);
    }
  };'''

    if padrao_exec.search(c):
        c = padrao_exec.sub(lambda m: nova_exec, c)
        print("✅ Função executarImportacaoEdenred (Edenred/BSOFT) atualizada para listar erros.")

    # 3. Atualizar a função executarImportacaoPDFLote
    padrao_pdf = re.compile(r'const executarImportacaoPDFLote = async \(arquivos: File\[\]\) => \{[\s\S]*?\n  \};', re.DOTALL)
    
    nova_pdf = '''const executarImportacaoPDFLote = async (arquivos: File[]) => {
    if (importandoPDF || arquivos.length === 0) return;

    setImportandoPDF(true);
    let importados = 0;
    const errosDetalhados: any[] = [];
    let fornecedorPendenteData: any = null;

    for (let fileIdx = 0; fileIdx < arquivos.length; fileIdx++) {
      const file = arquivos[fileIdx];
      try {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await Promise.race([
          pdfjsLib.getDocument({ data: arrayBuffer }).promise,
          new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout (10s)")), 10000))
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
          errosDetalhados.push({ identificador: `Placa: ${placa}`, motivo: "Veículo não cadastrado" });
          continue; 
        }

        const kmMatch = text.match(/KM[:\\s]*(\\d+)/i);
        const km = kmMatch ? Number(kmMatch[1]) : 0;
        const dateMatch = text.match(/DATA DA EMISS[ÃA]O.*?(\\d{2}\\/\\d{2}\\/\\d{4})/i);
        let dataStr = new Date().toISOString().split("T")[0];
        if (dateMatch) { const [d, m, y] = dateMatch[1].split("/"); dataStr = `${y}-${m}-${d}`; }

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
            fornecedorPendenteData = { nome: fornecedorNome, cnpj: payload.cnpj, payload, restantes: arquivos.slice(fileIdx + 1) };
            break;
          }
        }

        await apiPost("/abastecimentos/importar", payload);
        importados++;
        await new Promise(r => setTimeout(r, 150));
      } catch (err: any) {
        const isDup = err.message && (err.message.includes("409") || err.message.toLowerCase().includes("duplicado"));
        const motivo = isDup ? (err.message.split(":").pop()?.trim() || "Registro duplicado") : (err.message || "Erro desconhecido");
        errosDetalhados.push({ identificador: `Arquivo: ${file.name}`, motivo });
      }
    }

    setImportandoPDF(false);

    if (fornecedorPendenteData) {
      setPdfPendingFornecedor(fornecedorPendenteData);
      setAvaliacaoPdf(0);
      setOpenPdfFornecedorConfirm(true);
      if (importados > 0) toast.success(`${importados} PDF(s) importado(s) antes da pausa.`);
      if (errosDetalhados.length > 0) {
         setDuplicateErrors(errosDetalhados);
         setOpenDuplicateModal(true);
      }
      return;
    }

    if (errosDetalhados.length === 0) {
      toast.success(`${importados} PDF(s) importado(s)!`);
    } else if (importados > 0) {
      setDuplicateErrors(errosDetalhados);
      setOpenDuplicateModal(true);
      toast.warning(`${importados} importado(s), mas ${errosDetalhados.length} bloqueados.`);
    } else {
      setDuplicateErrors(errosDetalhados);
      setOpenDuplicateModal(true);
      toast.error("Nenhum PDF importado.");
    }

    invalidate();
    setPdfArquivosLote([]);
  };'''

    if padrao_pdf.search(c):
        c = padrao_pdf.sub(lambda m: nova_pdf, c)
        print("✅ Função executarImportacaoPDFLote atualizada para listar erros.")

    # 4. Adicionar o Modal de Listagem de Erros/Duplicados no JSX
    if 'openDuplicateModal' in c and 'Registros Bloqueados' not in c:
        modal_jsx = '''
      <Dialog open={openDuplicateModal} onOpenChange={setOpenDuplicateModal}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-red-400 flex items-center gap-2">
              <AlertTriangle className="size-5" /> Registros Bloqueados / Não Importados
            </DialogTitle>
            <DialogDescription>
              Os registros abaixo já existiam no sistema (duplicados) ou continham erros de validação.
            </DialogDescription>
          </DialogHeader>
          <div className="py-2">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Identificação do Registro</TableHead>
                  <TableHead>Motivo do Bloqueio</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {duplicateErrors.map((err, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-xs font-mono text-slate-300">{err.identificador}</TableCell>
                    <TableCell className="text-xs text-red-400">{err.motivo}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter>
            <Button onClick={() => { setOpenDuplicateModal(false); setDuplicateErrors([]); }}>Entendido</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    '''
        idx_fim = c.rfind('</div>')
        if idx_fim != -1:
            c = c[:idx_fim] + modal_jsx + c[idx_fim:]
            print("✅ Modal de listagem de erros adicionado.")

    # 5. Garantir import do AlertTriangle
    if 'AlertTriangle' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus', 'import { Fuel, Plus, AlertTriangle')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)