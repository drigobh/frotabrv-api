import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MANUTENCOES_UPGRADE_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    
    for arquivo in ["models/manutencoes.py", "routers/manutencoes.py", "pages/Manutencoes.tsx"]:
        caminho_abs = os.path.join(raiz, "app", "backend", arquivo.replace("/", os.sep)) if "models" in arquivo or "routers" in arquivo else os.path.join(raiz, "frontend", "src", arquivo.replace("/", os.sep))
        if os.path.exists(caminho_abs):
            with zipfile.ZipFile(caminho_zip, 'a', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(caminho_abs, arquivo)
            
    print(f"✅ Backup salvo: {caminho_zip}")

def fix_backend(raiz):
    # 1. Atualizar Model
    path_model = os.path.join(raiz, "app", "backend", "models", "manutencoes.py")
    with open(path_model, 'r', encoding='utf-8') as f:
        c = f.read()
    
    if 'data_inicio' not in c:
        c = c.replace(
            'data: str = Field(pattern=r"^\\d{4}-\\d{2}-\\d{2}$")',
            'data: str = Field(pattern=r"^\\d{4}-\\d{2}-\\d{2}$")\n    data_inicio: Optional[str] = None\n    data_fim: Optional[str] = None\n    previsao_dias: Optional[int] = None\n    autorizado_por: Optional[str] = None'
        )
        with open(path_model, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Model atualizado (novos campos).")

    # 2. Atualizar Router (Validação de Estoque)
    path_router = os.path.join(raiz, "app", "backend", "routers", "manutencoes.py")
    with open(path_router, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'Estoque insuficiente' not in c:
        # Injeta a validação dentro do criar e atualizar
        validacao = '''
    # VALIDAÇÃO DE ESTOQUE
    if body.pecas_utilizadas:
        for p in body.pecas_utilizadas:
            peca = await db.pecas.find_one({"id": p.get("peca_id")})
            if not peca:
                raise HTTPException(404, f"Peça {p.get('nome')} não encontrada.")
            qtd_solicitada = int(p.get("quantidade", 0))
            if peca.get("quantidade_atual", 0) < qtd_solicitada:
                raise HTTPException(400, f"Estoque insuficiente para {peca.get('nome')}. Disponível: {peca.get('quantidade_atual')}, Solicitado: {qtd_solicitada}")
'''
        c = c.replace(
            'doc = body.model_dump()\n    doc["id"] = str(uuid.uuid4())',
            validacao + '\n    doc = body.model_dump()\n    doc["id"] = str(uuid.uuid4())'
        )
        # Na edição, precisamos devolver o estoque antigo antes de validar o novo
        c = c.replace(
            'await atualizar_estoque(existe.get("pecas_utilizadas"), 1)\n    await db.manutencoes.update_one',
            'await atualizar_estoque(existe.get("pecas_utilizadas"), 1)\n' + validacao.replace('for p in body.pecas_utilizadas:', 'for p in body.pecas_utilizadas:\n            pass # estoque devolvido acima') + '\n    await db.manutencoes.update_one'
        )
        # Simplificando a validação para a edição (para não dar erro de lógica dupla)
        # Vamos apenas garantir que a validação esteja no criar e no atualizar de forma limpa.
        with open(path_router, 'w', encoding='utf-8') as f:
            f.write(c)
        print("✅ Router atualizado (validação de estoque).")

def fix_frontend(raiz):
    path = os.path.join(raiz, "frontend", "src", "pages", "Manutencoes.tsx")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Imports (adicionar FileDown, FileText, Filter, Calendar)
    if 'FileDown' not in c:
        c = c.replace(
            'import { AlertCircle, CheckCircle2, Clock, Info, Pencil, Plus, Trash2, UserCircle, Wrench }',
            'import { AlertCircle, CheckCircle2, Clock, Info, Pencil, Plus, Trash2, UserCircle, Wrench, FileDown, FileText, Filter }'
        )

    # 2. Estados dos Filtros
    if 'filtroData' not in c:
        c = c.replace(
            'const [filtroStatus, setFiltroStatus] = useState(TODOS);',
            'const [filtroStatus, setFiltroStatus] = useState(TODOS);\n  const [filtroData, setFiltroData] = useState("");\n  const [filtroFornecedor, setFiltroFornecedor] = useState(TODOS);\n  const [filtroPeca, setFiltroPeca] = useState(TODOS);'
        )

    # 3. Lógica de Filtragem
    if 'filtroData &&' not in c:
        c = c.replace(
            'if (filtroStatus !== TODOS) {\n      filtered = filtered.filter(r => r.status === filtroStatus);\n    }\n    return filtered;',
            '''if (filtroStatus !== TODOS) {
      filtered = filtered.filter(r => r.status === filtroStatus);
    }
    if (filtroData) {
      filtered = filtered.filter(r => (r as any).data_inicio?.startsWith(filtroData) || r.data?.startsWith(filtroData));
    }
    if (filtroFornecedor !== TODOS) {
      filtered = filtered.filter(r => (r as any).fornecedor_id === filtroFornecedor);
    }
    if (filtroPeca !== TODOS) {
      filtered = filtered.filter(r => (r as any).pecas_utilizadas?.some((p: any) => p.peca_id === filtroPeca));
    }
    return filtered;'''
        )
        c = c.replace(
            '}, [rows, filtroVeiculo, filtroStatus]);',
            '}, [rows, filtroVeiculo, filtroStatus, filtroData, filtroFornecedor, filtroPeca]);'
        )

    # 4. Estado inicial do Form (vazio)
    if 'data_inicio: hoje' not in c:
        c = c.replace(
            'data: hoje,',
            'data: hoje, data_inicio: hoje, data_fim: "", previsao_dias: "", autorizado_por: "",'
        )

    # 5. Abrir Edição (carregar novos campos)
    if 'data_inicio: (r as any).data_inicio' not in c:
        c = c.replace(
            'data: r.data, custo: String(r.custo),',
            'data: r.data, data_inicio: (r as any).data_inicio || r.data, data_fim: (r as any).data_fim || "", previsao_dias: String((r as any).previsao_dias || ""), autorizado_por: (r as any).autorizado_por || "", custo: String(r.custo),'
        )

    # 6. Funções de Exportação
    if 'const exportarPDF =' not in c:
        c = c.replace(
            'const statusColor = (status: string) => {',
            '''const exportarExcel = () => {
    const cabecalho = ["Data Início", "Veículo", "Tipo", "Descrição", "Oficina", "Custo", "Status"];
    const linhas = rowsFiltradas.map(r => [
      r.data_inicio || r.data, 
      r.veiculo_label, 
      r.tipo, 
      r.descricao, 
      r.oficina || "", 
      r.custo.toString().replace(".", ","), 
      r.status
    ]);
    const csvContent = "data:text/csv;charset=utf-8,\\uFEFF" + [cabecalho.join(";"), ...linhas.map(e => e.join(";"))].join("\\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `manutencoes_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
  };

  const exportarPDF = () => {
    window.print();
  };

  const statusColor = (status: string) => {'''
        )

    # 7. Substituir a Barra de Filtros
    if 'Filtros Avançados' not in c:
        # Procura a div dos filtros atuais
        padrao_filtros = re.compile(r'<div className="flex flex-wrap gap-3 mb-4">[\s\S]*?</div>\s*</div>')
        nova_barra = '''<div className="flex flex-wrap gap-3 mb-4 items-end">
          <div className="grid gap-1.5 w-full sm:w-auto">
            <Label>Veículo</Label>
            <FieldSelect value={filtroVeiculo} onChange={setFiltroVeiculo} options={[{ value: TODOS, label: "Todos os veículos" }, ...veicOpts]} />
          </div>
          <div className="grid gap-1.5 w-full sm:w-auto">
            <Label>Status</Label>
            <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: TODOS, label: "Todos os status" }, ...STATUS.map(s => ({ value: s, label: s }))]} />
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

    # 8. Modal: Substituir Data e Oficina
    if 'Data de Início' not in c:
        # Substituir a Data simples por Início, Fim e Previsão
        c = c.replace(
            '''<div className="grid gap-1.5">
              <Label>Data *</Label>
              <Input type="date" value={form.data} onChange={(e) => set("data")(e.target.value)} required />
            </div>''',
            '''<div className="grid gap-1.5">
              <Label>Data Início *</Label>
              <Input type="date" value={form.data_inicio} onChange={(e) => set("data_inicio")(e.target.value)} required />
            </div>
            <div className="grid gap-1.5">
              <Label>Data Término</Label>
              <Input type="date" value={form.data_fim} onChange={(e) => set("data_fim")(e.target.value)} />
            </div>
            <div className="grid gap-1.5">
              <Label>Previsão (Dias)</Label>
              <Input type="number" value={form.previsao_dias} onChange={(e) => set("previsao_dias")(e.target.value)} placeholder="Ex: 5" />
            </div>
            <div className="grid gap-1.5">
              <Label>Autorizado por</Label>
              <Input value={form.autorizado_por || me?.nome || ""} disabled className="bg-slate-800/50" />
            </div>'''
        )

        # Substituir a Oficina de texto para Select de Fornecedor
        c = c.replace(
            '''<div className="grid gap-1.5">
              <Label>Oficina / prestador</Label>
              <Input value={form.oficina} onChange={(e) => set("oficina")(e.target.value)} />
            </div>''',
            '''<div className="grid gap-1.5">
              <Label>Oficina / Prestador</Label>
              <FieldSelect 
                value={form.fornecedor_id} 
                onChange={(v) => {
                  setForm(s => ({ ...s, fornecedor_id: v, oficina: fornecedores.find((f:any)=>f.id===v)?.nome || "" }));
                }} 
                options={fornecedores.map((f: any) => ({ value: f.id, label: f.nome }))} 
                placeholder="Selecione o fornecedor" 
              />
            </div>'''
        )

    # 9. Ajustar o envio do salvar para garantir que 'data' acompanhe 'data_inicio' (compatibilidade)
    if 'data: form.data_inicio' not in c:
        c = c.replace(
            '...form,\n        pecas_utilizadas: pecasUsadas,',
            '...form,\n        data: form.data_inicio, // Compatibilidade com backend antigo\n        pecas_utilizadas: pecasUsadas,'
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado (Filtros, Exportação, Formulário e Modal).")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix_backend(raiz)
    fix_frontend(raiz)
    print("\n✅ Script aplicado com sucesso!")