import os
import datetime
import zipfile

def criar_backup_rapido(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_rapido_progresso_{agora}.zip"
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print("📦 Criando Backup Rápido...")
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        pasta_front = os.path.join(raiz, "frontend", "src")
        for root, dirs, files in os.walk(pasta_front):
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build']]
            for file in files:
                caminho_completo = os.path.join(root, file)
                caminho_relativo = os.path.relpath(caminho_completo, raiz)
                try:
                    zipf.write(caminho_completo, caminho_relativo)
                except Exception:
                    pass
    print(f"✅ Backup salvo: {nome_backup}")

def atualizar_abastecimentos(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo Abastecimentos.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adiciona os estados de progresso e erros (se não existirem)
    if "const [importProgress" not in conteudo:
        # Insere após a declaração de excluirId
        conteudo = conteudo.replace(
            '  const [excluirId, setExcluirId] = useState<string | null>(null);',
            '''  const [excluirId, setExcluirId] = useState<string | null>(null);
  const [importProgress, setImportProgress] = useState<{ total: number; current: number; errors: any[] } | null>(null);'''
        )
        print("✅ Estados de progresso adicionados.")

    # 2. Substitui a função handleImportXLS inteira
    # Encontra o início e o fim da função
    inicio = conteudo.find("const handleImportXLS = async")
    if inicio == -1:
        print("❌ Função handleImportXLS não encontrada.")
        return
    
    fim = conteudo.find("};", inicio) + 2

    funcao_nova = '''const handleImportXLS = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const rowRegex = /<tr[^>]*>([\\s\\S]*?)<\\/tr>/gi;
      const rows: string[][] = [];
      let rowMatch;

      while ((rowMatch = rowRegex.exec(text)) !== null) {
        const cells: string[] = [];
        let cellMatch;
        const cellRegexLocal = /<td[^>]*>([\\s\\S]*?)<\\/td>/gi;
        while ((cellMatch = cellRegexLocal.exec(rowMatch[1])) !== null) {
          let cellText = cellMatch[1];
          cellText = cellText.replace(/<[^>]+>/g, "").trim();
          cellText = cellText.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
          cells.push(cellText);
        }
        if (cells.length > 0) rows.push(cells);
      }

      if (rows.length === 0) {
        toast.error("Nenhuma linha encontrada no arquivo HTML.");
        return;
      }

      let startRow = -1;
      for (let i = 0; i < rows.length; i++) {
        const rowStr = rows[i].join(" ").toLowerCase();
        if (rowStr.includes("data") && rowStr.includes("placa") && rowStr.includes("litros")) {
          startRow = i + 1;
          break;
        }
      }

      if (startRow === -1) {
        toast.error("Cabeçalho da planilha não encontrado.");
        return;
      }

      const headerRow = rows[startRow - 1];
      const colIndex = (name: string) => headerRow.findIndex(h => h.toLowerCase().includes(name.toLowerCase()));

      const idxData = colIndex("data");
      const idxPlaca = colIndex("placa");
      const idxKm = colIndex("leitura");
      const idxPosto = colIndex("posto");
      const idxLitros = colIndex("litros");
      const idxPreco = colIndex("v. litro");

      if (idxData === -1 || idxPlaca === -1 || idxLitros === -1 || idxPreco === -1) {
        toast.error("Colunas essenciais não encontradas.");
        return;
      }

      const totalLinhas = rows.length - startRow;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      
      let importados = 0;
      const erros: any[] = [];

      for (let i = startRow; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[idxData] || row[idxData].toLowerCase().includes("total") || row[idxData].includes("Bsoft")) {
          setImportProgress(prev => prev ? { ...prev, current: prev.current + 1 } : null);
          continue;
        }

        let dataStr = row[idxData];
        if (dataStr.includes("/")) {
           const [d, m, y] = dataStr.split("/");
           dataStr = `${y}-${m}-${d}`;
        }

        const placaRaw = row[idxPlaca] || "";
        const placa = placaRaw.split("/")[0].replace("-", "").toUpperCase();

        const litrosRaw = Number(row[idxLitros].replace(/\\./g, "").replace(",", ".")) / 1000;
        const valorLitroRaw = Number(row[idxPreco].replace(/\\./g, "").replace(",", ".")) / 100;
        
        const payload = {
          data: dataStr,
          placa: placa,
          km: Number((row[idxKm] || "0").replace(/\\./g, "").replace(",", ".")),
          fornecedor: row[idxPosto] || "",
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
        } catch (err: any) {
          // Captura o erro da API
          const msgErro = err.response?.data?.detail || err.message || "Erro desconhecido";
          erros.push({
            linha: i + 1,
            placa: placa || "N/A",
            erro: msgErro
          });
        }

        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      
      if (erros.length === 0) {
        toast.success(`${importados} abastecimentos importados com sucesso!`);
        setTimeout(() => setImportProgress(null), 2000); // Fecha após 2s se não houver erros
      }
      
      invalidate();
    } catch (error) {
      console.error(error);
      toast.error("Erro ao ler o arquivo.");
      setImportProgress(null);
    }
  };'''

    conteudo = conteudo[:inicio] + funcao_nova + conteudo[fim:]
    print("✅ Função handleImportXLS atualizada com progresso.")

    # 3. Adiciona o Modal de Progresso no final do return (antes do fechamento da div principal)
    # Procura o final do return, que tem o ConfirmDialog
    if "<ConfirmDialog" in conteudo and "importProgress" in conteudo:
        modal_jsx = '''
      {/* Modal de Progresso de Importação */}
      <Dialog open={importProgress !== null} onOpenChange={() => {}}>
        <DialogContent className="sm:max-w-md" onPointerDownOutside={(e) => e.preventDefault()}>
          <DialogHeader>
            <DialogTitle>Importando Planilha</DialogTitle>
            <DialogDescription>
              {importProgress && importProgress.current < importProgress.total 
                ? "Por favor, aguarde enquanto processamos os registros..."
                : "Importação concluída!"}
            </DialogDescription>
          </DialogHeader>
          
          {importProgress && (
            <div className="space-y-4 py-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Progresso</span>
                <span className="font-mono text-slate-200">{importProgress.current} / {importProgress.total}</span>
              </div>
              
              {/* Barra de Progresso */}
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-sky-500 transition-all duration-300" 
                  style={{ width: `${(importProgress.current / importProgress.total) * 100}%` }}
                />
              </div>

              {/* Lista de Erros */}
              {importProgress.errors.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-2">
                    <AlertTriangle className="size-4" /> Erros encontrados ({importProgress.errors.length})
                  </h4>
                  <div className="max-h-40 overflow-y-auto rounded-md border border-slate-800 bg-slate-950 p-2">
                    <ul className="space-y-1 text-xs">
                      {importProgress.errors.map((err, idx) => (
                        <li key={idx} className="text-slate-300">
                          <span className="font-mono text-slate-500">Linha {err.linha}</span> - 
                          <span className="text-red-300 font-medium ml-1">{err.placa}</span>:
                          <span className="ml-1 text-slate-400">{err.erro}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            {importProgress && importProgress.current >= importProgress.total ? (
              <Button onClick={() => setImportProgress(null)}>Fechar</Button>
            ) : (
              <Button disabled variant="outline">Processando...</Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
'''
        # Insere antes do <ConfirmDialog
        conteudo = conteudo.replace("<ConfirmDialog", modal_jsx + "\n      <ConfirmDialog")
        print("✅ Modal de Progresso adicionado ao JSX.")

        # Adiciona o ícone AlertTriangle no import (se não existir)
        if "AlertTriangle" not in conteudo:
            conteudo = conteudo.replace(
                "Fuel, Plus, Trash2,",
                "Fuel, Plus, Trash2, AlertTriangle,"
            )
            print("✅ Ícone AlertTriangle adicionado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("✅ Arquivo Abastecimentos.tsx atualizado com sucesso.")

if __name__ == "__main__":
    raiz = os.getcwd()
    print("🤖 Iniciando Atualização do Modal de Progresso...")
    criar_backup_rapido(raiz)
    atualizar_abastecimentos(raiz)
    print("\n🚀 Concluído! Reinicie o Vite para testar.")