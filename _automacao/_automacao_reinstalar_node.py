import os
import shutil
import subprocess

def reinstalar_node():
    raiz = os.getcwd()
    print("🤖 Iniciando Reinstalação Completa do Node...")

    # 1. Matar processos do Node
    print("🛑 Fechando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Apagar a pasta node_modules
    caminho_node = os.path.join(raiz, "frontend", "node_modules")
    if os.path.exists(caminho_node):
        print("🧹 Apagando a pasta node_modules (pode demorar um pouco)...")
        shutil.rmtree(caminho_node)
        print("✅ Pasta node_modules apagada.")
    else:
        print("ℹ️ A pasta node_modules já não existia.")

    # 3. Apagar o yarn.lock para garantir versões frescas
    caminho_lock = os.path.join(raiz, "frontend", "yarn.lock")
    if os.path.exists(caminho_lock):
        os.remove(caminho_lock)
        print("🧹 yarn.lock removido para reinstalação limpa.")

    # 4. Rodar o yarn install
    print("\n📦 Rodando 'yarn install' (isso pode levar alguns minutos)...")
    os.chdir(os.path.join(raiz, "frontend"))
    subprocess.run(["yarn", "install"], check=True)
    
    print("\n✅ Reinstalação concluída com sucesso!")
    print("👉 Agora rode: yarn dev")
    print("👉 Abra o navegador em modo anônimo (Ctrl+Shift+N).")

if __name__ == "__main__":
    reinstalar_node()