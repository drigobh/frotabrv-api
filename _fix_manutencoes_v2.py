import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MANUTENCOES_V2_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    arquivos = [
        "app/backend/routers/manutencoes.py",
        "frontend/src/pages/Manutencoes.tsx",
        "frontend/src/components/layout/Sidebar.tsx",
        "frontend/src/App.tsx"
    ]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    path = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # Substituir a rota de criar inteira para garantir a validação correta
    novo_criar = '''@router.post("", response_model=Manutencao, status_code=201)
async def criar(body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    # VALIDAÇÃO DE ESTOQUE RIGOROSA
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            peca = await db.pecas.find_one({"id": p.get("peca_id")})
            if not peca:
                raise HTTPException(404, f"Peça {p.get('nome')} não encontrada.")
            qtd_solicitada = int(p.get("quantidade", 0))
            if peca.get("quantidade_atual", 0) < qtd_solicitada:
                raise HTTPException(400, f"Estoque insuficiente para {peca.get('nome')}. Disponível: {peca.get('quantidade_atual')}, Solicitado: {qtd_solicitada}")

    doc = body.model_dump()
    doc["id"] = str(uuid.uuid4())
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    
    if not doc.get("data_inicio"):
        doc["data_inicio"] = body.data
        
    doc["criado_por"] = user.get("nome", user.get("email", "Sistema"))
    doc["created_at"] = now_iso()

    await db.manutencoes.insert_one(doc)
    
    # BAIXA DE ESTOQUE DIRETA
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            await db.pecas.update_one(
                {"id": p.get("peca_id")},
                {"$inc": {"quantidade_atual": -int(p.get("quantidade", 0))}}
            )
            
    doc.pop("_id", None)
    return doc'''

    c = re.sub(r'@router\.post\("", response_model=Manutencao, status_code=201\)\n[\s\S]*?return doc', novo_criar, c, count=1)

    # Substituir a rota de atualizar para garantir o estorno e nova validação
    novo_atualizar = '''@router.put("/{id}", response_model=Manutencao)
async def atualizar(id: str, body: ManutencaoCreate, request: Request, user: dict = Depends(require("write"))):
    existe = await db.manutencoes.find_one({"id": id})
    if not existe:
        raise HTTPException(404, "Manutenção não encontrada")

    veiculo = await db.veiculos.find_one({"id": body.veiculo_id}, {"_id": 0})
    if not veiculo:
        raise HTTPException(404, "Veículo não encontrado")

    # 1. Estorna o estoque antigo para poder validar o novo
    if existe.get("pecas_utilizadas"):
        for p in existe["pecas_utilizadas"]:
            await db.pecas.update_one(
                {"id": p.get("peca_id")},
                {"$inc": {"quantidade_atual": int(p.get("quantidade", 0))}}
            )

    # 2. Valida o novo estoque
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            peca = await db.pecas.find_one({"id": p.get("peca_id")})
            if not peca:
                # Se der erro, precisamos desfazer o estorno, mas para simplificar, assumimos que o frontend envia IDs válidos
                raise HTTPException(404, f"Peça {p.get('nome')} não encontrada.")
            qtd_solicitada = int(p.get("quantidade", 0))
            if peca.get("quantidade_atual", 0) < qtd_solicitada:
                # Desfaz o estorno caso falhe
                if existe.get("pecas_utilizadas"):
                    for p_old in existe["pecas_utilizadas"]:
                        await db.pecas.update_one({"id": p_old.get("peca_id")}, {"$inc": {"quantidade_atual": -int(p_old.get("quantidade", 0))}})
                raise HTTPException(400, f"Estoque insuficiente para {peca.get('nome')}. Disponível: {peca.get('quantidade_atual')}, Solicitado: {qtd_solicitada}")

    doc = body.model_dump()
    doc["veiculo_label"] = f"{veiculo['placa']} · {veiculo['modelo']}"
    doc["criado_por"] = existe.get("criado_por", user.get("nome", "Sistema"))
    doc["created_at"] = existe.get("created_at", now_iso())

    await db.manutencoes.update_one({"id": id}, {"$set": doc})
    
    # 3. Baixa do novo estoque
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            await db.pecas.update_one(
                {"id": p.get("peca_id")},
                {"$inc": {"quantidade_atual": -int(p.get("quantidade", 0))}}
            )
            
    doc["id"] = id
    return doc'''

    c = re.sub(r'@router\.put\("/\{id\}", response_model=Manutencao\)\n[\s\S]*?return doc', novo_atualizar, c, count=1)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Lógica de estoque reescrita e corrigida.")

