import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ACOPLAMENTO_FEATURES_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    for arquivo in ["models/acoplamentos.py", "routers/acoplamentos.py"]:
        caminho_abs = os.path.join(raiz, "app", "backend", arquivo.replace("/", os.sep))
        if os.path.exists(caminho_abs):
            with zipfile.ZipFile(caminho_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(caminho_abs, f"app/backend/{arquivo}")

    caminho_front = os.path.join(raiz, "frontend", "src", "pages", "Acoplamentos.tsx")
    if os.path.exists(caminho_front):
        with zipfile.ZipFile(caminho_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_front, "frontend/src/pages/Acoplamentos.tsx")
            
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Atualizar Models (adicionar campos)
    path_model = os.path.join(raiz, "app", "backend", "models", "acoplamentos.py")
    if os.path.exists(path_model):
        with open(path_model, 'r', encoding='utf-8') as f:
            c = f.read()
        
        # Adiciona data_inicio, data_fim e updated_by ao Model base, se não existirem
        if 'data_inicio' not in c:
            c = c.replace(
                'veiculo_id: str',
                'veiculo_id: str\n    data_inicio: str | None = None\n    data_fim: str | None = None\n    updated_by: str | None = None'
            )
            # Adiciona ao Create também
            c = re.sub(r'(class AcoplamentoCreate\(BaseModel\):\s*[\s\S]*?veiculo_id: str)', r'\1\n    data_inicio: str | None = None\n    data_fim: str | None = None', c)
            
            with open(path_model, 'w', encoding='utf-8') as f:
                f.write(c)
            print("✅ Model atualizado (data_inicio, data_fim, updated_by).")

    # 2. Atualizar Router (salvar datas, adicionar PUT/DELETE, adicionar historico/{id})
    path_router = os.path.join(raiz, "app", "backend", "routers", "acoplamentos.py")
    with open(path_router, 'r', encoding='utf-8') as f:
        c = f.read()

    # Salvar datas no POST
    if 'doc["data_inicio"] = body.data_inicio' not in c:
        c = c.replace(
            '"created_by": user["nome"],',
            '"created_by": user["nome"],\n        "updated_by": user["nome"],\n        "data_inicio": body.data_inicio,\n        "data_fim": body.data_fim,'
        )

    # Adicionar rotas PUT, DELETE e GET /{id}/historico se não existirem
    if '@router.put("/{id}")' not in c:
        novas_rotas = '''
@router.put("/{id}", response_model=Acoplamento)
async def atualizar(id: str, body: AcoplamentoCreate, request: Request, user: dict = Depends(require("write"))):
    v_label, c_label, m_label = await _get_labels(body.veiculo_id, body.carreta_id, body.motorista_id)
    update_data = {
        "veiculo_id": body.veiculo_id, "veiculo_label": v_label,
        "carreta_id": body.carreta_id, "carreta_label": c_label,
        "motorista_id": body.motorista_id, "motorista_label": m_label,
        "data_inicio": body.data_inicio, "data_fim": body.data_fim,
        "completo": bool(body.carreta_id and body.motorista_id),
        "updated_at": now_iso(), "updated_by": user["nome"]
    }
    await db.acoplamentos.update_one({"id": id}, {"$set": update_data})
    await audit(user, "atualizar", "acoplamentos", id, f"Veículo: {v_label}", request)
    doc = await db.acoplamentos.find_one({"id": id})
    return Acoplamento(**doc)

@router.delete("/{id}")
async def excluir(id: str, request: Request, user: dict = Depends(require("write"))):
    await db.acoplamentos.update_one({"id": id}, {"$set": {"status": "inativo", "updated_at": now_iso(), "updated_by": user["nome"]}})
    await audit(user, "excluir", "acoplamentos", id, "Desacoplamento", request)
    return {"ok": True}

@router.get("/{id}/historico", response_model=list[HistoricoItem])
async def historico_item(id: str, _u: dict = Depends(require("read"))):
    docs = await db.acoplamentos_historico.find({"acoplamento_id": id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return [HistoricoItem(**d) for d in docs]
'''
        c += novas_rotas

    with open(path_router, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Router atualizado (salva datas, PUT, DELETE, historico).")

def fix_frontend(raiz):
    path_front = os.path.join(raiz, "frontend", "src", "pages", "Acoplamentos.tsx")
    with open(path_front, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar imports necessários (History, Clock)
    if 'History' not in c.split('lucide-react')[0]:
        c = c.replace('import { Link2, Plus, Pencil, Trash2 }', 'import { Link2, Plus, Pencil, Trash2, History, Clock, User }')

    # 2. Adicionar estado para o modal de histórico e buscar usuário logado
    if 'const [historicoId, setHistoricoId] = useState<string | null>(null);' not in c:
        c = c.replace(
            'const [excluirId, setExcluirId] = useState<string | null>(null);',
            'const [excluirId, setExcluirId] = useState<string | null>(null);\n  const [historicoId, setHistoricoId] = useState<string | null>(null);\n  const { data: authUser } = useQuery({ queryKey: ["me"], queryFn: () => apiGet<any>("/auth/me") });'
        )

    # 3. Adicionar query do histórico
    if 'queryKey: ["acoplamento-historico"' not in c:
        c = c.replace(
            'const q = useQuery({ queryKey: ["acoplamentos"], queryFn: () => apiGet<any[]>("/acoplamentos") });',
            'const q = useQuery({ queryKey: ["acoplamentos"], queryFn: () => apiGet<any[]>("/acoplamentos") });\n  const histQuery = useQuery({ queryKey: ["acoplamento-historico", historicoId], queryFn: () => apiGet<any[]>(`/acoplamentos/${historicoId}/historico`), enabled: !!historicoId });'
        )

    # 4. Cabeçalho: Adicionar coluna Usuário e trocar Ações
    if '>Usuário</TableHead>' not in c:
        c = c.replace(
            '<TableHead>Início</TableHead>',
            '<TableHead>Início</TableHead>\n                      <TableHead>Usuário</TableHead>'
        )

    # 5. Corpo da tabela: Adicionar célula do usuário e botão de histórico
    if '{r.updated_by || r.created_by}' not in c:
        c = c.replace(
            '<TableCell>{r.data_inicio}</TableCell>',
            '<TableCell>{r.data_inicio ? new Date(r.data_inicio).toLocaleDateString("pt-BR", {timeZone: "UTC"}) : "—"}</TableCell>\n                <TableCell className="text-xs text-slate-400">{r.updated_by || r.created_by || "—"}</TableCell>'
        )
        
    if '<History className="size-4 text-amber-400" />' not in c:
        c = c.replace(
            '<Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>',
            '<Button size="icon-sm" variant="ghost" onClick={() => setHistoricoId(r.id)} title="Histórico"><History className="size-4 text-amber-400" /></Button>\n                  <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'
        )

    # 6. Modal de Cadastro: Mostrar usuário logado
    if 'Usuário Logado:' not in c:
        c = c.replace(
            '<Input type="date" value={form.data_inicio}',
            '<div className="flex items-center gap-2 p-2 rounded-md bg-slate-800/50 border border-slate-700/50 text-sm text-slate-300">\n              <User className="size-4 text-sky-400" />\n              <span>Usuário Logado: <strong>{authUser?.nome || "Carregando..."}</strong></span>\n            </div>\n            <div className="grid grid-cols-2 gap-3">\n            <Input type="date" value={form.data_inicio}'
        )
        c = c.replace(
            '<DialogFooter><Button type="submit">Salvar</Button></DialogFooter>',
            '</div>\n            <DialogFooter><Button type="submit">Salvar</Button></DialogFooter>'
        )

    # 7. Adicionar o Modal de Histórico no final do componente
    if '<Dialog open={!!historicoId}' not in c:
        modal_hist = '''
      {/* Modal de Histórico */}
      <Dialog open={!!historicoId} onOpenChange={(o) => !o && setHistoricoId(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Histórico de Movimentações</DialogTitle></DialogHeader>
          <div className="max-h-[60vh] overflow-y-auto space-y-4 pr-2 mt-2">
            {histQuery.isLoading ? (
              <p className="text-sm text-slate-400 text-center py-4">Carregando histórico...</p>
            ) : histQuery.data?.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-4">Nenhuma movimentação registrada.</p>
            ) : (
              histQuery.data?.map((h: any) => (
                <div key={h.id} className="flex gap-3 text-sm">
                  <div className="mt-0.5"><Clock className="size-4 text-amber-400" /></div>
                  <div>
                    <p className="font-semibold text-slate-200">{h.evento}</p>
                    <p className="text-slate-400 text-xs">{h.descricao}</p>
                    <p className="text-slate-500 text-[10px] mt-1">{new Date(h.created_at).toLocaleString("pt-BR")}</p>
                  </div>
                </div>
              ))
            )}
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setHistoricoId(null)}>Fechar</Button></DialogFooter>
        </DialogContent>
      </Dialog>
'''
        c = c.replace('    </div>\n  );\n}', modal_hist + '    </div>\n  );\n}')

    with open(path_front, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado (Usuário, Botão Histórico, Modal e Datas).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso! Reinicie o Vite e o Backend.")