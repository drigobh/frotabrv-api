import os
import re
import zipfile
import shutil
import glob

def restaurar_backup(raiz):
    # Procura o backup mais recente que contenha Pneus.tsx
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    if not os.path.exists(pasta_backups):
        print("❌ Pasta de backups não encontrada.")
        return False

    zips = glob.glob(os.path.join(pasta_backups, "*.zip"))
    zips.sort(key=os.path.getmtime, reverse=True)

    for z in zips:
        try:
            with zipfile.ZipFile(z, 'r') as zipf:
                nomes = zipf.namelist()
                if any("Pneus.tsx" in n for n in nomes):
                    # Extrai o Pneus.tsx para o local correto
                    for n in nomes:
                        if n.endswith("Pneus.tsx"):
                            zipf.extract(n, raiz)
                            origem = os.path.join(raiz, n)
                            destino = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
                            shutil.move(origem, destino)
                            print(f"✅ Backup restaurado: {z}")
                            return True
        except Exception as e:
            continue

    print("⚠️ Nenhum backup com Pneus.tsx encontrado.")
    return False

def aplicar_correcao(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")
    if not os.path.exists(caminho):
        print("❌ Pneus.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Adicionar a função parseDate após as constantes
    if 'const parseDate' not in c:
        # Procura a linha das constantes e insere depois
        padrao = re.compile(r'(const TIPOS_PNEU = \[[^\]]+\];\n)')
        match = padrao.search(c)
        if match:
            funcao = '''
const parseDate = (val: any): string => {
  if (!val) return "";
  const str = String(val).trim();
  if (!str) return "";
  if (/^\\d{4}-\\d{2}-\\d{2}/.test(str)) {
    return str.split("T")[0].split(" ")[0];
  }
  const num = Number(str);
  if (!isNaN(num) && num > 0) {
    const date = new Date((num - 25569) * 86400 * 1000);
    return date.toISOString().split("T")[0];
  }
  const d = new Date(str);
  if (!isNaN(d.getTime())) {
    return d.toISOString().split("T")[0];
  }
  return "";
};
'''
            c = c[:match.end()] + funcao + c[match.end():]
            print("✅ Função parseDate adicionada.")
        else:
            print("⚠️ Não foi possível inserir parseDate.")

    # 2. Substituir no abrirEdicao
    c = c.replace(
        'data_compra: r.data_compra ? String(r.data_compra).split("T")[0].split(" ")[0] : "",',
        'data_compra: parseDate(r.data_compra),'
    )
    c = c.replace(
        'data_descarte: r.data_descarte ? String(r.data_descarte).split("T")[0].split(" ")[0] : "",',
        'data_descarte: parseDate(r.data_descarte),'
    )

    # 3. Substituir no handleImportFile
    c = c.replace(
        'const wb = XLSX.read(bstr, { type: \'binary\' });',
        'const wb = XLSX.read(bstr, { type: \'binary\', cellDates: true });'
    )
    c = c.replace(
        'const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: "" });',
        'const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: "", raw: false });'
    )
    c = c.replace(
        'data_compra: data_compra_raw ? data_compra_raw.split("T")[0].split(" ")[0] : "",',
        'data_compra: parseDate(data_compra_raw),'
    )
    c = c.replace(
        'data_descarte: data_descarte_raw ? data_descarte_raw.split("T")[0].split(" ")[0] : "",',
        'data_descarte: parseDate(data_descarte_raw),'
    )

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(c)
    print("✅ Correções de data aplicadas cirurgicamente.")

if __name__ == "__main__":
    raiz = os.getcwd()
    if restaurar_backup(raiz):
        aplicar_correcao(raiz)
    else:
        print("⚠️ Não foi possível restaurar o backup. A correção não foi aplicada.")