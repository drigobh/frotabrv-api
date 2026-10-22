import os
import shutil
import subprocess
import json
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_createRoot_{agora}.zip"
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

def alinhar_react(raiz):
    pasta_front = os.path.join(raiz, "frontend")
    caminho_pkg = os.path.join(pasta_front, "package.json")
    
    with open(caminho_pkg, 'r', encoding='utf-8') as f:
        pkg = json.load(f)

    # Força a mesma versão do React e React DOM
    versao = "19.0.0"
    if "dependencies" not in pkg:
        pkg["dependencies"] = {}
    pkg["dependencies"]["react"] = versao
    pkg["dependencies"]["react-dom"] = versao

    with open(caminho_pkg, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, indent=2)
    print(f"⚙️ package.json atualizado: React e React DOM na versão {versao}.")

def corrigir_vite(raiz):
    caminho = os.path.join(raiz, "frontend", "vite.config.ts")
    
    codigo_novo = '''import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
    dedupe: ['react', 'react-dom', 'react-router-dom'],
  },
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-dom/client',
      'react-router-dom',
      'recharts',
    ],
    noDiscovery: true,
  },
  server: {
    host: true,
    port: 3000,
    allowedHosts: true,
  },
});
'''
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(codigo_novo)
    print("⚙️ vite.config.ts atualizado (react-dom/client incluído, aliases removidos).")

def reinstalar(raiz):
    pasta_front = os.path.join(raiz, "frontend")
    
    print("🛑 Fechando processos do Node...")
    subprocess.run(["taskkill", "/F", "/IM", "node.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print("🧹 Apagando node_modules e cache...")
    for pasta in ["node_modules", "dist"]:
        caminho = os.path.join(pasta_front, pasta)
        if os.path.exists(caminho):
            shutil.rmtree(caminho)
            print(f"  - {pasta} apagada.")

    print("\n📦 Reinstalando dependências com npm...")
    try:
        subprocess.run(["npm", "install", "--legacy-peer-deps"], cwd=pasta_front, check=True, shell=True)
        print("✅ Dependências instaladas.")
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False
    return True

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção do createRoot...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    alinhar_react(raiz)
    corrigir_vite(raiz)
    
    if reinstalar(raiz):
        print("\n🚀 Automação concluída! Siga os passos:")
        print("1. No terminal, rode: cd frontend")
        print("2. Rode: npm run dev")
        print("3. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()