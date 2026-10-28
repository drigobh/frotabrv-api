import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_MATEMATICA_MEDIA_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    caminho_abs = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    if os.path.exists(caminho_abs):
        with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(caminho_abs, "frontend/src/pages/Abastecimentos.tsx")
        print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Substituir o bloco 'resumo' (Cards)
    padrao_resumo = re.compile(r'const resumo = useMemo\(\(\) => \{[\s\S]*?\}, \[rowsFiltradas\]\);', re.DOTALL)
    
    novo_resumo = '''const resumo = useMemo(() => {
    const validRows = rowsFiltradas.filter(r => !r.produto?.toUpperCase().includes("ARLA"));
    const litros = validRows.reduce((s, r) => s + (Number(r.litros) || 0), 0);
    const valor = validRows.reduce((s, r) => s + (Number(r.valor_total) || 0), 0);
    const km = validRows.reduce((s, r) => s + (Number(r.km_rodados) || 0), 0);
    
    // A média geral é a média das médias dos registros válidos (que já foram calculadas corretamente pelo backend)
    const comMedia = validRows.filter(r => r.media_km_l != null && r.media_km_l > 0);
    const mediaGeral = comMedia.length > 0 ? comMedia.reduce((s, r) => s + Number(r.media_km_l), 0) / comMedia.length : 0;
    
    const preco = litros > 0 ? valor / litros : 0;
    const maior = validRows.reduce((max, r) => (Number(r.valor_total) || 0) > (Number(max?.valor_total) || 0) ? r : max, null as any);
    const menor = validRows.reduce((min, r) => (Number(r.valor_total) || 0) < (Number(min?.valor_total) || Infinity) ? r : min, null as any);
    
    return { 
      litros, valor, km, 
      media: mediaGeral, 
      preco, 
      total: validRows.length, 
      maior, menor, 
      mediaValor: validRows.length > 0 ? valor / validRows.length : 0, 
      mediaKm: validRows.length > 0 ? km / validRows.length : 0, 
      custoPorKm: km > 0 ? valor / km : 0, 
      comNF: validRows.filter(r => r.numero_nf).length, 
      semNF: validRows.filter(r => !r.numero_nf).length,
      mediaGeral: mediaGeral
    };
  }, [rowsFiltradas]);'''

    if padrao_resumo.search(c):
        c = padrao_resumo.sub(novo_resumo, c)
        print("✅ Bloco 'resumo' (Cards) atualizado com a matemática correta.")
    else:
        print("⚠️ Bloco 'resumo' não encontrado.")

    # 2. Substituir o bloco 'ranking' (Termômetro)
    padrao_ranking = re.compile(r'const ranking = useMemo\(\(\) => \{[\s\S]*?\}, \[rowsFiltradas\]\);', re.DOTALL)
    
    novo_ranking = '''const ranking = useMemo(() => {
    const porVeiculo: Record<string, { label: string, soma: number, count: number }> = {};
    for (const r of rowsFiltradas) {
      // Ignora ARLA e registros sem média calculada
      if (r.produto?.toUpperCase().includes("ARLA")) continue;
      if (r.media_km_l == null || r.media_km_l <= 0) continue;
      
      if (!porVeiculo[r.veiculo_id]) {
        porVeiculo[r.veiculo_id] = { label: r.veiculo_label?.split(" · ")[0] || "—", soma: 0, count: 0 };
      }
      porVeiculo[r.veiculo_id].soma += Number(r.media_km_l);
      porVeiculo[r.veiculo_id].count += 1;
    }
    return Object.values(porVeiculo)
      .map(v => ({ label: v.label, media: v.count > 0 ? v.soma / v.count : 0 }))
      .filter(v => v.media > 0)
      .sort((a, b) => b.media - a.media)
      .slice(0, 5);
  }, [rowsFiltradas]);'''

    if padrao_ranking.search(c):
        c = padrao_ranking.sub(novo_ranking, c)
        print("✅ Bloco 'ranking' (Termômetro) atualizado com a matemática correta.")
    else:
        print("⚠️ Bloco 'ranking' não encontrado.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Script aplicado com sucesso!")

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)