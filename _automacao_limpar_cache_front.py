import os
import shutil
import subprocess

def limpar_cache_e_reiniciar():
    raiz = os.getcwd()
    print("🧹 Limpando cache do Vite...")
    
    caminho_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("✅ Cache do Vite apagado.")
    else:
        print("ℹ️ Cache do Vite já estava limpo.")

    print("\n🚀 Reiniciando o Frontend...")
    print("👉 Vá para o terminal, pare o Vite (Ctrl+C) e rode 'yarn dev' novamente.")
    print("👉 Depois, abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/")

if __name__ == "__main__":
    limpar_cache_e_reiniciar()