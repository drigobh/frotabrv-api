import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORN_LAYOUT_SEED_{agora}.zip")
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
    # 1. CORRIGIR O LAYOUT DOS FILTROS (1 linha)
    # ==========================================
    # Deixa o grid com 5 colunas iguais e coloca todos os campos dentro
    c = c.replace('md:grid-cols-6 gap-2', 'md:grid-cols-5 gap-2')
    
    # Remove o FieldSelect que estava fora do grid (o que causou a quebra visual)
    # e junta tudo num grid de 5 colunas com tamanhos iguais
    import re
    padrao_filtros = re.compile(r'<div className="mb-4 grid grid-cols-1 md:grid-cols-5 gap-2">[\s\S]*?</div>')
    
    novo_filtros = '''<div className="mb-4 grid grid-cols-1 md:grid-cols-5 gap-2">
        <Input placeholder="Buscar por Nome ou Documento..." value={filtroNome} onChange={(e) => setFiltroNome(e.target.value)} className="h-9" />
        <Input placeholder="Cidade..." value={filtroCidade} onChange={(e) => setFiltroCidade(e.target.value)} className="h-9" />
        <FieldSelect value={filtroTipo} onChange={setFiltroTipo} options={[{ value: "__all__", label: "PJ e PF" }, { value: "PJ", label: "Apenas PJ" }, { value: "PF", label: "Apenas PF" }]} />
        <FieldSelect value={filtroStatus} onChange={setFiltroStatus} options={[{ value: "__all__", label: "Todos os Status" }, { value: "ativo", label: "Apenas Ativos" }, { value: "inativo", label: "Apenas Inativos" }]} />
        <FieldSelect value={filtroTipoForn} onChange={setFiltroTipoForn} options={[{ value: "__all__", label: "Todos os Tipos" }, ...(tiposQ.data || []).filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))]} />
      </div>'''
    
    if padrao_filtros.search(c):
        c = padrao_filtros.sub(novo_filtros, c, count=1)
        print("✅ Filtros compactados em 1 linha.")

    # ==========================================
    # 2. TORNAR O CAMPO OBRIGATÓRIO NO FRONTEND
    # ==========================================
    # Adiciona o asterisco no Label
    c = c.replace(
        '<Label className="text-xs">Tipo de Fornecedor (Opcional)</Label>',
        '<Label className="text-xs">Tipo de Fornecedor *</Label>'
    )
    
    # Desabilita o botão de salvar se não tiver o tipo selecionado
    c = c.replace(
        'disabled={salvar.isPending || !form.nome || !form.documento}',
        'disabled={salvar.isPending || !form.nome || !form.documento || !form.tipo_fornecedor_id}'
    )
    print("✅ Campo 'Tipo de Fornecedor' agora é obrigatório.")

    # ==========================================
    # 3. BOTÃO "INJETAR TIPO EM MASSA"
    # ==========================================
    if 'preencherTiposEmMassa' not in c:
        # Adiciona a função de injeção em massa (procura o fornecedor que tem o tipo "Combustíveis e lubrificantes")
        funcao_massa = '''
  const bulkUpdateTipos = useMutation({
    mutationFn: async () => {
      // Acha o ID do tipo "Combustíveis e lubrificantes"
      const tipoAlvo = tiposQ.data?.find((t: any) => t.nome.toLowerCase().includes("combustíveis e lubrificantes"));
      if (!tipoAlvo) {
        throw new Error("Tipo 'Combustíveis e lubrificantes' não encontrado.");
      }

      // Pega todos os fornecedores que estão sem tipo
      const semTipo = rowsFiltradas.filter(r => !r.tipo_fornecedor_id);
      
      for (const f of semTipo) {
        // Atualiza um por um
        await apiPut(`/fornecedores/${f.id}`, { ...f, tipo_fornecedor_id: tipoAlvo.id });
      }
      return semTipo.length;
    },
    onSuccess: (qtd) => {
      toast.success(`${qtd} fornecedores atualizados com o tipo "Combustíveis e lubrificantes".`);
      qc.invalidateQueries({ queryKey: ["fornecedores"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao preencher em massa.")
  });

  const preencherTiposEmMassa = () => {
    if (confirm("Isso vai preencher o tipo 'Combustíveis e lubrificantes' em TODOS os fornecedores que estão SEM tipo. Deseja continuar?")) {
      bulkUpdateTipos.mutate();
    }
  };
'''
        # Insere a função antes do return principal
        idx = c.find('  return (')
        if idx != -1:
            c = c[:idx] + funcao_massa + c[idx:]
            print("✅ Função de injeção em massa adicionada.")

    # Adiciona o botão no header (ao lado do "Novo Fornecedor")
    if 'Preencher Tipos em Massa' not in c:
        alvo_btn = '<Button className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Fornecedor</Button>'
        if alvo_btn in c:
            novo_btn = '''<Button variant="outline" onClick={preencherTiposEmMassa} disabled={bulkUpdateTipos.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
          <Wrench className="size-4 mr-2" /> {bulkUpdateTipos.isPending ? "Processando..." : "Preencher Tipos em Massa"}
        </Button>
        \n        ''' + alvo_btn
            c = c.replace(alvo_btn, novo_btn)
            
            # Garante import do ícone Wrench
            if 'Wrench' not in c.split('lucide-react')[0]:
                c = c.replace('import { AlertTriangle,', 'import { AlertTriangle, Wrench,')
            print("✅ Botão 'Preencher Tipos em Massa' adicionado no Header.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)