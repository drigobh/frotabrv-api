import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_SEED_FRONTEND_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "TiposFornecedores.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/TiposFornecedores.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "TiposFornecedores.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar o botão "Popular Lista" no cabeçalho (se não existir)
    if 'Popular Lista' not in c:
        c = c.replace(
            'actions={<Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Tipo</Button>}',
            '''actions={<div className="flex gap-2">
          <Button variant="outline" onClick={popularLista} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10">
            <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Lista Base"}
          </Button>
          <Button onClick={abrirNovo} className="bg-sky-600 hover:bg-sky-500"><Plus className="size-4 mr-2" /> Novo Tipo</Button>
        </div>}'''
        )
        print("✅ Botão 'Popular Lista' adicionado.")

    # 2. Importar o ícone Database
    if 'Database' not in c.split('lucide-react')[0]:
        c = c.replace(
            'import { FolderTree, Plus, Pencil, Trash2, Tag }',
            'import { FolderTree, Plus, Pencil, Trash2, Tag, Database }'
        )
        print("✅ Import do ícone Database adicionado.")

    # 3. Adicionar a função popularLista e o seed Mutation
    if 'const popularLista =' not in c:
        # Encontra o ponto após a definição do excluir
        idx = c.find('const abrirNovo =')
        if idx == -1:
            idx = c.find('  return (')
        
        seed_code = '''
  const seed = useMutation({
    mutationFn: async () => {
      const dados = [
        { nome: "1. Insumos Operacionais e Manutenção", sub: ["Combustíveis e lubrificantes", "Peças e componentes", "Oficinas e serviços mecânicos"] },
        { nome: "2. Serviços de Apoio e Gestão", sub: ["Tecnologia e rastreamento", "Pedágio e meios de pagamento", "Seguros", "Serviços gerais e administrativos"] },
        { nome: "3. Terceirização de Transporte (Agregados e Terceiros)", sub: ["Transportadores autônomos de cargas (TAC) / Agregados", "Empresas parceiras de apoio"] },
        { nome: "4. Infraestrutura e Movimentação de Carga", sub: ["Fabricantes de carrocerias e implementos", "Locadoras de veículos e frotas", "Equipamentos de movimentação", "Sistemas de armazenagem (Estruturas)"] },
        { nome: "5. Segurança e Gerenciamento de Risco (GR)", sub: ["Gerenciadoras de risco", "Empresas de pronta resposta", "Sistemas de segurança física"] },
        { nome: "6. Sustentabilidade e ESG", sub: ["Gestão de resíduos", "Consultorias de transição energética"] },
        { nome: "7. Recursos Humanos e Capacitação", sub: ["Treinamento e direção defensiva", "Agências de recrutamento especializadas", "Plataformas de saúde ocupacional"] }
      ];

      for (const cat of dados) {
        try {
          const res = await apiPost<any>("/tipos-fornecedores", { nome: cat.nome });
          for (const sub of cat.sub) {
            await apiPost("/tipos-fornecedores", { nome: sub, categoria_pai_id: res.id });
          }
        } catch (e: any) {
          if (e.message?.includes("409") || e.message?.includes("Já existe")) {
            console.log(`Categoria já existe: ${cat.nome}`);
          }
        }
      }
    },
    onSuccess: () => {
      toast.success("Lista base populada com sucesso!");
      qc.invalidateQueries({ queryKey: ["tipos-fornecedores"] });
    },
    onError: () => toast.error("Erro ao popular a lista.")
  });

  const popularLista = () => {
    if (confirm("Isso vai adicionar as 7 categorias e todas as subcategorias na base. Deseja continuar?")) {
      seed.mutate();
    }
  };

'''
        c = c[:idx] + seed_code + c[idx:]
        print("✅ Função 'popularLista' e a mutation 'seed' adicionadas.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)