import os

def fix_backend(raiz):
    # 1. Atualizar o Modelo de Manutenção para aceitar peças
    model_path = os.path.join(raiz, "app", "backend", "models", "manutencoes.py")
    with open(model_path, 'r', encoding='utf-8') as f:
        c = f.read()
    if 'pecas_utilizadas' not in c:
        c = c.replace(
            'pecas_substituidas: Optional[str] = None',
            'pecas_substituidas: Optional[str] = None\n    pecas_utilizadas: Optional[list[dict]] = None'
        )
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write(c)

    # 2. Atualizar o Router de Manutenção (Criar e Atualizar)
    router_path = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Lógica para dar baixa no estoque ao CRIAR
    if 'atualizar_estoque' not in c:
        # Função auxiliar
        helper = '''
async def atualizar_estoque(pecas_utilizadas: list[dict], multiplicador: int = -1):
    if not pecas_utilizadas: return
    for p in pecas_utilizadas:
        if p.get("peca_id") and p.get("quantidade"):
            await db.pecas.update_one(
                {"id": p["peca_id"]},
                {"$inc": {"quantidade_estoque": multiplicador * int(p["quantidade"])}}
            )
'''
        c = c.replace('@router.get("", response_model=None)', helper + '\n@router.get("", response_model=None)')
        
        # No Criar
        c = c.replace(
            'await db.manutencoes.insert_one(doc)',
            'await db.manutencoes.insert_one(doc)\n    await atualizar_estoque(doc.get("pecas_utilizadas"), -1)'
        )
        
        # No Atualizar (devolve o estoque antigo e tira o novo)
        c = c.replace(
            'await db.manutencoes.update_one({"id": id}, {"$set": doc})',
            'await atualizar_estoque(existe.get("pecas_utilizadas"), 1)\n    await db.manutencoes.update_one({"id": id}, {"$set": doc})\n    await atualizar_estoque(doc.get("pecas_utilizadas"), -1)'
        )
        
        # No Excluir (devolve o estoque)
        c = c.replace(
            'await db.manutencoes.delete_one({"id": id})',
            'manut = await db.manutencoes.find_one({"id": id})\n    if manut: await atualizar_estoque(manut.get("pecas_utilizadas"), 1)\n    await db.manutencoes.delete_one({"id": id})'
        )

    with open(router_path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend atualizado: Modelo e lógica de baixa de estoque.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar estado das peças no formulário
    if 'pecas_utilizadas' not in c:
        c = c.replace(
            'const [form, setForm] = useState(() => vazio(""));',
            'const [form, setForm] = useState(() => vazio(""));\n  const [pecasUsadas, setPecasUsadas] = useState<{ peca_id: string, quantidade: string, nome: string }[]>([]);'
        )
        # Atualizar o vazio
        c = c.replace('pecas_substituidas: "",', 'pecas_substituidas: "",\n  pecas_utilizadas: [],')

    # 2. Carregar peças no início
    if 'useQuery({ queryKey: ["pecas"]' not in c:
        c = c.replace(
            'const q = useQuery({',
            'const pecasQ = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas") });\n  const listaPecas = pecasQ.data ?? [];\n\n  const q = useQuery({'
        )

    # 3. No abrirEdicao, carregar as peças usadas
    if 'setPecasUsadas(r.pecas_utilizadas' not in c:
        # Precisamos substituir o bloco do abrirEdicao inteiro
        import re
        padrao = re.compile(r'const abrirEdicao = \(r: Manutencao\) => \{[\s\S]*?setOpen\(true\);\s*\}', re.DOTALL)
        novo_abrir = '''const abrirEdicao = (r: Manutencao) => { 
    setEditingId(r.id); 
    setForm({
      veiculo_id: r.veiculo_id, tipo: r.tipo, status: r.status, descricao: r.descricao,
      data: r.data, custo: String(r.custo), oficina: r.oficina || "", fornecedor_id: (r as any).fornecedor_id || "",
      km_manutencao: r.km_manutencao ? String(r.km_manutencao) : "", proxima_revisao_km: r.proxima_revisao_km ? String(r.proxima_revisao_km) : "",
      pecas_substituidas: r.pecas_substituidas || ""
    });
    setPecasUsadas((r as any).pecas_utilizadas || []);
    setOpen(true); 
  };'''
        c = padrao.sub(novo_abrir, c)

    # 4. No abrirNovo, limpar peças
    if 'setPecasUsadas([])' not in c:
        c = c.replace(
            'setForm(vazio(hoje)); setOpen(true);',
            'setForm(vazio(hoje)); setPecasUsadas([]); setOpen(true);'
        )

    # 5. Atualizar o salvar (mutation) para enviar peças
    if 'pecas_utilizadas: pecasUsadas' not in c:
        c = c.replace(
            'const payload = {',
            'const payload = {\n        ...form,\n        pecas_utilizadas: pecasUsadas,'
        )

    # 6. Adicionar a UI de seleção de peças no modal (antes do campo de peças substituídas)
    if 'Adicionar Peça' not in c:
        ui_pecas = '''<div className="col-span-2 border-t border-slate-800 pt-3 mt-1">
              <div className="flex justify-between items-center mb-2">
                <Label className="text-sm font-semibold text-slate-300">Peças Utilizadas (Baixa no Estoque)</Label>
                <Button type="button" variant="outline" size="sm" onClick={() => setPecasUsadas([...pecasUsadas, { peca_id: "", quantidade: "1", nome: "" }])}>
                  <Plus className="size-3 mr-1" /> Adicionar Peça
                </Button>
              </div>
              {pecasUsadas.length === 0 ? (
                <p className="text-xs text-slate-500 italic">Nenhuma peça vinculada a esta manutenção.</p>
              ) : (
                <div className="space-y-2">
                  {pecasUsadas.map((pu, idx) => (
                    <div key={idx} className="flex gap-2 items-center">
                      <FieldSelect 
                        value={pu.peca_id} 
                        onChange={(v) => {
                          const nova = [...pecasUsadas];
                          nova[idx].peca_id = v;
                          const p = listaPecas.find(x => x.id === v);
                          nova[idx].nome = p ? p.nome : "";
                          setPecasUsadas(nova);
                        }} 
                        options={listaPecas.map(p => ({ value: p.id, label: `${p.nome} (Estoque: ${p.quantidade_estoque})` }))} 
                        placeholder="Selecione a peça" 
                      />
                      <Input 
                        type="number" 
                        min="1"
                        value={pu.quantidade} 
                        onChange={(e) => {
                          const nova = [...pecasUsadas];
                          nova[idx].quantidade = e.target.value;
                          setPecasUsadas(nova);
                        }} 
                        className="w-20" 
                      />
                      <Button type="button" variant="ghost" size="icon" className="text-red-400" onClick={() => setPecasUsadas(pecasUsadas.filter((_, i) => i !== idx))}>
                        <Trash2 className="size-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="col-span-2 grid gap-1.5">
              <Label>Peças substituídas (Descrição livre)</Label>'''
        
        c = c.replace(
            '<div className="col-span-2 grid gap-1.5">\n              <Label>Peças substituídas</Label>',
            ui_pecas
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado: Interface de seleção de peças na manutenção.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)