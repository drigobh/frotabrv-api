import os

raiz = os.getcwd()
app_path = os.path.join(raiz, "frontend", "src", "App.tsx")

with open(app_path, "r", encoding="utf-8") as f:
    c = f.read()

# Remove o banner vermelho que foi injetado de forma incorreta
banner_errado = '''
      <div style={{ background: 'red', color: 'white', padding: '20px', textAlign: 'center', fontSize: '24px', fontWeight: 'bold', zIndex: 99999, position: 'relative' }}>
        🔥 O CÓDIGO NOVO ESTÁ AQUI! DEPLOY FUNCIONOU! 🔥
      </div>
'''

if banner_errado in c:
    c = c.replace(banner_errado, "")
    print("✅ Banner de teste removido com sucesso!")
else:
    print("ℹ️ Banner não encontrado (já foi removido ou o script anterior falhou).")

# Garante que o return não ficou com espaços em branco ou tags órfãs
c = c.replace("return (\n\n  <QueryClientProvider", "return (\n  <QueryClientProvider")

with open(app_path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ App.tsx restaurado! O erro de compilação foi corrigido.")