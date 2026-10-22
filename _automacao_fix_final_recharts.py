import os
import shutil
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_final_{agora}.zip"
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

def configurar_vite(raiz):
    caminho_vite = os.path.join(raiz, "frontend", "vite.config.ts")
    
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
      // A CORREÇÃO: Força o Vite a converter essa biblioteca problemática
      'use-sync-external-store/shim/with-selector',
      'use-sync-external-store/shim',
    ],
    noDiscovery: true,
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
        f.write(codigo_novo)
    print("⚙️ vite.config.ts atualizado (use-sync-external-store incluído no optimizeDeps).")

def limpar_cache(raiz):
    caminho_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("🧹 Cache do Vite apagado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção Final do Recharts...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    configurar_vite(raiz)
    limpar_cache(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000")

if __name__ == "__main__":
    executar()