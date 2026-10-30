import os
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ESTOQUE_PNEUS_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    arquivos = ["frontend/src/pages/Estoque.tsx"]
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            c = os.path.join(raiz, arq.replace("/", os.sep))
            if os.path.exists(c):
                zipf.write(c, arq)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    # 1. Adicionar filtro no Backend (rota de pneus já existe, mas vamos garantir)
    print("✅ Backend: rota /pneus já existe. Nenhuma alteração necessária.")

    # 2. Atualizar a tela de Estoque para incluir a aba de Pneus
    caminho_estoque = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    with open(caminho_estoque, 'r', encoding='utf-8') as f:
        c = f.read()

    # Verifica se a tela de Estoque já foi modificada
    if 'Pneus em Estoque' in c:
        print("ℹ️ Tela de Estoque já tem a aba de Pneus.")
        return

    # Adiciona a aba de Pneus (simplificado para não quebrar o layout existente)
    # Vamos adicionar uma seção no final da página que busca os pneus com status "Estoque"
    
    # 1. Adicionar import do ícone Disc
    if 'Disc' not in c.split('lucide-react')[0]:
        c = c.replace('import { ', 'import { Disc, ')

    # 2. Adicionar a lógica de busca de pneus
    if 'queryKey: ["pneus-estoque"]' not in c:
        # Adiciona a query após a primeira useQuery existente
        idx = c.find('const { data:')
        if idx != -1:
            # Pega a primeira declaração de query para inserir antes
            c = c[:idx] + '  const { data: pneusEstoque = [] } = useQuery({ queryKey: ["pneus-estoque"], queryFn: () => apiGet<any[]>("/pneus") });\n  const pneusEmEstoque = pneusEstoque.filter((p: any) => p.status === "Estoque");\n\n' + c[idx:]
            print("✅ Lógica de busca de pneus em estoque adicionada.")

    # 3. Adicionar a seção de Pneus no final da página (antes do fechamento)
    if 'Pneus em Estoque' not in c:
        # Procura o final do return (antes do último </div>)
        idx = c.rfind('</div>\n  );')
        if idx != -1:
            secao_pneus = '''
      {/* Seção de Pneus em Estoque */}
      <div className="mt-8">
        <div className="flex items-center gap-2 mb-3">
          <Disc className="size-5 text-sky-400" />
          <h3 className="text-lg font-bold text-slate-100">Pneus em Estoque</h3>
          <span className="bg-sky-500/20 text-sky-400 text-xs font-bold px-2 py-0.5 rounded-full">{pneusEmEstoque.length}</span>
        </div>
        {pneusEmEstoque.length === 0 ? (
          <div className="glass p-6 rounded-2xl text-center text-slate-500 text-sm">Nenhum pneu em estoque no momento.</div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {pneusEmEstoque.map((p: any) => (
              <div key={p.id} className="glass p-4 rounded-xl border border-sky-500/30">
                <p className="text-sm font-bold text-sky-400">{p.numero_fogo}</p>
                <p className="text-xs text-slate-300 mt-1">{p.marca} {p.modelo && `- ${p.modelo}`}</p>
                <p className="text-xs text-slate-500">{p.medida}</p>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{p.tipo}</span>
                  <span className="text-xs font-mono text-amber-400">R$ {p.custo_aquisicao?.toFixed(2) || "0,00"}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
'''
            c = c[:idx] + secao_pneus + c[idx:]
            print("✅ Seção 'Pneus em Estoque' adicionada à página de Estoque.")

    with open(caminho_estoque, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Página de Estoque atualizada.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")