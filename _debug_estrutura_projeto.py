import os

def diagnosticar():
    raiz = os.getcwd()
    resultado = []
    
    # 1. Verificar estrutura do Backend
    resultado.append("=== BACKEND ===")
    backend_routers = os.path.join(raiz, "app", "backend", "routers")
    if os.path.exists(backend_routers):
        resultado.append(f"Routers existentes: {os.listdir(backend_routers)}")
    
    backend_models = os.path.join(raiz, "app", "backend", "models")
    if os.path.exists(backend_models):
        resultado.append(f"Models existentes: {os.listdir(backend_models)}")
    
    # 2. Verificar Sidebar
    resultado.append("\n=== SIDEBAR ===")
    sidebar = os.path.join(raiz, "frontend", "src", "components", "layout", "Sidebar.tsx")
    if os.path.exists(sidebar):
        with open(sidebar, 'r', encoding='utf-8') as f:
            c = f.read()
        # Procura por 'Administração'
        idx = c.find('Administração')
        if idx != -1:
            resultado.append(f"Menu 'Administração' encontrado na posição {idx}")
            resultado.append(c[max(0, idx-300):idx+500])
        else:
            resultado.append("Menu 'Administração' NÃO encontrado")
    
    # 3. Verificar App.tsx
    resultado.append("\n=== APP.TSX (Rotas) ===")
    app_tsx = os.path.join(raiz, "frontend", "src", "App.tsx")
    if os.path.exists(app_tsx):
        with open(app_tsx, 'r', encoding='utf-8') as f:
            c = f.read()
        # Procura por 'admin'
        import re
        matches = re.findall(r'<Route path="[^"]*admin[^"]*"[^>]*/>', c)
        for m in matches:
            resultado.append(m)
    
    with open('debug_projeto.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(resultado))
    print("✅ Diagnóstico salvo em debug_projeto.txt")

if __name__ == "__main__":
    diagnosticar()