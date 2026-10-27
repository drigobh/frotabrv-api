import os
import re
import datetime
import zipfile

def backup(raiz):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho_zip = os.path.join(raiz, "_automacao", "backups", f"BACKUP_CARDS_MATH_{agora}.zip")
    os.makedirs(os.path.dirname(caminho_zip), exist_ok=True)
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for p in ["frontend/src/pages/Abastecimentos.tsx"]:
            caminho_abs = os.path.join(raiz, p)
            if os.path.exists(caminho_abs):
                zipf.write(caminho_abs, p)
    print(f"✅ Backup salvo: {caminho_zip}")

def fix(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Substituir o bloco do resumo por um cálculo 100% à prova de falhas
    inicio = c.find('const resumo = useMemo(() => {')
    fim = c.find('}, [rowsFiltradas]);', inicio)
    
    if inicio != -1 and fim != -1:
        fim += len('}, [rowsFiltradas]);')
        
        novo_bloco = '''const parseSafe = (val: any) => {
        if (val === undefined || val === null || val === "") return 0;
        if (typeof val === 'number') return val;
        let str = String(val).replace(/[^0-9.,-]/g, "");
        if (str.includes('.') && str.includes(',')) str = str.replace(/\\./g, '').replace(',', '.');
        else if (str.includes(',')) str = str.replace(',', '.');
        return Number(str) || 0;
      };

      const resumo = useMemo(() => {
        const litros = rowsFiltradas.reduce((s, r) => s + parseSafe(r.litros), 0);
        const valor = rowsFiltradas.reduce((s, r) => s + parseSafe(r.valor_total), 0);
        const km = rowsFiltradas.reduce((s, r) => s + parseSafe(r.km_rodados), 0);
        const comMedia = rowsFiltradas.filter(r => parseSafe(r.media_km_l) > 0);
        const mediaGeral = comMedia.length > 0 ? comMedia.reduce((s, r) => s + parseSafe(r.media_km_l), 0) / comMedia.length : 0;
        const preco = litros > 0 ? valor / litros : 0;
        const maior = rowsFiltradas.reduce((max, r) => parseSafe(r.valor_total) > parseSafe(max?.valor_total) ? r : max, null as Abastecimento | null);
        const menor = rowsFiltradas.reduce((min, r) => parseSafe(r.valor_total) < parseSafe(min?.valor_total) || !min ? r : min, null as Abastecimento | null);
        return { litros, valor, km, media: litros > 0 ? km / litros : 0, preco, total: rowsFiltradas.length, maior, menor, mediaValor: rowsFiltradas.length > 0 ? valor / rowsFiltradas.length : 0, mediaKm: rowsFiltradas.length > 0 ? km / rowsFiltradas.length : 0, custoPorKm: km > 0 ? valor / km : 0, comNF: rowsFiltradas.filter(r => r.numero_nf).length, semNF: rowsFiltradas.filter(r => !r.numero_nf).length };
      }, [rowsFiltradas]);'''
        
        c = c[:inicio] + novo_bloco + c[fim:]
        print("✅ Cálculo dos Cards blindado com sucesso.")
    else:
        print("⚠️ Não foi possível encontrar o bloco resumo.")

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)

if __name__ == "__main__":
    raiz = os.getcwd()
    backup(raiz)
    fix(raiz)