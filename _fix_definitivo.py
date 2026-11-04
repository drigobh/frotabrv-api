import os
import re

# Caminho do arquivo
path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Substitui a função parseDate por uma versão que entende M/D/YY e D/M/YYYY
nova_fn = '''const parseDate = (val: any): string => {
  if (!val) return "";
  if (val instanceof Date) {
    if (isNaN(val.getTime())) return "";
    return `${val.getFullYear()}-${String(val.getMonth()+1).padStart(2,'0')}-${String(val.getDate()).padStart(2,'0')}`;
  }
  const str = String(val).trim();
  if (!str) return "";
  if (/^\\d{4}-\\d{2}-\\d{2}/.test(str)) return str.slice(0, 10);
  if (/^\\d+(\\.\\d+)?$/.test(str)) {
    const num = parseFloat(str);
    if (num > 1000) {
      const d = new Date((num - 25569) * 86400 * 1000);
      return `${d.getUTCFullYear()}-${String(d.getUTCMonth()+1).padStart(2,'0')}-${String(d.getUTCDate()).padStart(2,'0')}`;
    }
  }
  // Lida com 9/25/26 ou 25/09/2026
  const parts = str.split(/[\\/\\-]/);
  if (parts.length === 3) {
     let p1 = parseInt(parts[0]), p2 = parseInt(parts[1]), p3 = parseInt(parts[2]);
     let d, m, y;
     if (p3 > 1000) { y = p3; } else { y = p3 + 2000; }
     if (p1 > 12) { d = p1; m = p2; } else { m = p1; d = p2; }
     if (d >= 1 && d <= 31 && m >= 1 && m <= 12) {
         return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
     }
  }
  return "";
};'''

if "const parseDate" in c:
    c = re.sub(r'const parseDate =[\s\S]*?\n\};', nova_fn, c, count=1)
else:
    c = c.replace('const TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda", "Liso", "Borrachudo"];', 'const TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda", "Liso", "Borrachudo"];\n\n' + nova_fn)

# 2. Substituição EXATA no abrirEdicao
c = c.replace('data_compra: r.data_compra ? String(r.data_compra).split("T")[0].split(" ")[0] : "",', 'data_compra: parseDate(r.data_compra),')
c = c.replace('data_descarte: r.data_descarte ? String(r.data_descarte).split("T")[0].split(" ")[0] : "",', 'data_descarte: parseDate(r.data_descarte),')

# 3. Substituição EXATA no handleImportFile
c = c.replace("const wb = XLSX.read(bstr, { type: 'binary' });", "const wb = XLSX.read(bstr, { type: 'binary', cellDates: true });")
c = c.replace('const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: "" });', 'const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: "", raw: true });')
c = c.replace('data_compra: data_compra_raw ? data_compra_raw.split("T")[0].split(" ")[0] : "",', 'data_compra: parseDate(data_compra_raw),')
c = c.replace('data_descarte: data_descarte_raw ? data_descarte_raw.split("T")[0].split(" ")[0] : "",', 'data_descarte: parseDate(data_descarte_raw),')

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Pneus.tsx atualizado! As datas agora serao lidas como Date Objects e convertidas certinho.")