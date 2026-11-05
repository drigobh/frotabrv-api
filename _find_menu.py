import os

raiz = os.getcwd()
print("🔍 Buscando arquivos de menu/layout no projeto...\n")

for root, dirs, files in os.walk(os.path.join(raiz, "frontend", "src")):
    if "node_modules" in root: continue
    for f in files:
        if any(x in f.lower() for x in ["sidebar", "menu", "layout", "nav"]):
            print(f"📄 {os.path.join(root, f)}")