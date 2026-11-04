import os, re

raiz = os.getcwd()
path = os.path.join(raiz, "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Substitui parseDate existente OU insere nova, robusta para M/D/YY
nova_fn = '''const parseDate = (val: any): string => {
  if (val === null || val === undefined || val === "") return "";
  if (val instanceof Date) {
    if (isNaN(val.getTime())) return "";
    const y = val.getUTCFullYear();
    const m = String(val.getUTCMonth() + 1).padStart(2, "0");
    const d = String(val.getUTCDate()).padStart(2, "0");
    return `${y}-${m}-${d}`;
  }
  const str = String(val).trim();
  if (!str) return "";
  if (/^\\d{4}-\\d{2}-\\d{2}/.test(str)) return str.slice(0, 10);
  if (/^\\d+(\\.\\d+)?$/.test(str)) {
    const num = parseFloat(str);
    if (num > 1000 && num < 100000) {
      const date = new Date((num - 25569) * 86400 * 1000);
      return date.toISOString().slice(0, 10);
    }
  }
  // M/D/YY, M/D/YYYY, DD/MM/YYYY, DD-MM-YY
  const m = str.match(/^(\\d{1,2})[\\/\\-](\\d{1,2})[\\/\\-](\\d{2,4})$/);
  if (m) {
    let a = Number(m[1]), b = Number(m[2]), c2 = Number(m[3]);
    if (c2 < 100) c2 += 2000;
    // US (M/D/Y) primeiro
    if (a >= 1 && a <= 12 && b >= 1 && b <= 31) {
      return `${c2}-${String(a).padStart(2, "0")}-${String(b).padStart(2, "0")}`;
    }
    // BR (D/M/Y)
    if (b >= 1 && b <= 12 && a >= 1 && a <= 31) {
      return `${c2}-${String(b).padStart(2, "0")}-${String(a).padStart(2, "0")}`;
    }
  }
  const d = new Date(str);
  if (!isNaN(d.getTime())) return d.toISOString().slice(0, 10);
  return "";
};'''

if "const parseDate" in c:
    c = re.sub(r"const parseDate =[\s\S]*?\n\};", nova_fn, c, count=1)
    print("✅ parseDate substituída")
else:
    c = c.replace(
        'const TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda", "Liso", "Borrachudo"];',
        'const TIPOS_PNEU = ["Direcional", "Tração", "Misto", "Banda", "Liso", "Borrachudo"];\n\n' + nova_fn
    )
    print("✅ parseDate inserida")

# 2. Substitui as chamadas de data_compra/data_descarte em abrirEdicao e import
subs = [
    (r"data_compra:\s*r\.data_compra\s*\?[^,\n]+?:\s*\"\"", 'data_compra: parseDate(r.data_compra)'),
    (r"data_descarte:\s*r\.data_descarte\s*\?[^,\n]+?:\s*\"\"", 'data_descarte: parseDate(r.data_descarte)'),
    (r"data_compra:\s*data_compra_raw\s*\?[^,\n]+?:\s*\"\"", 'data_compra: parseDate(data_compra_raw)'),
    (r"data_descarte:\s*data_descarte_raw\s*\?[^,\n]+?:\s*\"\"", 'data_descarte: parseDate(data_descarte_raw)'),
]
for old, new in subs:
    if re.search(old, c):
        c = re.sub(old, new, c)
        print(f"✅ substituído: {new}")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)
print("\n✅ Pneus.tsx atualizado. Faça: git add . && git commit -m 'fix: parseDate robusto M/D/YY' && git push")