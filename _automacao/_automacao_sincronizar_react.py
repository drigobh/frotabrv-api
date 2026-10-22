import os
import shutil
import subprocess
import json

def sincronizar_react():
    raiz = os.getcwd()
    pasta_front = os.path.join(raiz, "frontend")

    print("🛑 Fechando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("🧹 Apagando pastas e lockfile...")
    for pasta in ["node_modules", "dist", ".vite"]:
        caminho = os.path.join(pasta_front, pasta)
        if os.path.exists(caminho):
            shutil.rmtree(caminho)

    caminho_lock = os.path.join(pasta_front, "yarn.lock")
    if os.path.exists(caminho_lock):
        os.remove(caminho_lock)

    # 2. Sincronizar versões no package.json
    caminho_pkg = os.path.join(pasta_front, "package.json")
    with open(caminho_pkg, 'r', encoding='utf-8') as f:
        pkg = json.load(f)

    # Força as versões do React e React DOM para a mesma
    versao_react = "19.0.0"
    if "dependencies" not in pkg:
        pkg["dependencies"] = {}
    
    pkg["dependencies"]["react"] = versao_react
    pkg["dependencies"]["react-dom"] = versao_react
    # Adiciona os types correspondentes
    if "devDependencies" not in pkg:
        pkg["devDependencies"] = {}
    pkg["devDependencies"]["@types/react"] = "^19.0.0"
    pkg["devDependencies"]["@types/react-dom"] = "^19.0.0"

    with open(caminho_pkg, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, indent=2)
    print(f"⚙️ package.json atualizado: React e React DOM na versão {versao_react}.")

    # 3. Instalar
    print("\n📦 Instalando dependências (isso demorará alguns minutos)...")
    try:
        subprocess.run(["npm", "install", "--legacy-peer-deps"], cwd=pasta_front, check=True, shell=True)
        print("✅ Dependências instaladas com npm.")
    except Exception as e:
        print(f"❌ Falha no npm: {e}")
        return

    # 4. Iniciar
    print("\n🚀 Iniciando o servidor...")
    try:
        subprocess.run(["npm", "run", "dev"], cwd=pasta_front, shell=True)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    sincronizar_react()