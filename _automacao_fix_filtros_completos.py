import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Substituir a função listar para aceitar todos os parâmetros
    padrao = re.compile(r'@router\.get\("", response_model=None\)\s*async def listar\([\s\S]*?return docs', re.DOTALL)
    
    nova_listar = '''@router.get("", response_model=None)
async def listar(
    veiculo_id: str = Query(None),
    mes: str = Query(None),
    motorista_id: str = Query(None),
    posto: str = Query(None),
    produto: str = Query(None),
    origem: str = Query(None),
    _u: dict = Depends(require("read"))
):
    query = {}
    
    if veiculo_id and veiculo_id != "__all__":
        query["veiculo_id"] = veiculo_id
    if mes:
        query["data"] = {"$regex": f"^{mes}"}
    if motorista_id and motorista_id != "__all__":
        query["motorista_id"] = motorista_id
    if posto:
        query["posto"] = {"$regex": posto, "$options": "i"}
    if produto:
        query["produto"] = {"$regex": produto, "$options": "i"}
    if origem and origem != "__all__":
        query["origem"] = origem
        
    docs = await db.abastecimentos.find(query, {"_id": 0}).sort("data", -1).to_list(5000)
    return docs'''
    
    if padrao.search(c):
        c = padrao.sub(lambda m: nova_listar, c)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Filtros de Motorista, Posto, Produto e Origem adicionados.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar os estados dos filtros (caso o script anterior não tenha pegado)
    if 'const [filtroMotorista' not in c:
        c = c.replace(
            'const [mes, setMes] = useState("");',
            '''const [mes, setMes] = useState("");
  const [filtroMotorista, setFiltroMotorista] = useState(TODOS);
  const [filtroPosto, setFiltroPosto] = useState("");
  const [filtroProduto, setFiltroProduto] = useState("");
  const [filtroOrigem, setFiltroOrigem] = useState(TODOS);'''
        )

    # 2. Atualizar a URL de requisição e o QueryKey
    if 'if (filtroMotorista !== TODOS)' not in c:
        c = c.replace(
            'if (mes) params.set("mes", mes);',
            '''if (mes) params.set("mes", mes);
  if (filtroMotorista !== TODOS) params.set("motorista_id", filtroMotorista);
  if (filtroPosto) params.set("posto", filtroPosto);
  if (filtroProduto) params.set("produto", filtroProduto);
  if (filtroOrigem !== TODOS) params.set("origem", filtroOrigem);'''
        )
        c = c.replace(
            'queryKey: ["abastecimentos", filtroVeiculo, mes],',
            'queryKey: ["abastecimentos", filtroVeiculo, mes, filtroMotorista, filtroPosto, filtroProduto, filtroOrigem],'
        )

    # 3. Adicionar os campos visuais (HTML) dos filtros
    if 'placeholder="Nome do posto..."' not in c:
        c = c.replace(
            '<div className="grid gap-1.5"><Label>Mês</Label><Input type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="w-44" /></div>',
            '''<div className="grid gap-1.5"><Label>Mês</Label><Input type="month" value={mes} onChange={(e) => setMes(e.target.value)} className="w-44" /></div>
        <div className="grid w-48 gap-1.5"><Label>Motorista</Label><FieldSelect value={filtroMotorista} onChange={setFiltroMotorista} options={[{ value: TODOS, label: "Todos" }, ...(motoristas.data ?? []).map((m: any) => ({ value: m.id, label: m.nome }))]} testId="filtro-motorista" /></div>
        <div className="grid w-40 gap-1.5"><Label>Posto</Label><Input value={filtroPosto} onChange={(e) => setFiltroPosto(e.target.value)} placeholder="Nome do posto..." className="h-9" /></div>
        <div className="grid w-36 gap-1.5"><Label>Produto</Label><Input value={filtroProduto} onChange={(e) => setFiltroProduto(e.target.value)} placeholder="Ex: Diesel..." className="h-9" /></div>
        <div className="grid w-36 gap-1.5"><Label>Origem</Label><FieldSelect value={filtroOrigem} onChange={setFiltroOrigem} options={[{ value: TODOS, label: "Todas" }, { value: "manual", label: "Manual" }, { value: "bsoft", label: "BSOFT" }, { value: "edenred", label: "Edenred" }, { value: "pdf", label: "PDF" }]} testId="filtro-origem" /></div>'''
        )

    # 4. Adicionar botão de Limpar Filtros
    if 'Limpar Filtros' not in c:
        c = c.replace(
            '{(mes || filtroVeiculo !== TODOS) && <Button variant="ghost" onClick={() => { setMes(""); setFiltroVeiculo(TODOS); }}>Limpar</Button>}',
            '''{(mes || filtroVeiculo !== TODOS || filtroMotorista !== TODOS || filtroPosto || filtroProduto || filtroOrigem !== TODOS) && (
          <Button variant="ghost" onClick={() => { 
            setMes(""); setFiltroVeiculo(TODOS); setFiltroMotorista(TODOS); setFiltroPosto(""); setFiltroProduto(""); setFiltroOrigem(TODOS); 
          }} className="mb-[2px]">Limpar Filtros</Button>
        )}'''
        )

    # 5. Garantir que dataBR está sendo usado
    if '{dataBR(r.data)}' not in c:
        c = c.replace('{r.data.includes("-") ? r.data.split("-").reverse().join("/") : r.data}', '{dataBR(r.data)}')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Interface dos filtros e botão Limpar adicionados.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)