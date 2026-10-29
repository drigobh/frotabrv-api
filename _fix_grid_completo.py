import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_GRID_COMPLETO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Fornecedores.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Encontrar o bloco inteiro do map (do rowsFiltradas.map até o fechamento do TableBody)
    padrao_tbody = re.compile(r'\{rowsFiltradas\.map\(\(r\) => \([\s\S]*?</TableRow>\s*\)\)', re.DOTALL)
    
    novo_bloco = '''{rowsFiltradas.map((r) => (
              <TableRow key={r.id} className="border-slate-800/70">
                
                {/* 1. FORNECEDOR */}
                <TableCell className="font-medium text-slate-200">
                  <div className="flex items-center gap-2">
                    {r.tipo_pessoa === 'PJ' ? <Building2 className="size-4 text-sky-400" /> : <User className="size-4 text-purple-400" />}
                    <div>
                      <div className="flex items-center gap-2">
                        {r.nome}
                        <span className="text-[9px] font-bold bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{r.tipo_pessoa}</span>
                      </div>
                      <div className="text-slate-500 font-mono text-xs flex flex-col">
                        <span>{r.documento || "—"}</span>
                        {(!r.documento || String(r.documento).trim() === "") && (
                          <span className="text-red-500 animate-pulse font-bold text-[9px] flex items-center gap-1 mt-1">
                            <AlertTriangle className="size-3" /> CNPJ Pendente
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </TableCell>
                
                {/* 2. EMPRESA / UNIDADE */}
                <TableCell className="text-xs text-slate-400">
                  {empresas.find((e: any) => e.id === r.empresa_id)?.nome_fantasia || "—"}
                </TableCell>
                
                {/* 3. TIPO DE FORNECEDOR */}
                <TableCell className="text-xs text-slate-400">
                  {tipos.find((t: any) => t.id === r.tipo_fornecedor_id)?.nome || "—"}
                </TableCell>
                
                {/* 4. ROTA */}
                <TableCell className="text-xs text-slate-400 text-center">
                  {(() => {
                    if (!r.endereco || !r.cidade) return "—";
                    const emp = empresas.find((e: any) => e.id === r.empresa_id);
                    if (!emp || !emp.endereco) return "—";
                    const origem = encodeURIComponent(`${emp.endereco}, ${emp.cidade}, ${emp.estado}`);
                    const destino = encodeURIComponent(`${r.endereco}, ${r.cidade}, ${r.estado}`);
                    return (
                      <a href={`https://www.google.com/maps/dir/?api=1&origin=${origem}&destination=${destino}`} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline flex items-center justify-center gap-1">
                        <MapPin className="size-3" /> Ver Rota
                      </a>
                    );
                  })()}
                </TableCell>

                {/* 5. LOCALIZAÇÃO */}
                <TableCell className="text-slate-400 text-xs">
                  <span className="flex items-center gap-1">
                    <MapPin className="size-3" /> {r.cidade ? `${r.cidade}/${r.estado}` : "—"}
                  </span>
                </TableCell>
                
                {/* 6. CONTATO */}
                <TableCell className="text-xs text-slate-400 text-center">
                  <div className="flex flex-col items-center justify-center">
                    <span className="font-medium text-slate-300">{r.contato || "—"}</span>
                    {r.whatsapp && (
                      <a href={`https://wa.me/55${r.whatsapp.replace(/\\D/g, '')}`} target="_blank" rel="noreferrer" className="flex items-center gap-1 text-emerald-400 hover:text-emerald-300 mt-1">
                        <MessageCircle className="size-4 animate-pulse" />
                        <span className="text-[10px]">{r.whatsapp}</span>
                      </a>
                    )}
                  </div>
                </TableCell>
                
                {/* 7. AVALIAÇÃO */}
                <TableCell className="text-center">
                  <div className="flex justify-center gap-0.5">
                    {[1, 2, 3, 4, 5].map(star => (
                      <Star key={star} className={`size-3 ${star <= (r.avaliacao || 0) ? 'fill-amber-400 text-amber-400' : 'text-slate-700'}`} />
                    ))}
                  </div>
                </TableCell>
                
                {/* 8. STATUS */}
                <TableCell className="text-center">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${r.ativo ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                    {r.ativo ? "Ativo" : "Inativo"}
                  </span>
                </TableCell>
                
                {/* 9. AÇÕES */}
                <TableCell className="text-center">
                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>
                  <Button size="icon-sm" variant="ghost" onClick={() => setExcluirId(r.id)}><Trash2 className="size-4 text-red-300" /></Button>
                </TableCell>
              </TableRow>
            ))}'''

    if padrao_tbody.search(c):
        c = padrao_tbody.sub(lambda m: novo_bloco, c, count=1)
        print("✅ Todas as células foram reconstruídas na ordem correta.")
    else:
        print("⚠️ Não encontrei o bloco do map.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)