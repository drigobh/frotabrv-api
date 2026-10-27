import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MAPEAMENTO_FIXO_{agora}.zip")
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

    # 1. Substituir a função handleImportEdenred inteira por mapeamento fixo (0 a 26)
    padrao_edenred = re.compile(r'const handleImportEdenred = async[\s\S]*?\n  \};', re.DOTALL)
    
    nova_funcao = '''const handleImportEdenred = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const rows = XLSX.utils.sheet_to_json<any[]>(sheet, { header: 1, raw: false });

      if (rows.length < 2) { toast.error("Planilha vazia."); return; }

      const totalLinhas = rows.length - 1;
      setImportProgress({ total: totalLinhas, current: 0, errors: [] });
      let importados = 0; const erros: any[] = [];

      const parseNum = (val: any) => {
        if (!val) return 0;
        let str = String(val).trim();
        if (str.includes('.') && str.includes(',')) str = str.replace(/\\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        const num = Number(str);
        return isNaN(num) ? 0 : num;
      };

      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || !row[4] || String(row[4]).toUpperCase().includes("TOTAL")) continue;

        // MAPEAMENTO FIXO EDENRED
        const codigo_transacao = String(row[0] || "").trim();
        const dataStr = String(row[4] || "").trim();
        const placa = String(row[5] || "").toUpperCase().trim();
        const motoristaNome = String(row[11] || "").trim().toUpperCase();
        const produto = String(row[13] || "DIESEL").toUpperCase();
        const litros = parseNum(row[14]);
        const preco_litro = parseNum(row[15]);
        const km = parseNum(row[16]);
        const km_rodados = parseNum(row[17]);
        const media_km_l = parseNum(row[18]);
        const valor_total = parseNum(row[19]);
        const fornecedor = String(row[21] || "").trim();
        const cidade = String(row[25] || "").trim();
        const estado = String(row[26] || "").trim();

        const dataFinal = dataStr.split(" ")[0];
        const horaFinal = dataStr.includes(" ") ? dataStr.split(" ")[1].substring(0, 5) : null;

        let motoristaId = NENHUM;
        if (motoristaNome && motoristas.data) {
          const mot = motoristas.data.find((m: any) => m.nome.toUpperCase() === motoristaNome || m.nome.toUpperCase().includes(motoristaNome));
          if (mot) motoristaId = mot.id;
        }

        // Busca CNPJ se o fornecedor já existir no banco
        let cnpjFormatado = "";
        const existingForn = fornecedores.find((f: any) => f.nome.toLowerCase() === fornecedor.toLowerCase());
        if (existingForn && existingForn.documento) cnpjFormatado = existingForn.documento;

        const payload = {
          data: dataFinal, placa, km, motorista_id: motoristaId, fornecedor, cnpj: cnpjFormatado, cidade, estado,
          litros, preco_litro, valor_total, km_rodados, media_km_l, produto, codigo_transacao,
          hora: horaFinal, numero_nf: null, chave_nfe: null, origem: "excel"
        };

        try { 
          await apiPost("/abastecimentos/importar", payload); 
          importados++; 
          await new Promise(resolve => setTimeout(resolve, 100)); 
        } catch (err: any) { 
          erros.push({ linha: i + 1, placa: placa, erro: err.message || "Erro" }); 
        }
        setImportProgress(prev => prev ? { ...prev, current: prev.current + 1, errors: erros } : null);
      }

      setImportProgress(prev => prev ? { ...prev, current: totalLinhas, errors: erros } : null);
      if (erros.length === 0) toast.success(`${importados} Edenred importados!`);
      invalidate();
    } catch (error) {
      console.error(error); toast.error("Erro ao ler Edenred."); setImportProgress(null);
    }
  };'''

    if padrao_edenred.search(c):
        c = padrao_edenred.sub(lambda m: nova_funcao, c)

    # 2. Corrigir o Grid para exibir os dados alinhados
    padrao_tbody = re.compile(r'\{rowsFiltradas\.map\(\(r\) => \([\s\S]*?<\/TableRow>\s*\)\)\}', re.DOTALL)
    
    novo_tbody = '''{rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                <TableCell className="text-xs text-slate-400 px-2 text-center">{dataBR(r.data)}</TableCell>
                <TableCell className="text-center px-2"><span className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${r.origem === 'manual' ? 'bg-slate-800 text-slate-300' : r.origem === 'pdf' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>{r.origem}</span></TableCell>
                <TableCell className="text-center px-2">{r.numero_nf ? <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">{r.numero_nf}</span> : <span className="text-[10px] text-slate-500">—</span>}</TableCell>
                <TableCell className="text-center px-2 text-[10px] text-slate-400 font-mono">{r.codigo_transacao || "—"}</TableCell>
                <TableCell className="text-xs font-medium text-slate-200 px-2 text-center">{r.veiculo_label?.split(" · ")[0]}</TableCell>
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.motorista_label ?? "—"}</TableCell>
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.produto || "—"}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{num(r.litros, 3)}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{brl(r.preco_litro)}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{brl(r.valor_total)}</TableCell>
                <TableCell className="text-slate-300 px-2 max-w-[150px] text-center align-middle">
                  <div className="flex flex-col items-center justify-center">
                    <span className="truncate w-full" title={r.fornecedor || r.posto}>{r.fornecedor || r.posto || "—"}</span>
                    {(() => {
                      const docLimpo = (r.cnpj || "").replace(/\\D/g, '');
                      const nomeLimpo = (r.fornecedor || r.posto || "").toUpperCase();
                      const forn = fornecedores?.find((f: any) => (f.documento && f.documento.replace(/\\D/g, '') === docLimpo && docLimpo.length > 0) || (f.nome && f.nome.toUpperCase() === nomeLimpo));
                      if (!forn || !forn.avaliacao || forn.avaliacao === 0) return null;
                      return (
                        <div className="flex gap-0.5 mt-1 justify-center">
                          {[1, 2, 3, 4, 5].map(star => <Star key={star} className={`size-2.5 ${star <= forn.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-700'}`} />)}
                        </div>
                      );
                    })()}
                  </div>
                </TableCell>
                <TableCell className="tabular-nums px-2 text-center">{num(r.km)}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                <TableCell className="tabular-nums px-2 text-center">{r.media_km_l != null ? num(r.media_km_l) : "—"}</TableCell>
                <TableCell className="text-center px-2">
                  <div className="flex items-center justify-center gap-1">
                    <Button size="icon-sm" variant="ghost" onClick={() => { 
                      setForm({ ...vazio(hoje), ...r, litros: String(r.litros || ""), preco_litro: String(r.preco_litro || ""), km: String(r.km || ""), origem: r.origem || "excel", fornecedor: (r as any).fornecedor || r.posto || "", cnpj: r.cnpj || "", cidade: (r as any).cidade || "", estado: (r as any).estado || "", codigo_transacao: (r as any).codigo_transacao || "" }); 
                      setOpen(true); setEditingId(r.id); 
                    }} title="Visualizar"><Eye className="size-4 text-emerald-400" /></Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => {
                      if (r.origem === "pdf") toast.error("Proibido editar arquivo importado via PDF.");
                      else if (r.origem === "excel") toast.error("Proibido editar arquivo importado via Excel.");
                      else abrirEdicao(r);
                    }} title="Editar"><Pencil className="size-4 text-sky-400" /></Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)} title="Excluir"><Trash2 className="size-4 text-red-400" /></Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}'''

    if padrao_tbody.search(c):
        c = padrao_tbody.sub(novo_tbody, c)
    else:
        print("⚠️ Aviso: Não foi possível encontrar o bloco do TableRow. O grid pode precisar de ajuste manual.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Correção aplicada: Mapeamento fixo de colunas e grid realinhado!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)