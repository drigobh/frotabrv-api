import os

raiz = os.getcwd()
app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
if not os.path.exists(app_path):
    app_path = os.path.join(raiz, "frontend", "src", "main.tsx")

with open(app_path, "r", encoding="utf-8") as f:
    c = f.read()

banner = '''
      <div style={{ background: 'red', color: 'white', padding: '20px', textAlign: 'center', fontSize: '24px', fontWeight: 'bold', zIndex: 99999, position: 'relative' }}>
        🔥 O CÓDIGO NOVO ESTÁ AQUI! DEPLOY FUNCIONOU! 🔥
      </div>
'''
# Tenta injetar logo no início do return do App
if "O CÓDIGO NOVO ESTÁ AQUI" not in c:
    c = c.replace("return (", "return (\n" + banner, 1)
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(c)
    print("✅ Banner injetado no App.tsx!")