import os
import re

def fix_backend(raiz):
    # 1. Bloquear importação dupla no Backend
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona a checagem antes de inserir no banco
    if 'Verifica se a nota já foi importada' not in c:
        c = c.replace(
            '    await db.abastecimentos.insert_one(doc)\n    doc.pop("_id", None)\n    return doc',
            '''    # Verifica se a nota já foi importada (Duplicidade)
    chave_nfe_recebida = body.get("chave_nfe")
    numero_nf_recebido = body.get("numero_nf")
    
    if chave_nfe_recebida:
        existente = await db.abastecimentos.find_one({"chave_nfe": chave_nfe_recebida})
        if existente:
            raise HTTPException(409, "Esta nota fiscal já foi importada (Chave NF-e duplicada).")
    elif numero_nf_recebido and body.get("cnpj"):
        existente = await db.abastecimentos.find_one({"numero_nf": numero_nf_recebido, "cnpj": body.get("cnpj")})
        if existente:
            raise HTTPException(409, "Esta nota fiscal já foi importada (Número da NF e CNPJ duplicados).")

    await db.abastecimentos.insert_one(doc)
    doc.pop("_id", None)
    return doc'''
        )
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Backend: Bloqueio de notas fiscais duplicadas ativado.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 2. Adicionar a Query de fornecedores (caso não exista no topo do arquivo)
    if 'const { data: fornecedores = [] } = useQuery' not in c:
        c = c.replace(
            'const { data: motoristas = { data: [] } } = useMotoristas();',
            'const { data: motoristas = { data: [] } } = useMotoristas();\n  const { data: fornecedores = [] } = useQuery({ queryKey: ["fornecedores"], queryFn: () => apiGet<any[]>("/fornecedores") });'
        )

    # 3. Atualizar a coluna Posto no Grid para mostrar a avaliação (Estrelas)
    old_posto_cell = '<TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">{r.fornecedor || r.posto || "—"}</TableCell>'
    new_posto_cell = '''<TableCell className="text-slate-300 px-2 truncate max-w-[150px] text-center">
                      <div className="flex flex-col items-center justify-center">
                        <span>{r.fornecedor || r.posto || "—"}</span>
                        {(() => {
                          const docLimpo = (r.cnpj || "").replace(/\\D/g, '');
                          const forn = fornecedores.find((f: any) => f.nome === r.fornecedor || (f.documento && f.documento.replace(/\\D/g, '') === docLimpo));
                          if (!forn || !forn.avaliacao) return null;
                          return (
                            <div className="flex gap-0.5 mt-0.5 justify-center">
                              {[1, 2, 3, 4, 5].map(star => (
                                <Star key={star} className={`size-2.5 ${star <= forn.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-700'}`} />
                              ))}
                            </div>
                          );
                        })()}
                      </div>
                    </TableCell>'''
    c = c.replace(old_posto_cell, new_posto_cell)

    # 4. Tratar o erro 409 (Duplicidade) no onError da mutação salvar (para importações)
    # Se der erro 409 na importação, ele avisa no Toast
    c = c.replace(
        'onError: (e: any) => toast.error(errMsg(e)),',
        'onError: (e: any) => { if (e.message && e.message.includes("409")) toast.error("Esta nota fiscal já foi importada no sistema."); else toast.error(errMsg(e)); },'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Estrelas adicionadas na coluna Posto e tratamento de erro 409.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)