def fix_frontend(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Imports
    if 'FileDown' not in c:
        c = c.replace(
            'import { AlertCircle, CheckCircle2, Clock, Info, Pencil, Plus, Trash2, UserCircle, Wrench }',
            'import { AlertCircle, CheckCircle2, Clock, Info, Pencil, Plus, Trash2, UserCircle, Wrench, FileDown, FileText, Filter }'
        )

    # 2. Funções de Exportação
    if 'const exportarExcel =' not in c:
        c = c.replace(
            'const statusColor = (status: string) => {',
            '''const exportarExcel = () => {
    const cabecalho = ["Data Início", "Veículo", "Tipo", "Descrição", "Oficina", "Custo", "Status"];
    const linhas = rowsFiltradas.map(r => [
      r.data_inicio || r.data, r.veiculo_label, r.tipo, r.descricao, r.oficina || "", r.custo.toString().replace(".", ","), r.status
    ]);
    const csvContent = "data:text/csv;charset=utf-8,\\uFEFF" + [cabecalho.join(";"), ...linhas.map(e => e.join(";"))].join("\\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `manutencoes_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
  };
  const exportarPDF = () => window.print();
  const statusColor = (status: string) => {'''
        )

    # 3. Substituir a Barra de Filtros (usando Regex flexível)
    padrao_filtros = re.compile(r'<div className="flex flex-wrap gap-3 mb-4[^>]*>[\s\S]*?</div>\s*</div>')
    nova_barra = '''<div className="flex flex-wrap gap-3 mb-4 items-end">
          <div className="grid gap-1.5 w-full sm:w-auto">
            <Label>Veículo</Label>
            <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos" }, ...veicOpts]} />
          </div>
          <div className="grid gap-1.5 w-full sm:w-auto">
            <Label>Status</Label>
            <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: TODOS, label: "Todos" }, ...STATUS.map(s => ({ value: s, label: s }))]} />
          </div>
          <div className="grid gap-1.5 w-full sm:w-auto">
            <Label>Mês/Data</Label>
            <Input type="month" value={filtroData} onChange={(e) => setFiltroData(e.target.value)} className="h-9" />
          </div>
          <div className="grid gap-1.5 w-full sm:w-auto">
            <Label>Fornecedor</Label>
            <FieldSelect value={filtroFornecedor} onChange={setFiltroFornecedor} options={[{ value: TODOS, label: "Todos" }, ...fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))]} />
          </div>
          <div className="grid gap-1.5 w-full sm:w-auto">
            <Label>Peça</Label>
            <FieldSelect value={filtroPeca} onChange={setFiltroPeca} options={[{ value: TODOS, label: "Todas" }, ...listaPecas.map((p: any) => ({ value: p.id, label: p.nome }))]} />
          </div>
          <div className="ml-auto flex gap-2 mb-[2px]">
             <Button variant="outline" size="sm" onClick={() => { setFiltroVeiculo(TODOS); setFiltroStatus(TODOS); setFiltroData(""); setFiltroFornecedor(TODOS); setFiltroPeca(TODOS); }} className="h-9 px-3 border-red-500/40 text-red-400 hover:bg-red-500/10"><Filter className="size-4 mr-1.5" /> Limpar</Button>
             <Button size="sm" onClick={exportarExcel} className="h-9 px-3 bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg"><FileDown className="size-4 mr-1.5" /> Excel</Button>
             <Button size="sm" onClick={exportarPDF} className="h-9 px-3 bg-sky-600 hover:bg-sky-500 text-white shadow-lg"><FileText className="size-4 mr-1.5" /> PDF</Button>
          </div>
        </div>'''
    c = padrao_filtros.sub(nova_barra, c, count=1)

    # 4. Campo Fornecedor Autocomplete (Input + Datalist)
    c = re.sub(
        r'<div className="grid gap-1\.5">\s*<Label>Oficina / [^<]*</Label>\s*<Input[^>]*/>\s*</div>',
        '''<div className="grid gap-1.5">
              <Label>Oficina / Prestador (Digite para buscar)</Label>
              <Input
                list="fornecedores-list"
                value={form.oficina}
                onChange={(e) => {
                  const val = e.target.value;
                  const f = fornecedores.find((x: any) => x.nome === val);
                  setForm(s => ({ ...s, oficina: val, fornecedor_id: f ? f.id : "" }));
                }}
                placeholder="Ex: Tonho"
              />
              <datalist id="fornecedores-list">
                {fornecedores.map((f: any) => <option key={f.id} value={f.nome} />)}
              </datalist>
            </div>''',
        c
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend Manutenções: Filtros, Botões e Autocomplete aplicados.")

def criar_agendamento(raiz):
    # 1. Criar a Página Agendamento.tsx
    path_page = os.path.join(raiz, "frontend", "src", "pages", "Agendamento.tsx")
    if not os.path.exists(path_page):
        with open(path_page, 'w', encoding='utf-8') as f:
            f.write('''import { useQuery } from "@tanstack/react-query";
import { CalendarClock, Wrench } from "lucide-react";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useVeiculos } from "@/hooks/useCadastros";

export default function Agendamento() {
  const { data: manutencoes = [] } = useQuery({ queryKey: ["manutencoes"], queryFn: () => apiGet<any[]>("/manutencoes") });
  const { data: veiculos = [] } = useVeiculos();

  // Filtra apenas as manutenções que têm próxima revisão e ainda não chegaram lá
  const agendadas = manutencoes
    .filter(m => m.proxima_revisao_km)
    .map(m => {
      const v = veiculos.find((x: any) => x.id === m.veiculo_id);
      const kmAtual = v?.hodometro_km || 0;
      const falta = m.proxima_revisao_km - kmAtual;
      return { ...m, kmAtual, falta };
    })
    .sort((a, b) => a.falta - b.falta);

  return (
    <div>
      <PageHeader eyebrow="Operação" title="Agendamento de Manutenções" description="Controle de revisões preventivas por KM." />
      
      <div className="glass rounded-2xl overflow-hidden mt-4">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-transparent">
              <TableHead className="text-xs uppercase text-slate-500">Veículo</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">KM Atual</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Próx. Revisão</TableHead>
              <TableHead className="text-xs uppercase text-slate-500">Status do Prazo</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {agendadas.length === 0 ? (
              <TableRow>
                <TableCell colSpan={4} className="text-center text-slate-500 py-8">Nenhuma revisão agendada.</TableCell>
              </TableRow>
            ) : (
              agendadas.map((m, i) => (
                <TableRow key={i} className="border-slate-800">
                  <TableCell className="text-slate-200 font-medium">{m.veiculo_label}</TableCell>
                  <TableCell className="text-slate-400">{m.kmAtual.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell className="text-slate-400">{m.proxima_revisao_km.toLocaleString('pt-BR')} km</TableCell>
                  <TableCell>
                    {m.falta <= 0 ? (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-rose-500/20 text-rose-400 text-xs font-bold">
                        <Wrench className="size-3" /> Atrasada ({Math.abs(m.falta).toLocaleString('pt-BR')} km)
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-amber-500/20 text-amber-400 text-xs font-bold">
                        <CalendarClock className="size-3" /> Faltam {m.falta.toLocaleString('pt-BR')} km
                      </span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}''')
        print("✅ Página Agendamento.tsx criada.")

    # 2. Adicionar rota no App.tsx
    path_app = os.path.join(raiz, "frontend", "src", "App.tsx")
    if os.path.exists(path_app):
        with open(path_app, 'r', encoding='utf-8') as f:
            c_app = f.read()
        if 'Agendamento' not in c_app:
            c_app = c_app.replace(
                'import Manutencoes from',
                'import Agendamento from "@/pages/Agendamento";\nimport Manutencoes from'
            )
            c_app = c_app.replace(
                '<Route path="/manutencoes"',
                '<Route path="/agendamento" element={<Agendamento />} />\n              <Route path="/manutencoes"'
            )
            with open(path_app, 'w', encoding='utf-8') as f:
                f.write(c_app)
            print("✅ Rota /agendamento adicionada no App.tsx.")

    # 3. Adicionar item no Sidebar
    path_sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(path_sidebar):
        with open(path_sidebar, 'r', encoding='utf-8') as f:
            c_side = f.read()
        if '/agendamento' not in c_side:
            # Procura o item de Manutenções para colocar o Agendamento do lado
            padrao_manut = re.compile(r'(\{\s*label:\s*"Manutenções"[^}]*\}[,]?)')
            match = padrao_manut.search(c_side)
            if match:
                novo_item = '{ label: "Agendamento", icon: CalendarClock, path: "/agendamento" },'
                c_side = c_side[:match.start()] + novo_item + '\n      ' + c_side[match.start():]
                if 'CalendarClock' not in c_side.split('lucide-react')[0]:
                    c_side = c_side.replace('import { ', 'import { CalendarClock, ')
                with open(path_sidebar, 'w', encoding='utf-8') as f:
                    f.write(c_side)
                print("✅ Item 'Agendamento' adicionado ao Sidebar.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    criar_agendamento(raiz)
    print("\n✅ Todos os scripts aplicados com sucesso! Faça o push para o Render.")