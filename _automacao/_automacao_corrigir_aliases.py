import os
import shutil
import json
import datetime
import zipfile

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_aliases_{agora}.zip"
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

def corrigir_aliases(raiz):
    pasta_front = os.path.join(raiz, "frontend")

    # 1. Corrigir vite.config.ts
    caminho_vite = os.path.join(pasta_front, "vite.config.ts")
    with open(caminho_vite, 'w', encoding='utf-8') as f:
        f.write('''import path from "node:path";
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
    include: ['react', 'react-dom', 'react-router-dom', 'recharts'],
  },
  server: {
    host: true,
    port: 3000,
    allowedHosts: true,
  },
});
''')
    print("⚙️ vite.config.ts reescrito com o alias correto.")

    # 2. Corrigir tsconfig.json (raiz)
    caminho_tsconfig = os.path.join(pasta_front, "tsconfig.json")
    with open(caminho_tsconfig, 'w', encoding='utf-8') as f:
        json.dump({
            "files": [],
            "references": [
                { "path": "./tsconfig.app.json" },
                { "path": "./tsconfig.node.json" }
            ]
        }, f, indent=2)
    print("⚙️ tsconfig.json reescrito.")

    # 3. Corrigir tsconfig.app.json
    caminho_app = os.path.join(pasta_front, "tsconfig.app.json")
    with open(caminho_app, 'w', encoding='utf-8') as f:
        json.dump({
            "compilerOptions": {
                "target": "ES2022",
                "useDefineForClassFields": True,
                "lib": ["ES2022", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "verbatimModuleSyntax": True,
                "moduleDetection": "force",
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": False,
                "noUnusedParameters": False,
                "erasableSyntaxOnly": True,
                "noFallthroughCasesInSwitch": True,
                "noUncheckedSideEffectImports": True,
                "baseUrl": ".",
                "paths": {
                    "@/*": ["./src/*"]
                }
            },
            "include": ["src"]
        }, f, indent=2)
    print("⚙️ tsconfig.app.json reescrito com os paths corretos.")

def limpar_cache(raiz):
    caminho_cache = os.path.join(raiz, "frontend", "node_modules", ".vite")
    if os.path.exists(caminho_cache):
        shutil.rmtree(caminho_cache)
        print("🧹 Cache do Vite apagado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção de Aliases...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_aliases(raiz)
    limpar_cache(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()