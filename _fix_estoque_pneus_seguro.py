import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_ESTOQUE_PNEUS_SEGURO_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Estoque.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Estoque.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Garantir import do Disc APENAS no lucide-react (linha específica)
    linhas = c.split('\n')
    for i, linha in enumerate(linhas):
        if 'from "lucide-react"' in linha:
            if 'Disc' not in linha:
                linhas[i] = linha.replace('}', ', Disc }')
                print("✅ Import do Disc adicionado ao lucide-react.")
            break
    c = '\n'.join(linhas)

    # 2. Adicionar a query de pneus (se não existir)
    if 'queryKey: ["pneus-estoque"]' not in c:
        idx = c.find('const { data:')
        if idx != -1:
            c = c[:idx] + '  const { data: pneusEstoque = [] } = useQuery({ queryKey: ["pneus-estoque"], queryFn: () => apiGet<any[]>("/pneus") });\n  const pneusEmEstoque = pneusEstoque.filter((p: any) => p.status === "Estoque");\n\n' + c[idx:]
            print("✅ Lógica de busca de pneus adicionada.")

    # 3. Adicionar a seção visual de Pneus em Estoque (antes do fechamento)
    if 'Pneus em Estoque' not in c:
        idx = c.rfind('</div>\n  );')
        if idx != -1:
            secao = '''
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
            c = c[:idx] + secao + c[idx:]
            print("✅ Seção 'Pneus em Estoque' adicionada.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Estoque.tsx atualizado.")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)
    print("\n✅ Script aplicado com sucesso!")