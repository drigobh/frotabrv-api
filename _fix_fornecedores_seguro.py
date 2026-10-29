import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_FORN_SEGURO_{agora}.zip")
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

    # 1. Adiciona o estado do filtro (se não existir)
    if 'filtroTipoForn' not in c:
        c = c.replace(
            'const [filtroTipo, setFiltroTipo] = useState("__all__");',
            'const [filtroTipo, setFiltroTipo] = useState("__all__");\n  const [filtroTipoForn, setFiltroTipoForn] = useState("__all__");'
        )

    # 2. Lógica de filtragem
    if 'filtroTipoForn !== "__all__"' not in c:
        idx_return = c.find('return filtered;')
        if idx_return != -1:
            c = c[:idx_return] + '''
    if (filtroTipoForn !== "__all__") {
      filtered = filtered.filter(r => r.tipo_fornecedor_id === filtroTipoForn);
    }
    ''' + c[idx_return:]
            c = c.replace('filtroTipo, filtroStatus]', 'filtroTipo, filtroStatus, filtroTipoForn]')

    # 3. Corrige o layout dos filtros (força a linha única)
    c = c.replace('md:grid-cols-5 gap-2', 'md:grid-cols-5 gap-2')
    
    # 4. Injeta o campo no Modal (se ainda não estiver lá)
    if 'form.tipo_fornecedor_id' not in c:
        c = c.replace('nome: "", documento: ""', 'nome: "", tipo_fornecedor_id: "", documento: ""')
        c = c.replace('setForm({ nome: "",', 'setForm({ nome: "", tipo_fornecedor_id: "",')
        c = c.replace('setForm({ nome: r.nome,', 'setForm({ nome: r.nome, tipo_fornecedor_id: r.tipo_fornecedor_id || "",')

        alvo = '<div className="col-span-2 grid gap-1"><Label className="text-xs">Nome / Razão Social *</Label>'
        if alvo in c:
            novo_campo = '''<div className="col-span-2 grid gap-1">
              <Label className="text-xs">Tipo de Fornecedor *</Label>
              <FieldSelect 
                value={form.tipo_fornecedor_id || ""} 
                onChange={(v) => setForm(s => ({ ...s, tipo_fornecedor_id: v }))} 
                options={(tiposQ.data || []).filter((t: any) => t.categoria_pai_id).map((t: any) => ({ value: t.id, label: t.nome }))} 
                placeholder="Selecione o tipo..." 
              />
            </div>
            '''
            c = c.replace(alvo, novo_campo + alvo)

    # 5. Remove a função bulkUpdateTipos antiga para evitar erro de sintaxe e a recria corretamente
    import re
    c = re.sub(r'const bulkUpdateTipos = useMutation\(\{[\s\S]*?\}\);', '', c, count=1)
    
    nova_funcao = '''
  const bulkUpdateTipos = useMutation({
    mutationFn: async () => {
      const tipoAlvo = tiposQ.data?.find((t: any) => t.nome.toLowerCase().includes("combustíveis e lubrificantes"));
      if (!tipoAlvo) throw new Error("Tipo 'Combustíveis e lubrificantes' não encontrado.");
      const semTipo = rowsFiltradas.filter(r => !r.tipo_fornecedor_id);
      for (const f of semTipo) {
        await apiPut(`/fornecedores/${f.id}`, { ...f, tipo_fornecedor_id: tipoAlvo.id });
      }
      return semTipo.length;
    },
    onSuccess: (qtd) => {
      toast.success(`${qtd} fornecedores atualizados.`);
      qc.invalidateQueries({ queryKey: ["fornecedores"] });
    },
    onError: (e: any) => toast.error(e.message || "Erro ao preencher em massa.")
  });

  const preencherTiposEmMassa = () => {
    if (confirm("Isso vai preencher o tipo em TODOS os fornecedores sem tipo. Continuar?")) {
      bulkUpdateTipos.mutate();
    }
  };
'''
    
    idx = c.find('  return (')
    if idx != -1:
        c = c[:idx] + nova_funcao + c[idx:]

    # 6. Adiciona o botão no cabeçalho
    if 'Preencher Tipos em Massa' not in c:
        alvo_btn = '<Button className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Fornecedor</Button>'
        if alvo_btn in c:
            novo_btn = '''<Button variant="outline" onClick={preencherTiposEmMassa} disabled={bulkUpdateTipos.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
          <Wrench className="size-4 mr-2" /> Preencher Tipos em Massa
        </Button>
        ''' + alvo_btn
            c = c.replace(alvo_btn, novo_btn)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)