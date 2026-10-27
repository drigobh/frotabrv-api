import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_GRID_DEF_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_grid(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir o Cabeçalho (TableHeader)
    padrao_thead = re.compile(r'<TableHeader>[\s\S]*?</TableHeader>', re.DOTALL)
    novo_thead = '''<TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              {["Data", "Origem", "NF", "Cód.Trans", "Veículo", "Motorista", "Produto", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map(h => (
                <TableHead key={h} className="text-[10px] uppercase text-slate-500 px-2 text-center">{h}</TableHead>
              ))}
            </TableRow>
          </TableHeader>'''
    if padrao_thead.search(c):
        c = padrao_thead.sub(novo_thead, c)
        print("✅ Cabeçalho (TableHeader) corrigido.")

    # 2. Corrigir o Corpo (TableBody) garantindo a ordem exata das células
    padrao_tbody = re.compile(r'<TableBody>[\s\S]*?</TableBody>', re.DOTALL)
    novo_tbody = '''<TableBody>
            {rowsFiltradas.length === 0 && (
              <TableRow>
                <TableCell colSpan={15} className="py-10 text-center text-slate-500">
                  Nenhum abastecimento encontrado.
                </TableCell>
              </TableRow>
            )}
            {rowsFiltradas.map((r: any) => (
              <TableRow key={r.id} className="border-slate-800/70">
                {/* Data */}
                <TableCell className="text-xs text-slate-400 px-2 text-center">{dataBR(r.data)}</TableCell>
                {/* Origem */}
                <TableCell className="text-center px-2">
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${r.origem === 'manual' ? 'bg-slate-800 text-slate-300' : r.origem === 'pdf' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                    {r.origem}
                  </span>
                </TableCell>
                {/* NF */}
                <TableCell className="text-center px-2">
                  {r.numero_nf ? <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded">{r.numero_nf}</span> : <span className="text-[10px] text-slate-500">—</span>}
                </TableCell>
                {/* Cód.Trans */}
                <TableCell className="text-center px-2 text-[10px] text-slate-400 font-mono">
                  {r.codigo_transacao || "—"}
                </TableCell>
                {/* Veículo */}
                <TableCell className="text-xs font-medium text-slate-200 px-2 text-center">
                  {r.veiculo_label?.split(" · ")[0] || "—"}
                </TableCell>
                {/* Motorista */}
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">
                  {r.motorista_label ?? "—"}
                </TableCell>
                {/* Produto */}
                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">
                  {r.produto || "—"}
                </TableCell>
                {/* Litros */}
                <TableCell className="tabular-nums px-2 text-center">{num(r.litros, 3)}</TableCell>
                {/* R$/L */}
                <TableCell className="tabular-nums px-2 text-center">{brl(r.preco_litro)}</TableCell>
                {/* Total */}
                <TableCell className="tabular-nums px-2 text-center">{brl(r.valor_total)}</TableCell>
                {/* Posto (com estrelas) */}
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
                {/* KM */}
                <TableCell className="tabular-nums px-2 text-center">{num(r.km)}</TableCell>
                {/* Rodados */}
                <TableCell className="tabular-nums px-2 text-center">{r.km_rodados != null ? num(r.km_rodados) : "—"}</TableCell>
                {/* Média */}
                <TableCell className="tabular-nums px-2 text-center">{r.media_km_l != null ? num(r.media_km_l) : "—"}</TableCell>
                {/* Ações */}
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
            ))}
          </TableBody>'''
    
    if padrao_tbody.search(c):
        c = padrao_tbody.sub(novo_tbody, c)
        print("✅ Corpo (TableBody) corrigido e alinhado com o cabeçalho.")
    else:
        print("⚠️ Não foi possível encontrar o TableBody.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_grid(raiz)