import os
import shutil
import subprocess
import json
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_reset_def_{agora}.zip"
    caminho_zip = os.path.join(pasta_backups, nome_backup)
    
    print(f"📦 Criando Backup Full do Sistema...")
    ignorar = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']
    
    with zipfile.ZipFile(caminho_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta_alvo in ['app', 'frontend']:
            caminho_pasta = os.path.join(raiz, pasta_alvo)
            for root, dirs, files in os.walk(caminho_pasta):
                dirs[:] = [d for d in dirs if d not in ignorar]
                for file in files:
                    caminho_completo = os.path.join(root, file)
                    caminho_relativo = os.path.relpath(caminho_completo, raiz)
                    try:
                        zipf.write(caminho_completo, caminho_relativo)
                    except Exception:
                        pass
    print(f"✅ Backup Full salvo em: _automacao/backups/{nome_backup}")

def resetar_projeto(raiz):
    pasta_front = os.path.join(raiz, "frontend")
    
    # 1. Fechar Node
    print("🛑 Fechando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Apagar node_modules e dist
    print("🧹 Apagando node_modules e dist...")
    for pasta in ["node_modules", "dist"]:
        caminho = os.path.join(pasta_front, pasta)
        if os.path.exists(caminho):
            try:
                shutil.rmtree(caminho)
            except Exception:
                pass
    print("✅ Pastas apagadas.")

    # 3. Atualizar package.json
    caminho_pkg = os.path.join(pasta_front, "package.json")
    with open(caminho_pkg, 'r', encoding='utf-8') as f:
        pkg = json.load(f)
    
    if "dependencies" not in pkg:
        pkg["dependencies"] = {}
    pkg["dependencies"]["react"] = "19.0.0"
    pkg["dependencies"]["react-dom"] = "19.0.0"
    pkg["dependencies"]["recharts"] = "^2.15.0"  # Versão estável e compatível com React 19
    pkg["dependencies"]["react-router-dom"] = "^7.1.0"
    
    with open(caminho_pkg, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, indent=2)
    print("⚙️ package.json atualizado com versões compatíveis.")

    # 4. Reescrever vite.config.ts limpo
    caminho_vite = os.path.join(pasta_front, "vite.config.ts")
    codigo_vite = '''import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 3000,
    allowedHosts: true,
    proxy: {
      '/api': {
        target: 'https://frotabrv-api.onrender.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
});
'''
    with open(caminho_vite, 'w', encoding='utf-8') as f:
        f.write(codigo_vite)
    print("⚙️ vite.config.ts reescrito (limpo, sem aliases manuais).")

    # 5. Instalar dependências
    print("\n📦 Rodando npm install (isso pode demorar)...")
    try:
        subprocess.run(["npm", "install", "--force"], cwd=pasta_front, check=True, shell=True)
        print("✅ Dependências instaladas.")
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Reset Definitivo...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    resetar_projeto(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. No terminal, rode: cd frontend")
    print("2. Rode: npm run dev")
    print("3. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000")

if __name__ == "__main__":
    executar()