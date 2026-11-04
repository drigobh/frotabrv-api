import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove o cellDates: true e deixa o Excel entregar o texto puro
c = c.replace("const wb = XLSX.read(bstr, { type: 'binary', cellDates: true });", "const wb = XLSX.read(bstr, { type: 'binary' });")
c = c.replace("const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: \"\", raw: true });", "const data: any[] = XLSX.utils.sheet_to_json(ws, { defval: \"\", raw: true });")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Leitura do Excel corrigida! Agora o N.º Série virá como texto puro.")