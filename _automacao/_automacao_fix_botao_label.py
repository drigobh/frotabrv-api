import os
import shutil
import datetime
import zipfile
import re

def criar_backup_full(raiz, pasta_backups):
    agora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_backup = f"backup_FULL_fix_botao_label_{agora}.zip"
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

def corrigir_botoes(raiz):
    caminho = os.path.join(raiz, "frontend", "src", "pages", "Abastecimentos.tsx")
    
    if not os.path.exists(caminho):
        print("❌ Arquivo Abastecimentos.tsx não encontrado.")
        return

    with open(caminho, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Padrão para encontrar o bloco de botões que foi inserido com asChild
    padrao = re.compile(
        r'<div className="flex gap-2">[\s\S]*?</div>',
        re.DOTALL
    )

    novo_bloco = '''<div className="flex gap-2">
            <label className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 cursor-pointer">
              <input type="file" accept=".xls,.xlsx" onChange={handleImportXLS} className="hidden" />
              <Upload className="size-4 mr-2" /> Importar XLS
            </label>
            <label className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 cursor-pointer">
              <input type="file" accept=".pdf" onChange={handleImportPDF} className="hidden" />
              <FileText className="size-4 mr-2" /> Importar NF
            </label>
            <Button onClick={abrirNovo}>
              <Plus className="size-4" /> Novo abastecimento
            </Button>
          </div>'''

    if padrao.search(conteudo):
        conteudo = padrao.sub(novo_bloco, conteudo)
        
        # Remove as referências aos refs que não são mais necessárias
        conteudo = conteudo.replace('  const fileInputRef = useRef<HTMLInputElement>(null);\n', '')
        conteudo = conteudo.replace('  const xlsInputRef = useRef<HTMLInputElement>(null);\n', '')
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("✅ Bloco de botões corrigido com <label> estilizado (sem asChild).")
    else:
        print("⚠️ Bloco de botões não encontrado. O arquivo pode ter sido alterado.")

def executar():
    raiz = os.getcwd()
    print("🤖 Iniciando Automação de Correção dos Botões (Label Estilizado)...")
    
    pasta_backups = os.path.join(raiz, "_automacao", "backups")
    os.makedirs(pasta_backups, exist_ok=True)

    criar_backup_full(raiz, pasta_backups)
    corrigir_botoes(raiz)

    print("\n🚀 Automação concluída! Reinicie o Vite:")
    print("1. Pare o Vite (Ctrl+C) e rode 'npm run dev' novamente.")
    print("2. Abra o navegador em modo anônimo e teste a importação.")

if __name__ == "__main__":
    executar()