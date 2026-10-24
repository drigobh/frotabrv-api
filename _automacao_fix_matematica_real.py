import os
import re

def fix_backend(raiz):
    caminho = os.path.join(raiz, "app", "backend", "routers", "abastecimentos.py")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Atualizar a função calcular_km com a regra do Hodômetro (290 -> 290.000)
    padrao_calc = re.compile(r'def limpar_km\([\s\S]*?return km_rodados, media_km_l', re.DOTALL)
    
    nova_calc = '''def limpar_km(val):
    if val is None: return 0
    s = str(val).strip()
    if s.endswith(".0"): s = s[:-2]
    s = "".join(filter(str.isdigit, s))
    return int(s) if s else 0

def calcular_km(km_atual, litros, produto, ultimo, veiculo):
    km_atual = limpar_km(km_atual)
    km_rodados = None
    media_km_l = None

    def normalizar_km(val_str):
        val = limpar_km(val_str)
        # Se o hodômetro for menor que 10000 (ex: 290, 304), multiplica por 1000 (290000, 304000)
        if 0 < val < 10000:
            val = val * 1000
        return val

    if ultimo and ultimo.get("km"):
        ultimo_km = normalizar_km(ultimo["km"])
        km_rodados = km_atual - ultimo_km
    elif veiculo.get("hodometro_km") is not None:
        veiculo_km = normalizar_km(veiculo["hodometro_km"])
        km_rodados = km_atual - veiculo_km

    # Trava de segurança
    if km_rodados is not None:
        if km_rodados <= 0 or km_rodados > 50000:
            km_rodados = None
        elif km_rodados > 0 and litros > 0 and "ARLA" not in (produto or "").upper():
            media_km_l = km_rodados / litros
        elif km_rodados == 0:
            media_km_l = 0

    return km_rodados, media_km_l'''
    
    if padrao_calc.search(c):
        c = padrao_calc.sub(nova_calc, c)

    # 2. Atualizar o Hodômetro do Veículo após salvar
    # (Busca pelo insert e adiciona a atualização do hodômetro)
    c = c.replace(
        'await db.abastecimentos.insert_one(doc)',
        '''await db.abastecimentos.insert_one(doc)
    if km_atual > 0:
        await db.veiculos.update_one({"id": veiculo["id"]}, {"$set": {"hodometro_km": km_atual}})'''
    )

    # O mesmo para o criar manual
    c = c.replace(
        'await db.abastecimentos.insert_one(doc)\n    doc.pop("_id", None)\n    return doc',
        '''await db.abastecimentos.insert_one(doc)
    if body.km > 0:
        await db.veiculos.update_one({"id": body.veiculo_id}, {"$set": {"hodometro_km": body.km}})
    doc.pop("_id", None)
    return doc'''
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Backend: Cálculo inteligente de KM e atualização automática do hodômetro.")

def fix_frontend(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Formatar data para dd/mm/yyyy
    if 'dataBR(r.data)' not in c:
        c = c.replace('{r.data.includes("-") ? r.data.split("-").reverse().join("/") : r.data}', '{dataBR(r.data)}')

    # 2. Corrigir o Termômetro (Gradiente Dinâmico)
    padrao_termometro = re.compile(r'\{ranking\.map\(\(r, i\) => \{[\s\S]*?\}\)\}')
    novo_termometro = '''{ranking.map((r, i) => {
              const maxMedia = ranking[0]?.media || 1;
              const p = Math.min((r.media / maxMedia) * 100, 100);
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
            })}'''
    
    if padrao_termometro.search(c):
        c = padrao_termometro.sub(novo_termometro, c)

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Frontend: Data e Termômetro corrigidos.")

if __name__ == "__main__":
    raiz = os.getcwd()
    fix_backend(raiz)
    fix_frontend(raiz)