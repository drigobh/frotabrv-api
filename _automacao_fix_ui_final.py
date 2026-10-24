import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # Adicionar created_by_name no dicionário doc
    if "created_by_name" not in c:
        c = c.replace(
            '"created_by": user.get("id", "sistema"),',
            '"created_by": user.get("id", "sistema"),\n        "created_by_name": user.get("nome", user.get("email", "Sistema")),'
        )
        # Para o caso de estar usando outra formatação
        c = c.replace(
            '"created_by": user["id"],',
            '"created_by": user["id"],\n    "created_by_name": user.get("nome", user.get("email", "Sistema")),'
        )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend atualizado com created_by_name.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Atualizar o envio de origem no BSoft
    c = c.replace('origem: "excel"', 'origem: "bsoft"')
    
    # 2. Atualizar o envio de origem no Edenred
    # (O script do Edenred já foi criado com "excel", precisamos mudar apenas na função edenred)
    # Vamos garantir que a função edenred envie "edenred" e não "bsoft"
    if 'const handleImportEdenred' in c:
        # Isola a função edenred para não afetar o BSoft
        c = c.replace(
            'origem: "bsoft"',
            'origem: "edenred"',
            1 # Troca só a primeira ocorrência se estiver dentro do bloco edenred (hack rápido, mas vamos ser precisos)
        )
        # Como o replace é perigoso, vamos fazer manualmente:
        # Encontra o bloco do Edenred e muda
        import re
        c = re.sub(r'(const handleImportEdenred = async[\s\S]*?origem:\s*)"bsoft"', r'\1"edenred"', c)
        # Restaura o BSoft
        c = re.sub(r'(const handleImportXLS = async[\s\S]*?origem:\s*)"bsoft"', r'\1"bsoft"', c)

    # 3. Atualizar a coluna Origem no Grid
    old_origem = '''{r.origem === "pdf" ? <span className="bg-red-500/20 text-red-400 px-2 py-0.5 font-bold rounded">PDF</span> : r.origem === "excel" ? <span className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 font-bold rounded">XLS</span> : <span className="bg-slate-500/20 text-slate-400 px-2 py-0.5 font-bold rounded">M</span>}'''
    
    new_origem = '''{r.origem === "pdf" ? (
                  <span title="Importado PDF (NF)" className="bg-red-500/20 text-red-400 px-2 py-0.5 text-[10px] font-bold rounded">NF</span>
                ) : r.origem === "bsoft" ? (
                  <span title="Importado BSOFT" className="bg-sky-500/20 text-sky-400 px-2 py-0.5 text-[10px] font-bold rounded">BS</span>
                ) : r.origem === "edenred" ? (
                  <span title="Importado Edenred" className="bg-purple-500/20 text-purple-400 px-2 py-0.5 text-[10px] font-bold rounded">ED</span>
                ) : r.origem === "excel" ? (
                  <span title="Excel Antigo" className="bg-emerald-500/20 text-emerald-400 px-2 py-0.5 text-[10px] font-bold rounded">XLS</span>
                ) : (
                  <span title="Manual" className="bg-slate-500/20 text-slate-400 px-2 py-0.5 text-[10px] font-bold rounded">MA</span>
                )}'''
    
    if old_origem in c:
        c = c.replace(old_origem, new_origem)

    # 4. Adicionar ícone de Info nas Ações
    old_actions = '''<div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'''
    
    new_actions = '''<div className="flex gap-1 justify-center">
                    <Button size="icon-sm" variant="ghost" className="cursor-help" title={`Criado/Importado por: ${(r as any).created_by_name || 'Sistema'}`}>
                      <Info className="size-4 text-slate-400" />
                    </Button>
                    <Button size="icon-sm" variant="ghost" onClick={() => abrirEdicao(r)}><Pencil className="size-4 text-sky-400" /></Button>'''
    
    if old_actions in c:
        c = c.replace(old_actions, new_actions)

    # 5. Substituir o bloco do Termômetro pelo Gradiente (via Regex para garantir)
    # O bloco antigo usa a estrutura <div className="flex items-center gap-3 w-full"> ... </div>
    padrao_termometro = re.compile(
        r'<div key=\{r\.label\} className="flex items-center gap-3 w-full">[\s\S]*?</div>\s*</div>\s*\);',
        re.DOTALL
    )

    novo_termometro = '''<div key={r.label} className="flex items-center gap-3 w-full bg-slate-900/40 p-1.5 rounded-lg border border-slate-800/50">
                  <span className="w-6 text-xs text-slate-500 font-mono text-center">{i + 1}º</span>
                  <span className="w-20 text-sm font-semibold text-slate-300 font-mono truncate">{r.label.split(" ")[0]}</span>
                  <div className="flex-1 h-4 bg-slate-950 rounded-full overflow-hidden shadow-inner border border-slate-800 relative">
                    <div 
                      className="h-full rounded-full transition-all duration-500" 
                      style={{ 
                        width: `${p}%`, 
                        background: 'linear-gradient(90deg, #ef4444 0%, #f59e0b 30%, #eab308 50%, #22c55e 80%, #10b981 100%)',
                        boxShadow: '0 0 10px rgba(16, 185, 129, 0.3)'
                      }} 
                    />
                  </div>
                  <span className="w-14 text-right text-sm font-bold text-slate-100 bg-slate-800/50 py-0.5 px-2 rounded">{num(r.media, 2)}</span>
                </div>
              );'''

    if padrao_termometro.search(c):
        c = padrao_termometro.sub(novo_termometro, c)
    else:
        # Fallback mais bruto caso o regex falhe
        c = re.sub(r'\{ranking\.map\(\(r, i\) => \{[\s\S]*?\}\)\}', 
                   '''{ranking.map((r, i) => {
              const p = Math.min((r.media / 5) * 100, 100);
              return (
                <div key={r.label} className="flex items-center gap-3 w-full bg-slate-900/40 p-1.5 rounded-lg border border-slate-800/50">
                  <span className="w-6 text-xs text-slate-500 font-mono text-center">{i + 1}º</span>
                  <span className="w-20 text-sm font-semibold text-slate-300 font-mono truncate">{r.label.split(" ")[0]}</span>
                  <div className="flex-1 h-4 bg-slate-950 rounded-full overflow-hidden shadow-inner border border-slate-800 relative">
                    <div 
                      className="h-full rounded-full transition-all duration-500" 
                      style={{ 
                        width: `${p}%`, 
                        background: 'linear-gradient(90deg, #ef4444 0%, #f59e0b 30%, #eab308 50%, #22c55e 80%, #10b981 100%)',
                        boxShadow: '0 0 10px rgba(16, 185, 129, 0.3)'
                      }} 
                    />
                  </div>
                  <span className="w-14 text-right text-sm font-bold text-slate-100 bg-slate-800/50 py-0.5 px-2 rounded">{num(r.media, 2)}</span>
                </div>
              );
            })}''', c)

    # Garantir importação do Info
    if "Info" not in c.split("from \"lucide-react\"")[0]:
        c = c.replace('import { ', 'import { Info, ')

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend atualizado: Origem (BS, ED, NF, MA), Info de usuário e Termômetro Gradiente.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)