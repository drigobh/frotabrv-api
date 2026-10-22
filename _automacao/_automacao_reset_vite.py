import os
import shutil
import subprocess

def reset_vite():
    raiz = os.getcwd()
    
    # 1. Para qualquer processo do Node/Vite que esteja rodando
    print("🛑 Parando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Apaga a pasta node_modules/.vite (cache do Vite)
    caminho_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("🧹 Cache do Vite apagado.")
    else:
        print("ℹ️ Cache do Vite já estava limpo.")

    # 3. Apaga a pasta dist (build antigo)
    caminho_dist = os.path.join(raiz, "frontend", "dist")
    if os.path.exists(caminho_dist):
        shutil.rmtree(caminho_dist)
        print("🧹 Pasta dist apagada.")

    print("\n✅ Reset concluído! Agora siga os passos:")
    print("1. No terminal, rode: cd frontend")
    print("2. Rode: yarn dev")
    print("3. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000")

if __name__ == "__main__":
    reset_vite()