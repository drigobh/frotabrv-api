import os
import shutil
import subprocess
import json

def resolver_react():
    raiz = os.getcwd()
    pasta_front = os.path.join(raiz, "frontend")

    print("🛑 Fechando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("🧹 Limpando pastas e cache...")
    for pasta in ["node_modules", "dist"]:
        caminho = os.path.join(pasta_front, pasta)
        if os.path.exists(caminho):
            try:
                shutil.rmtree(caminho)
                print(f"  - {pasta} apagada.")
            except Exception as e:
                print(f"  - Erro ao apagar {pasta}: {e}")

    # 1. Configurar o vite.config.ts
    caminho_config = os.path.join(pasta_front, "vite.config.ts")
    with open(caminho_config, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Remove a configuração antiga do optimizeDeps (se existir)
    import re
    conteudo = re.sub(r"optimizeDeps:\s*\{[^}]*\},?", "", conteudo)
    
    # Adiciona a configuração correta no lugar certo (dentro do return do defineConfig)
    bloco_otimizacao = """
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom', 'recharts'],
    },
    resolve: {
      dedupe: ['react', 'react-dom', 'react-router-dom'],
    },"""

    # Insere antes do "server: {"
    if "server: {" in conteudo:
        conteudo = conteudo.replace("    server: {", bloco_otimizacao + "\n    server: {")
    else:
        # Se não achar o server, insere antes do fechamento do objeto
        conteudo = conteudo.replace("  } satisfies UserConfig;", bloco_otimizacao + "\n  } satisfies UserConfig;")

    with open(caminho_config, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print("⚙️ vite.config.ts reconfigurado para forçar dependências únicas.")

    # 2. Reinstalar dependências
    print("\n📦 Rodando npm install (isso pode demorar)...")
    try:
        subprocess.run(["npm", "install", "--legacy-peer-deps"], cwd=pasta_front, check=True, shell=True)
        print("✅ Dependências instaladas.")
    except Exception as e:
        print(f"❌ Erro ao instalar: {e}")
        return

    print("\n🚀 Tudo pronto! Agora rode:")
    print("   cd frontend")
    print("   npm run dev")

if __name__ == "__main__":
    resolver_react()