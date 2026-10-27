import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ED_LOTE_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar os estados para o Modal de Fornecedores Pendentes
    if 'pendingEdenredRows' not in c:
        c = c.replace(
            'const [excluirId, setExcluirId] = useState<string | null>(null);',
            '''const [excluirId, setExcluirId] = useState<string | null>(null);
  const [pendingEdenredRows, setPendingEdenredRows] = useState<any[]>([]);
  const [openFornecedoresModal, setOpenFornecedoresModal] = useState(false);
  const [fornecedoresPendentes, setFornecedoresPendentes] = useState<any[]>([]);
  const [selectedFornecedores, setSelectedFornecedores] = useState<Record<string, boolean>>({});
  const [avaliacoesPendentes, setAvaliacoesPendentes] = useState<Record<string, number>>({});'''
        )

    # 2. Substituir a função handleImportEdenred
    padrao = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const executarImportacaoEdenred = async (rowsData: any[]) => {
    setImportProgress({ total: rowsData.length, current: 0, errors: [] });
    let importados = 0; const erros: any[] = [];
    
    for (let i = 0; i < rowsData.length; i++) {
      const payload = rowsData[i];
      try { 
        await apiPost("/abastecimentos/importar", payload); 
        importados++; 
        await new Promise(resolve => setTimeout(resolve, 150));
      } catch (err: any) { 
        erros.push({ linha: i + 1, placa: payload.placa, erro: err.message && err.message.includes("409") ? "Já importado" : (err.message || "Erro") }); 
      }
      setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
    }
    
    setImportProgress(prev => prev ? { ...prev, current: rowsData.length, errors: erros } : null);
    if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
    else if (importados > 0) toast.warning(`${importados} importados, mas ${erros.length} deram erro ou já existiam.`);
    else toast.error("Todos os registros já foram importados ou deram erro.");
    
    invalidate();
    setOpenFornecedoresModal(false);
  };

  const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { toast.error("Planilha vazia."); return; }

      const headerRow = rows[0].map((c: any) => String(c).toUpperCase().trim());
      const findIdx = (name: string) => headerRow.findIndex(h => h.replace(/\\s+/g, '').includes(name.replace(/\\s+/g, '')));

      const idxCod = findIdx("CODIGO TRANSACAO");
      const idxData = findIdx("DATA TRANSACAO");
      const idxPlaca = findIdx("PLACA");
      const idxMotorista = findIdx("NOME MOTORISTA");
      const idxProduto = findIdx("TIPO COMBUSTIVEL");
      const idxLitros = findIdx("LITROS");
      const idxPreco = findIdx("VL/LITRO") !== -1 ? findIdx("VL/LITRO") : findIdx("V. LITRO");
      const idxKm = findIdx("HODOMETRO");
      const idxKmRodados = findIdx("KM RODADOS");
      const idxMedia = findIdx("KM/LITRO");
      const idxPosto = findIdx("NOME ESTABELECIMENTO");
      const idxValor = findIdx("VALOR EMISSAO");
      const idxCidade = findIdx("CIDADE");
      const idxEstado = findIdx("UF");
      const idxEndereco = findIdx("ENDERECO");
      const idxBairro = findIdx("BAIRRO");

      const parseNum = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) {
            if (str.lastIndexOf(',') > str.lastIndexOf('.')) str = str.replace(/\\./g, '').replace(',', '.');
            else str = str.replace(/,/g, '');
        } else if (str.includes(',')) {
            str = str.replace(',', '.');
        }
        return Number(str) || 0;
      };

      const mapFornecedores = new Set(fornecedores.map((f: any) => f.nome.toUpperCase().trim()));
      const unregistered: Record<string, any> = {};
      const payloads: any[] = [];

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || String(row[idxData]).toUpperCase().includes("TOTAL")) continue;

        const dataStr = String(row[idxData]).trim();
        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        const kmNum = parseNum(row[idxKm]);
        const litrosNum = parseNum(row[idxLitros]);
        const precoNum = parseNum(row[idxPreco]);
        const valorNum = idxValor !== -1 ? parseNum(row[idxValor]) : (litrosNum * precoNum);
        const kmRodadosNum = idxKmRodados !== -1 ? parseNum(row[idxKmRodados]) : null;
        const mediaNum = idxMedia !== -1 ? parseNum(row[idxMedia]) : null;

        const motoristaNome = idxMotorista !== -1 ? String(row[idxMotorista] || "").trim() : "";
        let motoristaId = NENHUM;
        if (motoristaNome && motoristas.data) {
          const mot = motoristas.data.find((m: any) => m.nome.toUpperCase() === motoristaNome.toUpperCase() || m.nome.toUpperCase().includes(motoristaNome));
          if (mot) motoristaId = mot.id;
        }

        const fornecedorNome = String(row[idxPosto] || "").trim();
        const cidade = idxCidade !== -1 ? String(row[idxCidade] || "").trim() : "";
        const estado = idxEstado !== -1 ? String(row[idxEstado] || "").trim() : "";
        const endereco = idxEndereco !== -1 ? String(row[idxEndereco] || "").trim() : "";
        const bairro = idxBairro !== -1 ? String(row[idxBairro] || "").trim() : "";

        if (fornecedorNome && !mapFornecedores.has(fornecedorNome.toUpperCase().trim())) {
          unregistered[fornecedorNome] = { nome: fornecedorNome, cidade, estado, endereco, bairro };
        }

        let cnpjFormatado = "";
        const existingForn = fornecedores.find((f: any) => f.nome.toUpperCase() === fornecedorNome.toUpperCase());
        if (existingForn && existingForn.documento) {
          cnpjFormatado = existingForn.documento;
        }

        payloads.push({
          data: dataFinal, placa: String(row[idxPlaca] || "").toUpperCase().trim(), km: kmNum,
          motorista_id: motoristaId, fornecedor: fornecedorNome, cnpj: cnpjFormatado,
          cidade, estado, litros: litrosNum, preco_litro: precoNum, valor_total: valorNum,
          km_rodados: kmRodadosNum, media_km_l: mediaNum,
          produto: String(row[idxProduto] || "DIESEL").toUpperCase(),
          codigo_transacao: String(row[idxCod] || "").trim(),
          hora: horaFinal, numero_nf: null, chave_nfe: null, origem: "excel"
        });
      }

      const pendentes = Object.values(unregistered);
      if (pendentes.length > 0) {
        // Configura o estado do modal
        const initialSelected: Record<string, boolean> = {};
        const initialAvaliacoes: Record<string, number> = {};
        pendentes.forEach(f => {
          initialSelected[f.nome] = true;
          initialAvaliacoes[f.nome] = 0;
        });
        setSelectedFornecedores(initialSelected);
        setAvaliacoesPendentes(initialAvaliacoes);
        setFornecedoresPendentes(pendentes);
        setPendingEdenredRows(payloads);
        setOpenFornecedoresModal(true);
      } else {
        // Nenhum fornecedor pendente, importa direto
        executarImportacaoEdenred(payloads);
      }
    } catch (error) {
      console.error(error); toast.error("Erro ao ler Edenred."); setImportProgress(null);
    }
  };

  const confirmarCadastroLote = async () => {
    const selecionados = fornecedoresPendentes.filter(f => selectedFornecedores[f.nome]);
    for (const f of selecionados) {
      try {
        await apiPost("/fornecedores", {
          nome: f.nome,
          documento: "", // Planilha não traz CNPJ
          endereco: f.endereco,
          bairro: f.bairro,
          cidade: f.cidade,
          estado: f.estado,
          ativo: true,
          avaliacao: avaliacoesPendentes[f.nome] || 0
        });
      } catch (err: any) {
        if (!err.message?.includes("409")) console.error(`Erro ao cadastrar ${f.nome}`, err);
      }
    }
    await refetchFornecedores();
    toast.success(`${selecionados.length} fornecedores cadastrados!`);
    executarImportacaoEdenred(pendingEdenredRows);
  };

  const toggleAllFornecedores = (checked: boolean) => {
    const newSelected: Record<string, boolean> = {};
    fornecedoresPendentes.forEach(f => { newSelected[f.nome] = checked; });
    setSelectedFornecedores(newSelected);
  };'''

    if padrao.search(c):
        c = padrao.sub(lambda m: nova_funcao, c)
        print("✅ Frontend: Função do Edenred atualizada para cadastro em lote.")
    else:
        print("⚠️ Não foi possível encontrar a função handleImportEdenred.")

    # 3. Adicionar o Alerta Vermelho Piscando no Grid (Coluna Posto)
    old_posto_cell = '''<span className="truncate w-full" title={r.fornecedor || r.posto}>{r.fornecedor || r.posto || "—"}</span>'''
    new_posto_cell = '''<span className="truncate w-full" title={r.fornecedor || r.posto}>{r.fornecedor || r.posto || "—"}</span>
                      {!r.cnpj && r.origem === 'excel' && (
                        <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center justify-center gap-1 mt-0.5">
                          <AlertTriangle className="size-3" /> CNPJ Pendente
                        </span>
                      )}'''
    if old_posto_cell in c:
        c = c.replace(old_posto_cell, new_posto_cell)
        print("✅ Frontend: Alerta vermelho adicionado na coluna Posto.")

    # 4. Adicionar o Modal de Fornecedores Pendentes no final do componente
    if 'openFornecedoresModal' in c and 'Fornecedores Pendentes' not in c:
        modal_html = '''
      <Dialog open={openFornecedoresModal} onOpenChange={setOpenFornecedoresModal}>
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto overflow-x-hidden">
          <DialogHeader>
            <DialogTitle>Fornecedores Pendentes de Cadastro</DialogTitle>
            <DialogDescription>
              Os seguintes fornecedores da planilha não estão cadastrados. Selecione quem deseja cadastrar agora.
            </DialogDescription>
          </DialogHeader>
          <div className="py-2">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-10">
                    <input type="checkbox" className="size-4 rounded border-slate-700 bg-slate-900" 
                      checked={fornecedoresPendentes.length > 0 && fornecedoresPendentes.every(f => selectedFornecedores[f.nome])}
                      onChange={(e) => toggleAllFornecedores(e.target.checked)} 
                    />
                  </TableHead>
                  <TableHead>Fornecedor</TableHead>
                  <TableHead>Cidade/UF</TableHead>
                  <TableHead>Avaliação</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {fornecedoresPendentes.map(f => (
                  <TableRow key={f.nome}>
                    <TableCell>
                      <input type="checkbox" className="size-4 rounded border-slate-700 bg-slate-900" 
                        checked={selectedFornecedores[f.nome] || false}
                        onChange={(e) => setSelectedFornecedores(s => ({ ...s, [f.nome]: e.target.checked }))} 
                      />
                    </TableCell>
                    <TableCell className="text-xs font-medium text-slate-200">{f.nome}</TableCell>
                    <TableCell className="text-xs text-slate-400">{f.cidade} / {f.estado}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map(star => (
                          <button type="button" key={star} onClick={() => setAvaliacoesPendentes(s => ({ ...s, [f.nome]: star }))} className="focus:outline-none hover:scale-110">
                            <Star className={`size-4 ${star <= (avaliacoesPendentes[f.nome] || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                          </button>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setOpenFornecedoresModal(false)}>Cancelar</Button>
            <Button onClick={confirmarCadastroLote}>Cadastrar Selecionados e Importar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      '''
        c = c.replace('<ConfirmDialog open={excluirId !== null}', modal_html + '<ConfirmDialog open={excluirId !== null}')
        print("✅ Frontend: Modal de cadastro em lote adicionado.")

    # 5. Garantir import do AlertTriangle
    if 'AlertTriangle' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus', 'import { Fuel, Plus, AlertTriangle')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)