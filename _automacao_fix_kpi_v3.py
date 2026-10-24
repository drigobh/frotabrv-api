import os
import re

def fix_ui(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Forçar o formulário manual a iniciar com origem "manual"
    start_vazio = c.find('const vazio = (hoje: string) => ({')
    end_vazio = c.find('});', start_vazio)
    if start_vazio != -1 and end_vazio != -1:
        bloco_vazio = c[start_vazio:end_vazio]
        bloco_vazio = re.sub(r'origem:\s*"[^"]+"', 'origem: "manual"', bloco_vazio)
        c = c[:start_vazio] + bloco_vazio + c[end_vazio:]
        print("✅ Origem do formulário manual corrigida para 'manual'.")

    # 2. Substituir o bloco do Termômetro usando corte preciso (Slicing)
    start_map = c.find('{ranking.length === 0')
    end_map = c.find('<div className="mb-4 flex flex-wrap items-end gap-3">', start_map)

    if start_map != -1 and end_map != -1:
        novo_bloco = '''{ranking.length === 0 ? <p className="text-sm text-slate-500">Sem dados.</p> : ranking.map((r, i) => {
              const p = Math.min((r.media / 5) * 100, 100);
              return (
                <div key={r.label} className="flex items-center gap-3 w-full bg-slate-900/60 p-2 rounded-lg border border-slate-800/80">
                  <span className="w-6 text-xs text-slate-500 font-mono text-center">{i + 1}º</span>
                  <span className="w-20 text-sm font-semibold text-slate-300 font-mono truncate">{r.label.split(" ")[0]}</span>
                  <div className="flex-1 h-4 bg-slate-950 rounded-full overflow-hidden shadow-inner border border-slate-700 relative">
                    <div 
                      className="h-full rounded-full transition-all duration-500" 
                      style={{ 
                        width: `${p}%`, 
                        background: 'linear-gradient(90deg, #ef4444 0%, #f59e0b 30%, #eab308 50%, #22c55e 80%, #10b981 100%)',
                        boxShadow: '0 0 10px rgba(16, 185, 129, 0.3)'
                      }} 
                    />
                  </div>
                  <span className="w-14 text-right text-sm font-bold text-slate-100 bg-slate-800/80 py-0.5 px-2 rounded">{num(r.media, 2)}</span>
                </div>
              );
          })}
        </div>
      </div>

      '''
        c = c[:start_map] + novo_bloco + c[end_map:]
        print("✅ Termômetro substituído com gradiente KPI.")
    else:
        print("❌ Ainda não foi possível encontrar o bloco do termômetro.")

    # 3. Reforçar a leitura do Edenred (para consertar os cards zerados)
    if 'const idxValor = findIdx("VALOR EMISSAO");' in c:
        # Adiciona um fallback caso a coluna não seja encontrada pelo nome exato
        c = c.replace('const idxValor = findIdx("VALOR EMISSAO");', 'let idxValor = findIdx("VALOR EMISSAO");\n      if (idxValor === -1) idxValor = findIdx("VALOR");')
        print("✅ Leitura de colunas do Edenred reforçada.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    fix_ui(os.getcwd())