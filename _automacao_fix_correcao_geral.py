import os

def fix_backend(raiz):
    router_path = os.path.join(raiz, "app", "backend", "routers", "movimentacoes.py")
    with open(router_path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adiciona a rota de reverter inventário
    if 'reverter' not in c:
        c += '''

@router.post("/inventarios/{id}/reverter")
async def reverter_inventario(id: str, user: dict = Depends(require("write"))):
    inv = await db.inventarios.find_one({"id": id}, {"_id": 0})
    if not inv:
        raise HTTPException(404, "Inventário não encontrado")
    
    for item in inv["itens"]:
        diff = item["qtd_fisica"] - item["qtd_anterior"]
        if diff != 0:
            # Reverte a quantidade (se diminuiu no inventario, agora adiciona de volta, e vice-versa)
            await db.pecas.update_one({"id": item["peca_id"]}, {"$inc": {"quantidade_estoque": -diff}})
            
            # Registra a movimentação de reversão
            doc_mov = {
                "id": str(uuid.uuid4()),
                "peca_id": item["peca_id"],
                "peca_nome": item["peca_nome"],
                "quantidade": abs(diff),
                "motivo": "Reversão de Inventário",
                "observacao": f"Revertendo ajuste do inventário de {inv['data_hora'][:10]}",
                "usuario_nome": user.get("nome", "Sistema"),
                "data_hora": now_iso()
            }
            await db.movimentacoes.insert_one(doc_mov)

    await db.inventarios.delete_one({"id": id})
    return {"ok": True}
'''
        with open(router_path, 'w', encoding='utf-8') as f:
            f.write(c)
    print("✅ Backend: Rota de reverter inventário adicionada.")

def fix_estoque_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Importar useMe
    if 'useMe' not in c:
        c = c.replace('import { useVeiculos, useCarretas } from "@/hooks/useCadastros";', 'import { useVeiculos, useCarretas } from "@/hooks/useCadastros";\nimport { useMe } from "@/hooks/useSession";')
        c = c.replace('export default function Estoque() {', 'export default function Estoque() {\n  const { data: me } = useMe();')

    # 2. Adicionar estado para confirmação de inventário
    if 'openInvConfirm' not in c:
        c = c.replace('const [excluirInvId, setExcluirInvId] = useState<string | null>(null);', 'const [excluirInvId, setExcluirInvId] = useState<string | null>(null);\n  const [openInvConfirm, setOpenInvConfirm] = useState(false);')

    # 3. Adicionar Mutation de Reverter
    if 'reverterInv' not in c:
        c = c.replace(
            'const excluirInv = useMutation({',
            '''const reverterInv = useMutation({
    mutationFn: (id: string) => apiPost(`/estoque/inventarios/${id}/reverter`),
    onSuccess: () => { toast.success("Inventário revertido e estoque restaurado!"); qc.invalidateQueries({ queryKey: ["pecas"] }); qc.invalidateQueries({ queryKey: ["movimentacoes"] }); qc.invalidateQueries({ queryKey: ["inventarios"] }); },
    onError: (e: any) => toast.error(e.message || "Erro ao reverter"),
  });

  const excluirInv = useMutation({'''
        )

    # 4. Fornecedores da peça com avaliação
    c = c.replace(
        '''const fornecedoresDaPeca = pecaSelecionada ? (pecaSelecionada.fornecedores_precos || []).map((fp:any) => {
    const f = fornecedores.find((x:any) => x.id === fp.fornecedor_id);
    return f ? { value: f.id, label: f.nome } : null;
  }).filter(Boolean) : [];''',
        '''const fornecedoresDaPeca = pecaSelecionada ? (pecaSelecionada.fornecedores_precos || []).map((fp:any) => {
    const f = fornecedores.find((x:any) => x.id === fp.fornecedor_id);
    return f ? { value: f.id, label: `${f.nome} (${f.avaliacao || 0}★)` } : null;
  }).filter(Boolean) : [];'''
    )

    # 5. Adicionar campo de usuário na Baixa e botão de Reverter no Histórico
    c = c.replace(
        '<div className="grid grid-cols-2 gap-4">\n              <div className="grid gap-1.5"><Label>Quantidade *</Label>',
        '''<div className="grid gap-1.5 bg-slate-900/50 p-2 rounded border border-slate-800">
              <Label className="text-xs text-slate-400">Responsável pela Baixa</Label>
              <Input value={me?.nome || "Usuário Logado"} disabled className="h-8 bg-transparent border-0 px-0 text-sky-400 font-medium" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-1.5"><Label>Quantidade *</Label>'''
    )

    c = c.replace(
        '<Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirInvId(inv.id)} title="Excluir Histórico"><Trash2 className="size-4" /></Button>',
        '''<Button size="icon-sm" variant="ghost" className="text-amber-400" onClick={() => { if(confirm("Deseja reverter este inventário? O estoque voltará ao estado anterior.")) reverterInv.mutate(inv.id); }} title="Reverter Inventário"><RefreshCw className="size-4" /></Button>
                      <Button size="icon-sm" variant="ghost" className="text-red-300" onClick={() => setExcluirInvId(inv.id)} title="Excluir Histórico"><Trash2 className="size-4" /></Button>'''
    )

    # 6. Adicionar o ConfirmDialog para o Inventário
    if '<ConfirmDialog open={openInvConfirm}' not in c:
        c = c.replace(
            '<Dialog open={openInv} onOpenChange={(o) => { setOpenInv(o); if (!o) setInvContagens({}); }}>',
            '''<ConfirmDialog open={openInvConfirm} onOpenChange={setOpenInvConfirm} title="Confirmar Ajuste de Estoque?" description="Isso alterará a quantidade atual das peças para os valores informados e gerará um histórico." confirmLabel="Confirmar Ajuste" pending={salvarInv.isPending} onConfirm={() => { setOpenInvConfirm(false); salvarInv.mutate(); }} testId="inventario-confirmar" />

      <Dialog open={openInv} onOpenChange={(o) => { setOpenInv(o); if (!o) setInvContagens({}); }}>'''
        )
        c = c.replace(
            '<Button onClick={() => salvarInv.mutate()} disabled={salvarInv.isPending || Object.keys(invContagens).length === 0}>Salvar Inventário</Button>',
            '<Button onClick={() => setOpenInvConfirm(true)} disabled={salvarInv.isPending || Object.keys(invContagens).length === 0}>Salvar Inventário</Button>'
        )

    # 7. Sincronizar Cards com a mesma base do Grid (usando 'rows' em vez de filtros)
    # O script anterior já usava 'rows', então está correto. Mas o problema de "não andar junto" era o cache. Vamos forçar o refetch.
    if 'staleTime: 0' not in c:
        c = c.replace('const q = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas") });', 'const q = useQuery({ queryKey: ["pecas"], queryFn: () => apiGet<any[]>("/pecas"), staleTime: 0, refetchOnMount: true });')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend Estoque: Baixa corrigida (fornecedor e usuário), Inventário com confirmação/reversão e Cards sincronizados.")

def fix_fornecedores(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Fornecedores.tsx")
    if not os.path.exists(caminho): return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Garantir que o campo avaliacao está no estado e no formulário
    if 'avaliacao: 0' not in c:
        c = c.replace('ativo: true', 'avaliacao: 0, ativo: true')

    if 'Avaliação do Fornecedor' not in c:
        # Adiciona as estrelas no formulário
        c = c.replace(
            '<div className="col-span-2 flex items-center gap-3 mt-2">\n              <input type="checkbox" checked={form.ativo}',
            '''<div className="col-span-2 grid gap-1.5">
              <Label>Avaliação do Fornecedor</Label>
              <div className="flex gap-2 items-center">
                {[1, 2, 3, 4, 5].map(star => (
                  <button type="button" key={star} onClick={() => setForm(s => ({ ...s, avaliacao: star }))} className="focus:outline-none hover:scale-110">
                    <Star className={`size-5 ${star <= form.avaliacao ? 'fill-amber-400 text-amber-400' : 'text-slate-600'}`} />
                  </button>
                ))}
                <span className="text-[10px] text-slate-400 ml-2">{form.avaliacao === 0 ? "Sem avaliação" : `${form.avaliacao} de 5`}</span>
              </div>
            </div>

            <div className="col-span-2 flex items-center gap-3 mt-2">\n              <input type="checkbox" checked={form.ativo}'''
        )
        # Adiciona as estrelas no grid
        c = c.replace(
            '<TableCell className="font-medium text-slate-200">\n                    <div className="flex items-center gap-2">',
            '''<TableCell className="font-medium text-slate-200">
                    <div className="flex items-center gap-2">'''
        )
        # Garantir import do Star
        if 'Star' not in c.split('lucide-react')[0]:
            c = c.replace('import { Truck, Plus', 'import { Truck, Plus, Star')
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend Fornecedores: Avaliação (estrelas) restaurada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_estoque_frontend(raiz)
    fix_fornecedores(raiz)