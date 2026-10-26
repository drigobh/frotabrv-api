import os

def fix_backend(raiz):
    # Adiciona created_by_name na rota de criação manual
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'doc["created_by_name"]' not in c:
        c = c.replace(
            'doc["created_by"] = user.get("id", "sistema")',
            'doc["created_by"] = user.get("id", "sistema")\n    doc["created_by_name"] = user.get("nome", user.get("email", "Sistema"))'
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Rota de criação salva created_by_name.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Corrigir a função abrirEdicao para incluir cidade, estado e avaliação
    import re
    padrao_edicao = re.compile(r'const abrirEdicao = \(r: Abastecimento\) => \{[\s\S]*?setOpen\(true\);\s*\}', re.DOTALL)
    nova_edicao = '''const abrirEdicao = (r: Abastecimento) => { 
    setEditingId(r.id); 
    setForm({ 
      data: r.data, 
      veiculo_id: r.veiculo_id, 
      motorista_id: r.motorista_id || NENHUM, 
      litros: String(r.litros), 
      preco_litro: String(r.preco_litro), 
      posto: r.posto || "", 
      km: String(r.km), 
      observacoes: r.observacoes || "", 
      numero_nf: r.numero_nf || "", 
      chave_nfe: r.chave_nfe || "", 
      hora: r.hora || "", 
      cnpj: r.cnpj || "", 
      fornecedor: (r as any).fornecedor || "", 
      origem: r.origem || "manual", 
      produto: (r as any).produto || "DIESEL", 
      combustivel_id: (r as any).combustivel_id || "",
      cidade: (r as any).cidade || "",
      estado: (r as any).estado || "",
      avaliacao: (r as any).avaliacao || 0
    }); 
    setOpen(true); 
  };'''
    if padrao_edicao.search(c):
        c = padrao_edicao.sub(lambda m: nova_edicao, c)

    # 2. Atualizar o Header da Tabela (adicionando a coluna NF)
    old_header = '''{["Data", "Origem", "Veículo", "Motorista", "Produto", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map(h => <TableHead key={h} className="text-[10px] uppercase text-slate-500 px-2 text-center">{h}</TableHead>)}'''
    new_header = '''{["Data", "Origem", "NF", "Veículo", "Motorista", "Produto", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map(h => <TableHead key={h} className="text-[10px] uppercase text-slate-500 px-2 text-center">{h}</TableHead>)}'''
    c = c.replace(old_header, new_header)
    c = c.replace('colSpan={13}', 'colSpan={14}')

    # 3. Atualizar o Corpo da Tabela (coluna NF, Posto fallback, botão de auditoria)
    old_body = '''<TableCell className="font-mono px-2 text-center">{r.veiculo_label.split(" · ")[0]}</TableCell>'''
    new_body = '''<TableCell className="text-center px-2">
                  {(r.numero_nf || r.chave_nfe) ? (
                    <span className="inline-flex items-center justify-center gap-1 bg-emerald-500/20 text-emerald-400 px-2 py-0.5 text-[10px] font-bold rounded" title={`NF: ${r.numero_nf || ''} | Chave: ${r.chave_nfe || ''}`}>
                      <CheckCircle2 className="size-3" /> OK
                    </span>
                  ) : (
                    <span className="inline-flex items-center justify-center gap-1 bg-red-500/20 text-red-400 px-2 py-0.5 text-[10px] font-bold rounded animate-pulse" title="Sem Nota Fiscal">
                      <AlertTriangle className="size-3" /> SEM
                    </span>
                  )}
                </TableCell>
                <TableCell className="font-mono px-2 text-center">{r.veiculo_label.split(" · ")[0]}</TableCell>'''
    c = c.replace(old_body, new_body, 1)

    c = c.replace(
        '<TableCell className="truncate max-w-[100px] text-slate-400 px-2 text-center">{r.posto}</TableCell>',
        '<TableCell className="truncate max-w-[100px] text-slate-400 px-2 text-center">{r.posto || (r as any).fornecedor || "—"}</TableCell>'
    )

    old_actions = '''<div className="flex gap-1 justify-center">
                      <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'''
    new_actions = '''<div className="flex gap-1 justify-center">
                      <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Cadastrado por: ${(r as any).created_by_name || (r as any).created_by || 'Sistema'}`}>
                        <Info className="size-4 text-slate-400" />
                      </Button>
                      <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'''
    c = c.replace(old_actions, new_actions, 1)

    # 4. Garantir que os ícones AlertTriangle e CheckCircle2 e Info estejam importados
    if 'AlertTriangle' not in c.split('lucide-react')[0]:
        c = c.replace('import { Fuel, Plus', 'import { Fuel, Plus, AlertTriangle, CheckCircle2, Info')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Grid atualizado com coluna NF, fallback de posto, auditoria e edição corrigida.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)
    