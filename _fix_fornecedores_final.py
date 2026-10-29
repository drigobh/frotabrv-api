import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORN_FINAL_{agora}.zip")
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

    # ==========================================
    # 1. QUERY E ESTADOS
    # ==========================================
    if 'queryKey: ["tipos-fornecedores"]' not in c:
        c = c.replace(
            'const fornecedoresQ = useQuery',
            'const tiposQ = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });\n  const fornecedoresQ = useQuery'
        )
        print("✅ Query de tipos adicionada.")

    if 'filtroTipoForn' not in c:
        # Adiciona o estado junto aos outros filtros
        if 'const [filtroTipo, setFiltroTipo]' in c:
            c = c.replace(
                'const [filtroTipo, setFiltroTipo] = useState("__all__");',
                'const [filtroTipo, setFiltroTipo] = useState("__all__");\n  const [filtroTipoForn, setFiltroTipoForn] = useState("__all__");'
            )
            print("✅ Estado do filtro (filtroTipoForn) adicionado.")

    # ==========================================
    # 2. LÓGICA DE FILTRAGEM
    # ==========================================
    if 'filtroTipoForn !== "__all__"' not in c:
        # Injeta a lógica no useMemo, antes do return
        idx_return = c.find('return filtered;')
        if idx_return != -1:
            logica = '''
    if (filtroTipoForn !== "__all__") {
      filtered = filtered.filter(r => r.tipo_fornecedor_id === filtroTipoForn);
    }
    '''
            c = c[:idx_return] + logica + c[idx_return:]
            # Atualiza as dependências
            if 'filtroTipo,' in c:
                c = c.replace('filtroTipo, filtroStatus]', 'filtroTipo, filtroStatus, filtroTipoForn]')
            print("✅ Lógica de filtragem por tipo adicionada.")

    # ==========================================
    # 3. CAMPO NO MODAL (FORMULÁRIO)
    # ==========================================
    if 'tipo_fornecedor_id' not in c or 'form.tipo_fornecedor_id' not in c:
        # Atualiza o estado inicial do form
        c = c.replace('nome: "", documento: ""', 'nome: "", tipo_fornecedor_id: "", documento: ""')
        
        # Atualiza o abrirNovo
        c = c.replace('setForm({ nome: "",', 'setForm({ nome: "", tipo_fornecedor_id: "",')
        
        # Atualiza o abrirEdicao
        c = c.replace(
            'setForm({ nome: r.nome,',
            'setForm({ nome: r.nome, tipo_fornecedor_id: r.tipo_fornecedor_id || "",'
        )

        # Injeta o campo visual antes do campo Nome
        alvo = '<div className="col-span-2 grid gap-1"><Label className="text-xs">Nome / Razão Social *</Label>'
        if alvo in c:
            novo_campo = '''<div className="col-span-2 grid gap-1">
              <Label className="text-xs">Tipo de Fornecedor (Opcional)</Label>
              <FieldSelect 
                value={form.tipo_fornecedor_id || ""} 
                onChange={(v) => setForm(s => ({ ...s, tipo_fornecedor_id: v }))} 
                options={(tiposQ.data || []).filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))} 
                placeholder="Selecione o tipo..." 
              />
            </div>
            '''
            c = c.replace(alvo, novo_campo + alvo)
            print("✅ Campo 'Tipo de Fornecedor' adicionado no Modal.")

    # ==========================================
    # 4. COLUNA NO GRID (HEADER E CELL)
    # ==========================================
    # Adicionar o cabeçalho (antes de Localização)
    if '<TableHead className="text-xs uppercase text-slate-500">Tipo de Fornecedor</TableHead>' not in c:
        c = c.replace(
            '<TableHead className="text-xs uppercase text-slate-500">Localização</TableHead>',
            '<TableHead className="text-xs uppercase text-slate-500">Tipo de Fornecedor</TableHead>\n              <TableHead className="text-xs uppercase text-slate-500">Localização</TableHead>'
        )
        print("✅ Coluna 'Tipo de Fornecedor' adicionada no cabeçalho do grid.")

    # Adicionar a célula (antes da célula de Localização que tem o MapPin)
    if '{tiposQ.data?.find((t: any) => t.id === r.tipo_fornecedor_id)?.nome' not in c:
        alvo_cell = '<TableCell className="text-slate-400 text-xs">\n                  <div className="flex flex-col gap-1">'
        if alvo_cell in c:
            nova_cell = '''<TableCell className="text-xs text-slate-400">
                  {tiposQ.data?.find((t: any) => t.id === r.tipo_fornecedor_id)?.nome || "—"}
                </TableCell>
                <TableCell className="text-slate-400 text-xs">
                  <div className="flex flex-col gap-1">'''
            c = c.replace(alvo_cell, nova_cell)
            # Ajusta o colSpan do grid (que era 5 e agora virou 6)
            c = c.replace('colSpan={5}', 'colSpan={6}')
            print("✅ Célula 'Tipo de Fornecedor' adicionada nas linhas do grid.")

    # ==========================================
    # 5. FILTRO NA BARRA DE PESQUISA
    # ==========================================
    if 'Todos os Tipos de Fornec.' not in c:
        alvo_filtro = '<FieldSelect value={filtroStatus}'
        if alvo_filtro in c:
            idx = c.find(alvo_filtro)
            start_div = c.rfind('<div', 0, idx)
            # O filtro atual está numa div com a classe do grid, então vamos inserir antes da div do campo Status
            novo_filtro = '''<FieldSelect 
          value={filtroTipoForn} 
          onChange={setFiltroTipoForn} 
          options={[{ value: "__all__", label: "Todos os Tipos de Fornec." }, ...(tiposQ.data || []).filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))]} 
        />
        '''
            c = c[:start_div] + novo_filtro + c[start_div:]
            print("✅ Filtro 'Tipo de Fornecedor' adicionado na barra.")

    # ==========================================
    # 6. AJUSTAR GRID DE FILTROS (que era 5 colunas, agora vai ter 6)
    # ==========================================
    c = c.replace('md:grid-cols-5 gap-2', 'md:grid-cols-6 gap-2')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)