import os
import shutil
import subprocess
import sys

def reset_total():
    raiz = os.getcwd()
    pasta_front = os.path.join(raiz, "frontend")

    print("🛑 Fechando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("🧹 Apagando pastas de build e cache...")
    for pasta in ["node_modules", "dist", ".vite"]:
        caminho = os.path.join(pasta_front, pasta)
        if os.path.exists(caminho):
            try:
                shutil.rmtree(caminho)
                print(f"  - {pasta} apagada.")
            except Exception as e:
                print(f"  - Erro ao apagar {pasta}: {e}")

    print("\n📦 Instalando dependências (isso pode demorar)...")
    
    # Tenta usar o npm, que é mais garantido de achar no Windows
    try:
        subprocess.run(["npm", "install"], cwd=pasta_front, check=True, shell=True)
        print("✅ Dependências instaladas com npm.")
    except Exception:
        print("⚠️ npm falhou, tentando com yarn...")
        try:
            subprocess.run(["yarn", "install"], cwd=pasta_front, check=True, shell=True)
            print("✅ Dependências instaladas com yarn.")
        except Exception as e:
            print(f"❌ Erro ao instalar dependências: {e}")
            return

    print("\n🚀 Iniciando o servidor...")
    try:
        subprocess.run(["npm", "run", "dev"], cwd=pasta_front, shell=True)
    except KeyboardInterrupt:
        print("\nServidor encerrado.")

if __name__ == "__main__":
    reset_total()