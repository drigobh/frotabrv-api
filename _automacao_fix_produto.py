import os

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Atualizar o modelo AbastecimentoCreate
    if "combustivel_id" not in c:
        c = c.replace(
            'fornecedor: Optional[str] = None\n    origem: Optional[str] = "manual"',
            'fornecedor: Optional[str] = None\n    combustivel_id: Optional[str] = None\n    produto: Optional[str] = None\n    origem: Optional[str] = "manual"'
        )

    # 2. Atualizar a rota criar (manual) para buscar o nome do combustível
    if "produto_nome = doc.get" not in c:
        c = c.replace(
            'doc = payload.dict()',
            '''doc = payload.dict()
    produto_nome = doc.get("produto")
    if not produto_nome and doc.get("combustivel_id"):
        comb = await db.combustiveis.find_one({"id": doc["combustivel_id"]}, {"_id": 0})
        if comb:
            produto_nome = comb["nome"]
    doc["produto"] = produto_nome or "Diesel S-10"'''
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend atualizado com suporte a produto no cadastro manual.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar extração de produto no handleImportPDF
    if "const produtoMatch" not in c:
        c = c.replace(
            'const litrosMatch = text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)\\s+([\\d.,]+)/i) || text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)/i);',
            '''const litrosMatch = text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)\\s+([\\d.,]+)/i) || text.match(/L\\s+([\\d.,]+)\\s+([\\d.,]+)/i);
      const produtoMatch = text.match(/DESCRIÇÃO DOS PRODUTOS \\/ SERVIÇOS\\s+([A-Z0-9\\s]+)/i) || text.match(/(OLEO DIESEL|DIESEL|ARLA)[A-Z0-9\\s]*/i);
      const produtoStr = produtoMatch ? produtoMatch[1] || produtoMatch[0] : "DIESEL S-10";'''
        )
        # Adicionar no payload do PDF
        c = c.replace(
            'preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0, km: kmMatch ? Number(kmMatch[1]) : 0, origem: "pdf"',
            'preco_litro: litrosMatch ? parseNum(litrosMatch[2]) : 0, km: kmMatch ? Number(kmMatch[1]) : 0, origem: "pdf", produto: produtoStr'
        )

    # 2. Adicionar a coluna Produto no Header
    if '"Produto"' not in c:
        c = c.replace(
            '{["Data", "Origem", "Veículo", "Motorista", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map(h => <TableHead key={h} className="text-[10px] uppercase text-slate-500 px-2 text-center">{h}</TableHead>)}',
            '{["Data", "Origem", "Veículo", "Motorista", "Produto", "Litros", "R$/L", "Total", "Posto", "KM", "Rodados", "Média", "Ações"].map(h => <TableHead key={h} className="text-[10px] uppercase text-slate-500 px-2 text-center">{h}</TableHead>)}'
        )

    # 3. Adicionar a célula Produto no Body
    if "r.produto" not in c:
        c = c.replace(
            '<TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.motorista_label ?? "—"}</TableCell>',
            '<TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.motorista_label ?? "—"}</TableCell>\n                <TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.produto || "—"}</TableCell>'
        )

    # 4. Atualizar colSpan de 12 para 13
    c = c.replace('colSpan={12}', 'colSpan={13}')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado com a coluna Produto e extração do PDF.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)