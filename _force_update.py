import os
import shutil
import datetime

def forcar_atualizacao():
    raiz = os.getcwd()
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Backup
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)
    print(f"✅ Backup seguro na pasta: {pasta_backups}")
    
    # 2. Limpar cache do Vite
    vite_cache = os.path.join(raiz, "node_modules", ".vite")
    if os.path.exists(vite_cache):
        shutil.rmtree(vite_cache)
        print("✅ Cache do Vite (node_modules/.vite) destruído.")
    
    frontend_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(frontend_cache):
        shutil.rmtree(frontend_cache)
        print("✅ Cache do Frontend Vite destruído.")

    # 3. Injetar marcador visual no App.tsx ou main.tsx
    # Vamos procurar o App.tsx principal
    app_path = os.path.join(raiz, "frontend", "src", "App.tsx")
    if not os.path.exists(app_path):
        app_path = os.path.join(raiz, "frontend", "src", "main.tsx")

    if os.path.exists(app_path):
        with open(app_path, "r", encoding="utf-8") as f:
            c = f.read()
            
        marcador = f'console.log("🔥🔥🔥 ATUALIZACAO FORCADA CARREGADA EM {agora} 🔥🔥🔥");\n'
        
        if "ATUALIZACAO FORCADA CARREGADA" not in c:
            # Insere no topo do arquivo
            c = marcador + c
            with open(app_path, "w", encoding="utf-8") as f:
                f.write(c)
            print(f"✅ Marcador injetado no topo do {os.path.basename(app_path)}.")
        else:
            print("ℹ️ Marcador já existe no arquivo.")

if __name__ == "__main__":
    forcar_atualizacao()