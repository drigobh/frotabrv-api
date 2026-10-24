import os
import re

def fix_ui(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Renomear botão XLS para BSOFT
    c = c.replace('Importar XLS</Button>', 'Importar BSOFT</Button>')

    # 2. Reduzir o tamanho dos Cards
    old_cards = '''<div className="mb-5 grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {cards.map((c) => (
          <div key={c.label} title={c.tip} className="glass lift relative overflow-hidden rounded-xl hover:scale-[1.02] cursor-help" style={{ padding: '12px 16px', height: '90px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '28px', height: '28px', borderRadius: '8px', backgroundColor: `${c.color}20`, color: c.color }}><c.icon size={16} /></div>
              <p style={{ fontSize: '12px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            </div>
            <div>
              <p style={{ fontSize: '20px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '10px', color: '#64748b', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.sub}</p>}
            </div>
          </div>
        ))}
      </div>'''
      
    new_cards = '''<div className="mb-4 grid gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
        {cards.map((c) => (
          <div key={c.label} title={c.tip} className="glass lift relative overflow-hidden rounded-xl hover:scale-[1.02] cursor-help" style={{ padding: '8px 12px', height: '72px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '22px', height: '22px', borderRadius: '6px', backgroundColor: `${c.color}20`, color: c.color }}><c.icon size={12} /></div>
              <p style={{ fontSize: '11px', color: '#94a3b8', margin: 0, fontWeight: 500 }}>{c.label}</p>
            </div>
            <div>
              <p style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', margin: 0, lineHeight: 1.1 }}>{c.valor}</p>
              {c.sub && <p style={{ fontSize: '9px', color: '#64748b', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{c.sub}</p>}
            </div>
          </div>
        ))}
      </div>'''
    
    if old_cards in c:
        c = c.replace(old_cards, new_cards)
    else:
        # Fallback caso o texto tenha pequenas diferenças
        c = re.sub(r'<div className="mb-5 grid gap-3[\s\S]*?</div>\s*</div>\s*<div className="mb-5 glass', new_cards + '\n      <div className="mb-5 glass', c)

    # 3. Melhorar o Termômetro com Gradiente (Estilo KPI)
    old_thermometer = '''<div className="flex items-center gap-3 w-full">
                  <span className="w-6 text-xs text-slate-500 font-mono">{i + 1}º</span>
                  <span className="w-20 text-sm font-medium text-slate-300 font-mono">{r.label.split(" ")[0]}</span>
                  <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden"><div className={`h-full ${good ? 'bg-emerald-500' : 'bg-red-500'}`} style={{ width: `${p}%` }} /></div>
                  <span className="w-12 text-right text-sm font-bold text-slate-200">{num(r.media, 2)}</span>
                </div>'''

    new_thermometer = '''<div className="flex items-center gap-3 w-full bg-slate-900/40 p-1.5 rounded-lg border border-slate-800/50">
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
                </div>'''

    if old_thermometer in c:
        c = c.replace(old_thermometer, new_thermometer)
    else:
        # Fallback
        c = re.sub(r'<div className="flex items-center gap-3 w-full">[\s\S]*?<span className="w-12 text-right text-sm font-bold text-slate-200">\{num\(r\.media, 2\)\}</span>\s*</div>', new_thermometer, c)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Interface atualizada: Botão BSOFT, Cards compactos e Termômetro com Gradiente KPI.")

if __name__ == "__main__":
    fix_ui(os.getcwd())