import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_BOTAO_POPULAR_FORN_{agora}.zip")
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

    # 1. Verificar se a query de parametrização existe
    if 'queryKey: ["parametrizacao-meta"]' not in c:
        c = c.replace(
            'const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });',
            'const { data: tipos = [] } = useQuery({ queryKey: ["tipos-fornecedores"], queryFn: () => apiGet<any[]>("/tipos-fornecedores") });\n  const { data: config } = useQuery({ queryKey: ["parametrizacao-meta"], queryFn: () => apiGet<any>("/parametrizacao/meta") });'
        )
        print("✅ Query de parametrização adicionada.")

    # 2. Adicionar a mutation de seed (se não existir)
    if 'const seed = useMutation({' not in c:
        c = c.replace(
            'const salvar = useMutation({',
            '''const seed = useMutation({
    mutationFn: () => apiPost("/tipos-fornecedores/seed", {}),
    onSuccess: () => { toast.success("Lista base populada!"); qc.invalidateQueries({ queryKey: ["tipos-fornecedores"] }); },
    onError: (e: any) => toast.error(e.message || "Erro")
  });

  const popularLista = () => {
    if (confirm("Isso vai adicionar as 7 categorias e todas as subcategorias na base. Deseja continuar?")) {
      seed.mutate();
    }
  };

  const salvar = useMutation({'''
        )
        print("✅ Mutation 'seed' adicionada.")

    # 3. Adicionar o botão "Popular Lista Base" no PageHeader (antes do "Mapa dos Fornecedores", se existir)
    if 'Popular Lista Base' not in c:
        # Verifica se existe o botão "Mapa dos Fornecedores"
        alvo_mapa = '<Button variant="outline" onClick={abrirMapaCompleto}'
        if alvo_mapa in c:
            # Insere antes do botão do mapa
            novo = '''{config?.mostrar_seed_fornecedores && (
              <Button variant="outline" onClick={popularLista} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">
                <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Lista Base"}
              </Button>
            )}
            '''
            c = c.replace(alvo_mapa, novo + alvo_mapa)
            print("✅ Botão 'Popular Lista Base' adicionado antes do Mapa.")
        else:
            # Se não existir mapa, insere após o PageHeader
            alvo = 'actions={<div className="flex gap-2">'
            if alvo in c:
                novo = 'actions={<div className="flex gap-2">\n          {config?.mostrar_seed_fornecedores && (\n            <Button variant="outline" onClick={popularLista} disabled={seed.isPending} className="border-amber-500/40 text-amber-400 hover:bg-amber-500/10 h-9">\n              <Database className="size-4 mr-2" /> {seed.isPending ? "Populando..." : "Popular Lista Base"}\n            </Button>\n          )}'
                c = c.replace(alvo, novo)
                print("✅ Botão 'Popular Lista Base' adicionado via fallback.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ TiposFornecedores.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")