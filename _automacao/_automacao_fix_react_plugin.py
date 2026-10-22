import os
import shutil
import subprocess

def instalar_plugin_e_reconfigurar():
    raiz = os.getcwd()
    pasta_front = os.path.join(raiz, "frontend")

    print("🛑 Fechando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 1. Instalar o plugin vite-optimize-persist
    print("📦 Instalando plugin vite-optimize-persist...")
    try:
        subprocess.run(["npm", "install", "vite-optimize-persist", "--save-dev"], cwd=pasta_front, check=True, shell=True)
        print("✅ Plugin instalado.")
    except Exception as e:
        print(f"❌ Falha ao instalar plugin: {e}")
        return

    # 2. Atualizar o vite.config.ts
    caminho_config = os.path.join(pasta_front, "vite.config.ts")
    with open(caminho_config, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Adiciona o import do plugin
    if "vite-optimize-persist" not in conteudo:
        conteudo = conteudo.replace(
            'import react from "@vitejs/plugin-react";',
            'import react from "@vitejs/plugin-react";\nimport { optimizePersist } from "vite-optimize-persist";'
        )
        # Adiciona o plugin na lista de plugins
        conteudo = conteudo.replace(
            'plugins: [',
            'plugins: [\n      optimizePersist(),'
        )

    with open(caminho_config, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ vite.config.ts atualizado com o plugin.")

    # 3. Limpar cache
    caminho_cache = os.path.join(pasta_front, "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("🧹 Cache do Vite apagado.")

    print("\n✅ Tudo pronto! Agora rode:")
    print("   cd frontend")
    print("   npm run dev")

if __name__ == "__main__":
    instalar_plugin_e_reconfigurar()