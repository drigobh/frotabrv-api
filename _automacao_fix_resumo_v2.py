import os
import re

def corrigir(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui o bloco useMemo(resumo) inteiro
    padrao = re.compile(r'const resumo = useMemo\(\(\) => \{[\s\S]*?\}, \[rows\]\);', re.DOTALL)
    
    novo_resumo = '''const resumo = useMemo(() => {
    const litros = rows.reduce((s, r) => s + r.litros, 0);
    const valor = rows.reduce((s, r) => s + r.valor_total, 0);
    const comKm = rows.filter((r) => r.km_rodados != null);
    const km = comKm.reduce((s, r) => s + (r.km_rodados ?? 0), 0);
    const litrosKm = comKm.reduce((s, r) => s + r.litros, 0);
    
    const maior = rows.reduce((max, r) => r.valor_total > (max?.valor_total || 0) ? r : max, null as Abastecimento | null);
    const menor = rows.reduce((min, r) => r.valor_total < (min?.valor_total || Infinity) ? r : min, null as Abastecimento | null);
    const mediaValor = rows.length ? valor / rows.length : 0;
    const mediaKm = comKm.length ? km / comKm.length : 0;
    const custoPorKm = km > 0 ? valor / km : 0;

    return { 
      litros, valor, km, media: litrosKm ? km / litrosKm : 0, preco: litros ? valor / litros : 0,
      total: rows.length, maior, menor, mediaValor, mediaKm, custoPorKm
    };
  }, [rows]);'''

    if padrao.search(conteudo):
        conteudo = padrao.sub(novo_resumo, conteudo)
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Bloco 'resumo' substituído com sucesso!")
    else:
        print("❌ Não foi possível encontrar o bloco 'resumo'.")

if __name__ == "__main__":
    corrigir(os.getcwd())