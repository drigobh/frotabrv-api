import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_termometro_v2_{agora}.zip"
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

def ajustar_termometro(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Substitui o bloco do ranking com a lógica correta
    bloco_antigo = re.search(r"\{ranking\.map\(\(r, i\) => \{.*?\}\)\}", conteudo, re.DOTALL)
    
    if bloco_antigo:
        novo_bloco = '''{ranking.map((r, i) => {
              // Escala de 0 a 5 km/L (o padrão de mercado é ~3 km/L para pesados)
              // Se a média for 3, a barra enche 60%. Se for 0.17, enche 3.4%.
              const percent = Math.min((r.media / 5) * 100, 100);
              const isGood = r.media >= 2.5;
              
              // Pega apenas a placa (antes do hífen ou do primeiro espaço)
              const placa = r.label.split(" ")[0].replace("-", "");

              return (
                <div key={r.label} className="flex items-center gap-3">
                  <span className="w-6 text-xs text-slate-500 font-mono">{i + 1}º</span>
                  <span className="w-24 text-sm font-medium text-slate-300 font-mono truncate" title={r.label}>{placa}</span>
                  <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${isGood ? 'bg-emerald-500' : 'bg-red-500'}`} 
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                  <span className="w-16 text-right text-sm font-bold text-slate-200">{num(r.media, 2)}</span>
                </div>
              );
            })}'''
        
        conteudo = conteudo.replace(bloco_antigo.group(0), novo_bloco)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("⚙️ Termômetro ajustado: Placa curta e escala fixa de 0 a 5 km/L.")
    else:
        print("⚠️ Bloco do ranking não encontrado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação Final do Termômetro...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    ajustar_termometro(raiz)

    print("\n🚀 Automação concluída! Siga os passos:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo (Ctrl+Shift+N) e acesse http://localhost:3000/abastecimentos")

if __name__ == "__main__":
    executar()