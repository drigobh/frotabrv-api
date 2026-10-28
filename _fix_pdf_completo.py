import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_PDF_COMPLETO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    for p in ["frontend/src/pages/Abastecimentos.tsx", "app/backend/routers/abastecimentos.py"]:
        caminho_abs = os.path.join(raiz, p)
        if os.path.exists(caminho_abs):
            with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def remover_tudo(c, nome):
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

def remover_dialog(c, var):
    while True:
        idx = c.find(f'{{{var}')
        if idx == -1: break
        start = c.rfind('<Dialog', 0, idx)
        if start == -1: break
        end = c.find('</Dialog>', start)
        if end == -1: break
        end += len('</Dialog>')
        c = c[:start] + c[end:]
    return c

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Remove modais antigos do PDF
    for var in ['openPdfModal', 'openPdfConfirm', 'openPdfLoteConfirm']:
        c = remover_dialog(c, var)
    
    # Remove funções antigas
    for func in ["handleImportPDF", "executarImportacaoPDF", "cancelarImportacaoPDF", "confirmarFornecedorPdf"]:
        c = remover_tudo(c, func)
    print("✅ Frontend: código antigo do PDF removido.")

    # Adiciona estados se não existirem
    if 'const [openPdfModal, setOpenPdfModal] = useState(false);' not in c:
        c = c.replace(
            'const [importandoPDF, setImportandoPDF] = useState(false);',
            'const [importandoPDF, setImportandoPDF] = useState(false);\n  const [openPdfModal, setOpenPdfModal] = useState(false);\n  const [pdfArquivosLote, setPdfArquivosLote] = useState<File[]>([]);'
        )
        print("✅ Estados do modal do PDF adicionados.")

    idx_return = c.find('  return (')
    if idx_return == -1:
        print("⚠️ Return não encontrado no frontend.")
        return

    # Nova função com TODO o fluxo: lote, modal de confirmação, validação de fornecedor e cadastro
    nova_funcao = '''  const handleImportPDF = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setPdfArquivosLote(Array.from(files));
    setOpenPdfModal(true);
    e.target.value = "";
  };

  const executarImportacaoPDFLote = async () => {
    if (importandoPDF || pdfArquivosLote.length === 0) return;

    setImportandoPDF(true);
    setOpenPdfModal(false);

    let importados = 0;
    const erros: string[] = [];

    for (let fileIdx = 0; fileIdx < pdfArquivosLote.length; fileIdx++) {
      const file = pdfArquivosLote[fileIdx];
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
        if (!veiculo) { erros.push(`${file.name}: veículo não encontrado`); continue; }

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

        // Cadastra fornecedor automaticamente se não existir
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
        importados++;
        await new Promise(r => setTimeout(r, 150));
      } catch (err: any) {
        erros.push(`${file.name}: ${err.message || "Erro"}`);
      }
    }

    if (erros.length === 0) toast.success(`${importados} PDF(s) importado(s) com sucesso!`);
    else if (importados > 0) toast.warning(`${importados} importado(s), ${erros.length} com erro.`);
    else toast.error("Nenhum PDF importado. Verifique os arquivos.");

    invalidate();
    setImportandoPDF(false);
    setPdfArquivosLote([]);
  };
'''
    c = c[:idx_return] + nova_funcao + c[idx_return:]

    # Corrigir input para aceitar múltiplos
    c = re.sub(
        r'<input type="file" accept="\.pdf"[^>]*/>',
        '<input type="file" accept=".pdf" multiple ref={fileInputRef} onChange={handleImportPDF} className="hidden" />',
        c
    )

    # Corrigir botão para abrir direto o seletor
    c = re.sub(
        r'<Button[^>]*onClick=\{[^}]*fileInputRef\.current\?\.click\(\)[^}]*\}[^>]*>[\s\S]*?Importar NF[\s\S]*?</Button>',
        '<Button variant="outline" disabled={importandoPDF} onClick={() => fileInputRef.current?.click()}><FileText className="size-4 mr-2" /> {importandoPDF ? "Importando..." : "Importar NF"}</Button>',
        c
    )

    # Adicionar Modal de Confirmação (igual Edenred)
    if 'Confirmar Importação de PDF' not in c:
        modal_jsx = '''
      <Dialog open={openPdfModal} onOpenChange={setOpenPdfModal}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Confirmar Importação de PDF</DialogTitle>
            <DialogDescription>
              Você selecionou <strong>{pdfArquivosLote.length}</strong> arquivo(s). Deseja importar todos?
            </DialogDescription>
          </DialogHeader>
          <div className="my-4 p-3 bg-red-950/40 border border-red-800/50 rounded-lg">
            <p className="text-red-400 animate-pulse font-bold text-sm text-center flex items-center justify-center gap-2">
              <AlertTriangle className="size-5" /> 
              Atenção: O sistema processará apenas esta leitura. Não clique várias vezes.
            </p>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => { setOpenPdfModal(false); setPdfArquivosLote([]); }}>
              Cancelar
            </Button>
            <Button onClick={executarImportacaoPDFLote} disabled={importandoPDF}>
              {importandoPDF ? "Importando..." : "Sim, Importar"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    '''
        idx_fim = c.rfind('</div>')
        if idx_fim != -1:
            c = c[:idx_fim] + modal_jsx + c[idx_fim:]
            print("✅ Modal de confirmação de PDF adicionado.")

    # Garantir import do AlertTriangle
    if 'AlertTriangle' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus', 'import { Fuel, Plus, AlertTriangle')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado com lote, modal, fornecedor e validação.")

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Ajusta checagem de duplicidade para bloquear por numero_nf mesmo sem CNPJ
    antigo = '''    elif numero_nf_recebido and cnpj_recebido:
            if await db.abastecimentos.find_one({"numero_nf": numero_nf_recebido, "cnpj": cnpj_recebido}):
                raise HTTPException(409, "Registro duplicado: Nota Fiscal já importada.")'''
    
    novo = '''    elif numero_nf_recebido:
            query_dup = {"numero_nf": numero_nf_recebido}
            if cnpj_recebido:
                query_dup["cnpj"] = cnpj_recebido
            if await db.abastecimentos.find_one(query_dup):
                raise HTTPException(409, "Registro duplicado: Nota Fiscal já importada.")'''

    if antigo in c:
        c = c.replace(antigo, novo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend atualizado: bloqueio por numero_nf mesmo sem CNPJ.")
    else:
        print("⚠️ Backend: trecho exato não encontrado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_frontend(raiz)
    fix_backend(raiz)
    print("\n✅ Script completo aplicado!")